# -*- coding: utf-8 -*-
"""
app/utils/tunnel.py —— 安全隧道（课堂 Demo）
=============================================================================
线上报文：

    请求: {"env":  "base64( SM2加密(后端公钥, keyblob) )",
           "data": "base64( SM4-CBC(c2s_key, c2s_iv, 明文JSON) )"}
    响应: {"data": "base64( SM4-CBC(s2c_key, s2c_iv, 明文JSON) )",
           "req":  "请求里的 nonce（回显，供前端绑定请求/响应）"}

    keyblob = {"c2s_key","c2s_iv","s2c_key","s2c_iv","nonce","ts"}
    —— 请求/响应各用一把方向密钥；响应不再套 SM2 信封，前端不需要私钥。

服务端拆包就四步：拆 JSON → 拆信封(SM2) → 校验时间戳 + nonce → 解密 data(SM4)

为什么 nonce / ts 要放在信封里面：它们是防重放用的（同一个包重发要能拒掉）。
放在明文位置，攻击者重放时改成新的就绕过去了；放进信封里改不动。
响应只回显请求的 nonce，不重复放 ts；前端校验 req 是否等于本次请求的 nonce。

自测：在本目录（后端flask）执行  .venv\\Scripts\\python.exe -m app.utils.tunnel
=============================================================================
"""

import base64
import json
import os
import threading
import time

from dotenv import load_dotenv

from . import SM2, SM4

load_dotenv()

# =============================================================================
# 密钥（来自 .env）：Vue 侧一对、Flask 侧一对
# =============================================================================
FLASK_PUBLIC_KEY = os.getenv('SM2_FLASK_PUBLIC_KEY')      # 前端给后端发请求时，用后端公钥封信封
FLASK_PRIVATE_KEY = os.getenv('SM2_FLASK_PRIVATE_KEY')    # 后端拆请求信封时用
# 说明：响应方向不再使用 SM2 信封，因此不再需要 SM2_VUE_PUBLIC_KEY / SM2_VUE_PRIVATE_KEY。

# =============================================================================
# 协议常量与参数
# =============================================================================
FIELD_ENV = 'env'        # 报文里放 SM2 信封的字段
FIELD_DATA = 'data'      # 报文里放 SM4 密文的字段

TS_WINDOW_MS = int(os.getenv('TUNNEL_TS_WINDOW_MS', '300000'))   # 时间窗 ±5 分钟
NONCE_TTL_S = int(os.getenv('TUNNEL_NONCE_TTL_S', '600'))        # nonce 记住 10 分钟

# 错误码 -> HTTP 状态码（装饰器直接拿来构造响应）
ERR_PACK = 'TUNNEL_BAD_PACKET'
ERR_UNWRAP = 'TUNNEL_UNWRAP_FAILED'
ERR_TS = 'TUNNEL_TS_EXPIRED'
ERR_REPLAY = 'TUNNEL_REPLAY'
ERR_BODY = 'TUNNEL_BODY_DECRYPT_FAILED'
HTTP_STATUS = {ERR_PACK: 400, ERR_UNWRAP: 400, ERR_TS: 401, ERR_REPLAY: 409, ERR_BODY: 400}


class TunnelError(Exception):
    """隧道校验失败。装饰器里这样用：

        except tunnel.TunnelError as e:
            return jsonify(e.to_dict()), e.http_status
    """

    def __init__(self, code, message=''):
        self.code = code
        self.http_status = HTTP_STATUS.get(code, 400)
        self.message = message or code
        super().__init__(f'[{code}] {self.message}')

    def to_dict(self):
        return {'code': self.code, 'message': self.message}


# =============================================================================
# 一、SM4 加密 body（要求 1）
# =============================================================================
def seal_body(body: bytes, key: bytes, iv: bytes) -> bytes:
    """SM4 加密 body，返回密文的 base64（线上形态）。

    实测与 OpenSSL / 前端 sm-crypto 结果逐字节相同：
        key = iv = 000102030405060708090a0b0c0d0e0f，明文 "AAAAAAA"
        -> 38601c5b95f1c60be75f7e103a0e0a74
    """
    return base64.b64encode(SM4.sm4_encrypt_raw(key, iv, body))


