/**
 * src/utils/sm-tunnel.js —— 前端安全隧道（对应后端 app/utils/tunnel.py）
 * =============================================================================
 * 协议版本 v2（方向密钥版，当前实现仍为 SM4-CBC）：
 *
 *   请求：{ "env":  base64(SM2(后端公钥, keyblob)),
 *           "data": base64(SM4-CBC(c2s_key, c2s_iv, 业务JSON)) }
 *
 *   响应：{ "data": base64(SM4-CBC(s2c_key, s2c_iv, 业务JSON)),
 *           "req":  "请求里的 nonce（回显）" }
 *
 *   keyblob = { c2s_key, c2s_iv, s2c_key, s2c_iv, nonce, ts }
 *
 * 关键变化（v2）：
 *   1) 请求/响应各用一把方向密钥；响应用请求带来的 s2c_key/s2c_iv 加密；
 *   2) 响应不再套 SM2 信封，因此前端**不需要私钥**，只持后端公钥；
 *   3) 响应回显请求 nonce，前端校验 req 是否匹配，防重放/错配；
 *   4) 前端把本次请求的 {s2cKey, s2cIv, nonce} 保存在 Axios config 里，
 *      响应拦截器按 response.config 取，避免并发请求串包。
 *
 * 三条必须和后端对齐的规则（写错了只会解出乱码，很难查）：
 *   1) SM2 用 cipherMode = 0（C1‖C2‖C3），与后端 gmssl 默认顺序一致；
 *   2) sm-crypto 的公钥必须带 04 前缀，但 doEncrypt 的输出不带 04；
 *      后端按“04 开头”识别信封，所以这里手动补上；
 *   3) SM4 用 CBC + PKCS#7，密钥与 IV 都是 16 字节 hex。
 * =============================================================================
 */
import smCrypto from 'sm-crypto'

const { sm2, sm4 } = smCrypto

// Vite 里是 import.meta.env；用 Node 直接跑这个文件做联调测试时它不存在，故兜底
const ENV = import.meta.env || {}

// =============================================================================
// 一、协议常量
// =============================================================================
/**
 * 后端公钥（对应 .env 里的 SM2_FLASK_PUBLIC_KEY）：前端用它封装 keyblob。
 * 公钥不是秘密，直接放在前端没问题；可用 .env.local 的 VITE_ 变量覆盖。
 */
const FLASK_PUBLIC_KEY =
  ENV.VITE_SM2_FLASK_PUBLIC_KEY ||
  '34917afcd83e883bd107a7322079a963b1f3575c2050ca52d53cba7f118200b609ded86e20d0432c7032def98f763b27a6fddae3765989ba3dae4350d24b74a8'

const SM2_CIPHER_MODE = 0 // 0 = C1‖C2‖C3，与后端 gmssl 默认一致
const FIELD_ENV = 'env'
const FIELD_DATA = 'data'

/**
 * sm-crypto 要求的公钥形态：必须带 04 前缀。
 * 注意别和我们自己补在密文上的那个 04 搞混 —— 那个 04 是后端识别信封的约定。
 */
const FLASK_PUBLIC_KEY_04 = FLASK_PUBLIC_KEY.startsWith('04')
  ? FLASK_PUBLIC_KEY
  : '04' + FLASK_PUBLIC_KEY

/**
 * 需要走隧道的接口（和后端接口上的 @tunnel_required 一一对应）。
 * 后端给别的接口也加上装饰器时，这里同步加一条即可。
 */
export const TUNNEL_URLS = ['/user/login']

// =============================================================================
// 二、编码小工具（hex / bytes / base64 互转）
// =============================================================================
const hexToBytes = (hex) => {
  const out = new Uint8Array(hex.length / 2)
  for (let i = 0; i < out.length; i++) out[i] = parseInt(hex.substr(i * 2, 2), 16)
  return out
}

const bytesToHex = (bytes) => {
  let s = ''
  for (let i = 0; i < bytes.length; i++) s += bytes[i].toString(16).padStart(2, '0')
  return s
}

const bytesToBase64 = (bytes) => {
  let s = ''
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i])
  return btoa(s)
}

const base64ToBytes = (b64) => {
  const s = atob(b64)
  const out = new Uint8Array(s.length)
  for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i)
  return out
}

