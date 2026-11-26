import subprocess
import tempfile
import os
import shutil

'''
注意
sm2使用byte的格式
这里输入的所有的明文都要是byte格式
使用函数时注意转换格式

'''
# OpenSSL 路径配置
OPENSSL_PATH = os.getenv('OPENSSL_PATH') or shutil.which('openssl') or r'E:\OpenSSL-Win64\bin\openssl.exe'
if not OPENSSL_PATH or not os.path.exists(OPENSSL_PATH):
    raise RuntimeError(f'OpenSSL 不可用：{OPENSSL_PATH}；请安装 OpenSSL，并在 bank.env 中设置 OPENSSL_PATH')



def run_openssl_command(args):
    """
    运行OpenSSL命令并返回结果
    """
    result = subprocess.run(
        [OPENSSL_PATH] + args,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        error_msg = f"OpenSSL命令执行失败: {' '.join(args)}\n错误: {result.stderr.strip()}"
        raise Exception(error_msg)
    return result.stdout


def generate_sm2_keypair():
    """
    使用 OpenSSL 生成 SM2 公私钥对

    Returns:
        tuple: (私钥, 公钥) - 均为PEM格式字符串
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')

        # 尝试使用不同命令格式生成密钥，为了兼容性
        for cmd_args in [
            ['genpkey', '-algorithm', 'SM2', '-out', private_key_path],
            ['ecparam', '-name', 'sm2p256v1', '-genkey', '-out', private_key_path],
            ['ec', '-genkey', '-name', 'sm2p256v1', '-out', private_key_path]
        ]:
            try:
                run_openssl_command(cmd_args)
                break
            except:
                continue
        else:
            raise Exception("无法生成SM2密钥对，请确保OpenSSL支持SM2")

        # 通过命令和私钥 导出公钥
        run_openssl_command([
            'pkey', '-in', private_key_path, '-pubout', '-out', public_key_path
        ])

        # 读取密钥
        with open(private_key_path, 'r') as f:
            private_key = f.read()
        with open(public_key_path, 'r') as f:
            public_key = f.read()

    return private_key, public_key


def sm2_encrypt(public_key, plaintext):
    """
    使用SM2公钥加密数据

    Args:
        public_key (str): PEM格式的SM2公钥
        plaintext (bytes): 要加密的明文数据

    Returns:
        bytes: 加密后的数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')

        # 写入文件
        with open(public_key_path, 'w') as f:
            f.write(public_key)
        with open(plaintext_path, 'wb') as f:
            f.write(plaintext)

        # 尝试不同加密参数
        for cmd_args in [
            ['pkeyutl', '-encrypt', '-in', plaintext_path,
             '-out', ciphertext_path, '-inkey', public_key_path, '-pubin',
             '-sm2', '-id', '1234567812345678'],
            ['pkeyutl', '-encrypt', '-in', plaintext_path,
             '-out', ciphertext_path, '-inkey', public_key_path, '-pubin']
        ]:
            try:
                run_openssl_command(cmd_args)
                break
            except:
                continue
        else:
            raise Exception("无法执行SM2加密")

        # 读取加密结果
        with open(ciphertext_path, 'rb') as f:
            ciphertext = f.read()

    return ciphertext


def sm2_decrypt(private_key, ciphertext):
    """
    使用SM2私钥解密数据

    Args:
        private_key (str): PEM格式的SM2私钥
        ciphertext (bytes): 要解密的数据

    Returns:
        bytes: 解密后的明文数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')

        # 写入文件
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(ciphertext_path, 'wb') as f:
            f.write(ciphertext)

        # 尝试不同解密参数
        for cmd_args in [
            ['pkeyutl', '-decrypt', '-in', ciphertext_path,
             '-out', plaintext_path, '-inkey', private_key_path,
             '-sm2', '-id', '1234567812345678'],
            ['pkeyutl', '-decrypt', '-in', ciphertext_path,
             '-out', plaintext_path, '-inkey', private_key_path]
        ]:
            try:
                run_openssl_command(cmd_args)
                break
            except:
                continue
        else:
            raise Exception("无法执行SM2解密")

        # 读取解密结果
        with open(plaintext_path, 'rb') as f:
            plaintext = f.read()

    return plaintext


def sm2_sign(private_key, data):
    """
    使用SM2私钥对数据进行签名

    Args:
        private_key (str): PEM格式的SM2私钥
        data (bytes): 要签名的数据

    Returns:
        bytes: 签名结果
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        private_key_path = os.path.join(tmpdir, 'sm2_private.pem')
        data_path = os.path.join(tmpdir, 'data.txt')
        signature_path = os.path.join(tmpdir, 'signature.bin')

        # 写入文件
        with open(private_key_path, 'w') as f:
            f.write(private_key)
        with open(data_path, 'wb') as f:
            f.write(data)

        # 执行签名
        run_openssl_command([
            'dgst', '-sign', private_key_path,
            '-out', signature_path, '-sm3', data_path
        ])

        # 读取签名
        with open(signature_path, 'rb') as f:
            signature = f.read()

    return signature


def sm2_verify(public_key, data, signature):
    """
    使用SM2公钥验证签名

    Args:
        public_key (str): PEM格式的SM2公钥
        data (bytes): 原始数据
        signature (bytes): 签名数据

    Returns:
        bool: 验证是否通过
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        public_key_path = os.path.join(tmpdir, 'sm2_public.pem')
        data_path = os.path.join(tmpdir, 'data.txt')
        signature_path = os.path.join(tmpdir, 'signature.bin')

        # 写入文件
        with open(public_key_path, 'w') as f:
            f.write(public_key)
        with open(data_path, 'wb') as f:
            f.write(data)
        with open(signature_path, 'wb') as f:
            f.write(signature)

        # 执行验证
        result = subprocess.run([
            OPENSSL_PATH, 'dgst', '-verify', public_key_path,
            '-out', os.devnull, '-sm3', '-signature', signature_path, data_path
        ], capture_output=True)

    return result.returncode == 0


'''
if __name__ == '__main__':
    try:
        if not os.path.exists(OPENSSL_PATH):
            print(f"错误: OpenSSL路径不存在: {OPENSSL_PATH}")
        else:
            # 生成密钥对
            print("生成SM2密钥对...")
            sk, pk = generate_sm2_keypair()
            print("密钥对生成成功")

            # 测试加解密
            test_data = b"Hello, SM2!"
            print(f"\n测试数据: {test_data.decode()}")

            encrypted = sm2_encrypt(pk, test_data)
            print(f"加密结果: {encrypted.hex()[:50]}...")

            decrypted = sm2_decrypt(sk, encrypted)
            print(f"解密结果: {decrypted.decode()}")
            print(f"加解密验证: {'成功' if decrypted == test_data else '失败'}")

            # 测试签名验证
            signature = sm2_sign(sk, test_data)
            print(f"\n签名结果: {signature.hex()[:50]}...")

            verify_result = sm2_verify(pk, test_data, signature)
            print(f"签名验证: {'成功' if verify_result else '失败'}")

    except Exception as e:
        print(f"错误: {e}")
        print(f"请确保OpenSSL路径正确: {OPENSSL_PATH}")
        print("请确保系统已安装支持SM2的OpenSSL版本（1.1.1及以上）")
'''