def open_body(body_b64, key: bytes, iv: bytes) -> bytes:
    """把 base64 的密文还原成明文；没有 body 就当空明文（GET 类接口）。

    解不开时统一报 TUNNEL_BODY_DECRYPT_FAILED，不把底层异常细节暴露出去。
    """
    if isinstance(body_b64, str):
        body_b64 = body_b64.encode('ascii', errors='ignore')
    if not body_b64:
        return b''
    try:
        return SM4.sm4_decrypt_raw(key, iv, base64.b64decode(body_b64))
    except Exception:
        raise TunnelError(ERR_BODY, 'SM4 解密失败（密钥不匹配或密文损坏）')


# =============================================================================
# 二、Nonce 与时间窗（要求 3）
# =============================================================================
def check_ts(ts_ms, now_ms=None, window_ms=None):
    """时间窗校验：|现在 - ts| 不超过允许窗口才算新鲜。

    返回实际偏移量（毫秒），便于排查前后端时钟不同步。
    """
    window_ms = TS_WINDOW_MS if window_ms is None else int(window_ms)
    now_ms = int(time.time() * 1000) if now_ms is None else int(now_ms)
    drift_ms = now_ms - int(ts_ms)
    if abs(drift_ms) > window_ms:
        raise TunnelError(ERR_TS, f'时间戳超出窗口 ±{window_ms}ms（drift={drift_ms}ms）')
    return drift_ms


# nonce 表：nonce -> 过期时刻（进程内存，单机 Demo 够用；多进程部署要换 Redis）
_used_nonces = {}
_nonce_lock = threading.Lock()


def check_nonce(nonce: str, now: float = None) -> bool:
    """nonce 一次性校验：第一次用返回 True，重复出现返回 False（说明是重放）。

    简单起见，校验通过就顺手登记（同一个包再发一次必然被打回）。
    """
    now = time.time() if now is None else now
    with _nonce_lock:
        # 先清掉过期的，避免字典无限增长
        for n in [n for n, exp in _used_nonces.items() if exp <= now]:
            del _used_nonces[n]
        if nonce in _used_nonces:
            return False
        _used_nonces[nonce] = now + NONCE_TTL_S
        return True


# =============================================================================
# 三、报文打包 / 拆包
# =============================================================================
def pack(envelope: bytes, data_b64: bytes) -> bytes:
    """把信封和密文打包成整个 body：{"env": "...", "data": "..."}。"""
    return json.dumps({
        FIELD_ENV: base64.b64encode(envelope).decode('ascii'),
        FIELD_DATA: data_b64.decode('ascii'),
    }).encode('utf-8')


def unpack(body) -> tuple:
    """从 body 里取出 (信封 bytes, 密文 base64 bytes)。

    任何格式问题（不是 JSON、缺字段、base64 非法）都报 TUNNEL_BAD_PACKET。
    """
    if isinstance(body, (bytes, bytearray)):
        try:
            body = bytes(body).decode('utf-8')
        except UnicodeDecodeError:
            raise TunnelError(ERR_PACK, '请求体不是 UTF-8 文本')
    try:
        obj = json.loads(body)
        envelope = base64.b64decode(obj[FIELD_ENV])
        data_b64 = obj[FIELD_DATA].encode('ascii')
    except Exception:
        raise TunnelError(ERR_PACK,
                          f'不是合法的隧道包（需要 {FIELD_ENV} 和 {FIELD_DATA} 两个字段）')
    return envelope, data_b64


# =============================================================================
# 四、封包 / 拆包（总入口）
# =============================================================================
def _new_keyblob(now_ms=None) -> dict:
    """生成一次性会话材料：请求/响应各一把 SM4 密钥与 IV（CBC 16B）。"""
    return {
        'c2s_key': os.urandom(16).hex(),   # 请求方向 SM4 密钥
        'c2s_iv': os.urandom(16).hex(),    # 请求方向 IV
        's2c_key': os.urandom(16).hex(),   # 响应方向 SM4 密钥
        's2c_iv': os.urandom(16).hex(),    # 响应方向 IV
        'nonce': os.urandom(16).hex(),     # 一次性票号（防重放）
        'ts': int(time.time() * 1000) if now_ms is None else int(now_ms),
    }