/** 生成 n 字节的随机十六进制串（方向密钥 / IV / nonce 都用它） */
const randomHex = (n) => bytesToHex(crypto.getRandomValues(new Uint8Array(n)))

// =============================================================================
// 三、对外函数
// =============================================================================
/**
 * 把业务数据封成隧道请求体。
 * 对应后端 tunnel.py 的 seal_request()。
 *
 * @param {object} payload 业务请求体，例如 { username, password, role }
 * @returns {{body: string, meta: {s2cKey: string, s2cIv: string, nonce: string}}}
 *          body 是整个请求体字符串；meta 必须挂到 Axios config 上供响应解密
 */
export function sealRequest(payload) {
  // 1) 生成一次性方向密钥 / IV / nonce / 时间戳
  const keyblob = {
    c2s_key: randomHex(16), // 请求方向 SM4 密钥
    c2s_iv: randomHex(16),  // 请求方向 IV
    s2c_key: randomHex(16), // 响应方向 SM4 密钥
    s2c_iv: randomHex(16),  // 响应方向 IV
    nonce: randomHex(16),   // 一次性票号（防重放）
    ts: Date.now()          // 毫秒时间戳，后端校验 ±5 分钟
  }

  // 2) SM2 封装整个 keyblob（两把方向密钥都在信封里）
  const envelopeHex =
    '04' + sm2.doEncrypt(JSON.stringify(keyblob), FLASK_PUBLIC_KEY_04, SM2_CIPHER_MODE)

  // 3) 用请求方向密钥加密业务 JSON（sm-crypto 返回 hex）
  const dataHex = sm4.encrypt(JSON.stringify(payload), keyblob.c2s_key, {
    mode: 'cbc',
    iv: keyblob.c2s_iv
  })

  // 4) 信封与密文都转成 base64（与后端编码一致）
  const body = JSON.stringify({
    [FIELD_ENV]: bytesToBase64(hexToBytes(envelopeHex)),
    [FIELD_DATA]: bytesToBase64(hexToBytes(dataHex))
  })

  return {
    body,
    meta: {
      s2cKey: keyblob.s2c_key,
      s2cIv: keyblob.s2c_iv,
      nonce: keyblob.nonce
    }
  }
}

/**
 * 拆开隧道响应。
 * 对应后端 tunnel.py 的 open_response_with_key()。
 *
 * - 响应带 {data, req} → 用本次请求的 s2cKey/s2cIv 解密；
 * - 没有 {data, req} → 明文响应（例如隧道错误码），原样返回。
 *
 * @param {object|string} data 响应体（axios 已解析成对象，或原始字符串）
 * @param {{s2cKey: string, s2cIv: string, nonce: string}} meta 本次请求的会话材料
 * @returns {object} 业务数据 / 明文错误对象
 */
export function openResponse(data, meta) {
  let pack = data
  if (typeof pack === 'string') {
    try {
      pack = JSON.parse(pack)
    } catch (e) {
      return data
    }
  }

  // 隧道错误或普通接口：没有 data + req，原样返回
  if (!pack || typeof pack !== 'object' ||
      typeof pack[FIELD_DATA] !== 'string' || typeof pack.req !== 'string') {
    return pack
  }

  if (!meta || !meta.s2cKey || !meta.s2cIv || !meta.nonce) {
    throw new Error('缺少响应解密所需的会话材料（s2cKey/s2cIv/nonce）')
  }

  // 响应必须绑定到本次请求，防重放/错配
  if (pack.req !== meta.nonce) {
    throw new Error('响应 nonce 与请求不匹配（可能被重放或错配）')
  }

  const dataHex = bytesToHex(base64ToBytes(pack[FIELD_DATA]))
  const plain = sm4.decrypt(dataHex, meta.s2cKey, {
    mode: 'cbc',
    iv: meta.s2cIv
  })
  return JSON.parse(plain)
}

/** 判断这个请求地址是否需要走隧道（供 request.js 的拦截器使用） */
export function isTunnelUrl(url = '') {
  // 去掉查询串再比对，避免 '/user/login?x=1' 匹配不上
  const path = url.split('?')[0]
  return TUNNEL_URLS.includes(path)
}