def _keyblob_fields(blob: dict):
    """校验 keyblob 并返回 (c2s_key, c2s_iv, s2c_key, s2c_iv, nonce, ts)。"""
    try:
        c2s_key = bytes.fromhex(blob['c2s_key'])
        c2s_iv = bytes.fromhex(blob['c2s_iv'])
        s2c_key = bytes.fromhex(blob['s2c_key'])
        s2c_iv = bytes.fromhex(blob['s2c_iv'])
        nonce = blob['nonce']
        ts = blob['ts']
    except Exception:
        raise TunnelError(ERR_UNWRAP, 'keyblob 字段缺失或格式错误')

    for name, value in (('c2s_key', c2s_key), ('c2s_iv', c2s_iv),
                        ('s2c_key', s2c_key), ('s2c_iv', s2c_iv)):
        if len(value) != 16:
            raise TunnelError(ERR_UNWRAP, f'{name} 长度必须为 16 字节')
    return c2s_key, c2s_iv, s2c_key, s2c_iv, nonce, ts


def _seal_request(plaintext: bytes, public_key_hex: str, now_ms=None) -> bytes:
    """请求封包：生成 keyblob → SM2 信封 → 用 c2s_key/c2s_iv 加密 Body。"""
    blob = _new_keyblob(now_ms)
    c2s_key, c2s_iv, _, _, _, _ = _keyblob_fields(blob)
    envelope = SM2.gmssl_sm2_encrypt_raw(public_key_hex, json.dumps(blob).encode('utf-8'))
    return pack(envelope, seal_body(plaintext, c2s_key, c2s_iv))


def seal_request(plaintext: bytes, now_ms=None, public_key_hex=None) -> bytes:
    """客户端 -> 服务端：用后端公钥封装 keyblob，返回整个请求体。"""
    return _seal_request(plaintext, public_key_hex or FLASK_PUBLIC_KEY, now_ms)


def open_request_ex(body, private_key_hex=None, now_ms=None):
    """服务端拆请求：返回 (明文 bytes, keyblob)。

    装饰器必须保存 keyblob，响应方向要用里面的 s2c_key / s2c_iv。
    """
    envelope, data_b64 = unpack(body)

    try:
        blob = json.loads(
            SM2.gmssl_sm2_decrypt_raw(private_key_hex or FLASK_PRIVATE_KEY, envelope).decode('utf-8')
        )
    except Exception:
        raise TunnelError(ERR_UNWRAP, 'SM2 拆封失败（私钥不匹配或信封损坏）')

    c2s_key, c2s_iv, _, _, nonce, ts = _keyblob_fields(blob)
    check_ts(ts, now_ms)
    if not check_nonce(nonce):
        raise TunnelError(ERR_REPLAY, 'nonce 重复（重放请求）')
    return open_body(data_b64, c2s_key, c2s_iv), blob


def seal_response_with_key(payload: bytes, keyblob: dict, now_ms=None) -> bytes:
    """服务端 -> 客户端：用 keyblob 里的 s2c_key/s2c_iv 加密响应，并回显请求 nonce。

    响应不再套 SM2 信封，因此前端不需要私钥，也不存在“所有用户共用一把前端私钥”的问题。
    """
    _, _, s2c_key, s2c_iv, nonce, _ = _keyblob_fields(keyblob)
    return json.dumps({
        'data': seal_body(payload, s2c_key, s2c_iv).decode('ascii'),
        'req': nonce,
    }).encode('utf-8')


def open_response_with_key(body, keyblob: dict, now_ms=None) -> bytes:
    """客户端/自测拆响应：校验 req 回显，再用 s2c_key/s2c_iv 解密。"""
    try:
        obj = json.loads(body.decode('utf-8') if isinstance(body, (bytes, bytearray)) else body)
        data_b64 = obj['data']
        req = obj['req']
    except Exception:
        raise TunnelError(ERR_PACK, '不是合法的隧道响应（需要 data 和 req 字段）')

    _, _, s2c_key, s2c_iv, nonce, _ = _keyblob_fields(keyblob)
    if req != nonce:
        raise TunnelError(ERR_REPLAY, '响应 req 与请求 nonce 不一致（重放/错配）')
    return open_body(data_b64, s2c_key, s2c_iv)


def _self_test():
    print('=' * 66)
    print('tunnel.py 自测（方向密钥版：请求/响应各一把 SM4 密钥）')
    print('=' * 66)
    print(f'时间窗 {TS_WINDOW_MS}ms | nonce 记忆 {NONCE_TTL_S}s')

    # 1) SM4 固定向量
    key, iv, plain = bytes(range(16)), bytes(range(16)), b'AAAAAAA'
    ct = SM4.sm4_encrypt_raw(key, iv, plain)
    expect = '38601c5b95f1c60be75f7e103a0e0a74'
    assert ct.hex() == expect, f'SM4 向量不符：{ct.hex()}'
    assert SM4.sm4_decrypt_raw(key, iv, ct) == plain
    print(f'[1] SM4 加解密      : {ct.hex()}（可复现，与 OpenSSL/sm-crypto 一致）')

    # 2) SM2 信封
    msg = b'{"hello":"tunnel"}'
    env = SM2.gmssl_sm2_encrypt_raw(FLASK_PUBLIC_KEY, msg)
    assert len(env) == 97 + len(msg), f'信封长度 {len(env)}'
    assert SM2.gmssl_sm2_decrypt_raw(FLASK_PRIVATE_KEY, env) == msg
    print(f'[2] SM2 封装/拆封   : 明文 {len(msg)}B -> 信封 {len(env)}B（=97+明文）')

    # 3) 完整请求往返 + 方向密钥
    now = int(time.time() * 1000)
    data = {'username': 'zhangsan', 'password': '123456', 'role': 'user'}
    payload = json.dumps(data, ensure_ascii=False).encode('utf-8')
    wire = seal_request(payload, now_ms=now)
    plaintext, blob = open_request_ex(wire, now_ms=now)
    assert json.loads(plaintext.decode('utf-8')) == data
    assert blob['c2s_key'] != blob['s2c_key'], '请求/响应应使用独立密钥'
    print(f'[3] 请求封包/拆封   : 整个 body {len(wire)}B；c2s/s2c 方向密钥独立')

    # 4) 重放
    wire2 = seal_request(payload, now_ms=now)
    open_request_ex(wire2, now_ms=now)
    try:
        open_request_ex(wire2, now_ms=now)
        raise AssertionError('重放竟然通过了')
    except TunnelError as e:
        assert e.code == ERR_REPLAY, e.code
        print(f'[4] nonce 重放      : 第二次 -> {e.code}（HTTP {e.http_status}）')

    # 5) 时间窗（每个 drift 用新包，避免 nonce 被上一次消耗）
    for drift, should_pass in ((299000, True), (-299000, True),
                               (301000, False), (-301000, False)):
        w = seal_request(payload, now_ms=now)
        try:
            open_request_ex(w, now_ms=now + drift)
            ok = True
        except TunnelError as e:
            ok = (e.code != ERR_TS)
        assert ok == should_pass, f'drift={drift}ms 期望 {should_pass}，实际 {ok}'
        print(f'[5] 时间窗 {drift:+8d}ms : {"通过" if ok else "被拒"}')

    # 6) 非法报文
    try:
        open_request_ex(json.dumps({'username': 'x', 'password': 'y'}).encode())
        raise AssertionError('非法包竟然通过了')
    except TunnelError as e:
        assert e.code == ERR_PACK, e.code
        print(f'[6] 非法报文        : -> {e.code}（HTTP {e.http_status}）')

    # 7) 响应方向：复用请求带来的 s2c 密钥，不再套 SM2
    resp = seal_response_with_key(b'{"code":0,"msg":"ok"}', blob)
    assert open_response_with_key(resp, blob) == b'{"code":0,"msg":"ok"}'
    print('[7] 响应封包/拆封   : 正常（s2c_key/s2c_iv，响应无 SM2 信封）')

    # 8) 响应 req 不匹配（重放/错配）必须拒绝
    bad = json.loads(resp.decode('utf-8'))
    bad['req'] = '00' * 16
    try:
        open_response_with_key(json.dumps(bad).encode('utf-8'), blob)
        raise AssertionError('响应 nonce 不匹配竟然通过了')
    except TunnelError as e:
        assert e.code == ERR_REPLAY, e.code
        print(f'[8] 响应 req 校验   : 不匹配 -> {e.code}')

    print()
    print('全部通过。请求：SM2 信封 + c2s 密钥；响应：s2c 密钥 + req 回显；前端无需私钥。')


if __name__ == '__main__':
    _self_test()
