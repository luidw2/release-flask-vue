import subprocess
import tempfile
import os
import shutil

# OpenSSL 路径配置
OPENSSL_PATH = os.getenv('OPENSSL_PATH') or shutil.which('openssl') or r'E:\OpenSSL-Win64\bin\openssl.exe'


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


def generate_sm4_key():
    """
    生成SM4密钥

    Returns:
        bytes: 16字节的SM4密钥
    """
    # 生成16字节随机密钥
    key = os.urandom(16)
    my_iv = os.urandom(16)
    return key, my_iv


def sm4_encrypt(key, my_iv, plaintext):
    """
    使用SM4加密数据

    Args:
        key (bytes): 16字节的SM4密钥
        plaintext (bytes): 要加密的明文数据

    Returns:
        bytes: 加密后的数据
    """
    #plain_bytes = plaintext.encode()
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入密钥到临时文件
        key_path = os.path.join(tmpdir, 'sm4.key')
        with open(key_path, 'wb') as f:
            f.write(key)

        # 写入明文到临时文件
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')
        with open(plaintext_path, 'wb') as f:
            f.write(plaintext)

        # 加密输出路径
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')

        # 执行加密命令
        run_openssl_command([
            'enc', '-sm4-cbc', '-in', plaintext_path,
            '-out', ciphertext_path, '-pass', f'file:{key_path}',
            '-iv', my_iv.hex()  # 16字节IV
        ])

        # 读取加密结果
        with open(ciphertext_path, 'rb') as f:
            ciphertext = f.read()

    return ciphertext


def sm4_decrypt(key , my_iv , ciphertext):
    """
    使用SM4解密数据

    Args:
        key (bytes): 16字节的SM4密钥
        ciphertext (bytes): 要解密的数据

    Returns:
        bytes: 解密后的明文数据
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # 写入密钥到临时文件
        key_path = os.path.join(tmpdir, 'sm4.key')
        with open(key_path, 'wb') as f:
            f.write(key)

        # 写入密文到临时文件
        ciphertext_path = os.path.join(tmpdir, 'ciphertext.bin')
        with open(ciphertext_path, 'wb') as f:
            f.write(ciphertext)

        # 解密输出路径
        plaintext_path = os.path.join(tmpdir, 'plaintext.txt')

        # 执行解密命令
        run_openssl_command([
            'enc', '-d', '-sm4-cbc', '-in', ciphertext_path,
            '-out', plaintext_path, '-pass', f'file:{key_path}',
            '-iv', my_iv.hex()  # 16字节IV
        ])

        # 读取解密结果
        with open(plaintext_path, 'rb') as f:
            plaintext = f.read()

    return plaintext


# 测试代码
if __name__ == '__main__':
    try:
        if not os.path.exists(OPENSSL_PATH):
            print(f"错误: OpenSSL路径不存在: {OPENSSL_PATH}")
        else:
            # 生成SM4密钥
            print("生成SM4密钥...")
            key, my_iv = generate_sm4_key()
            print(f"密钥: {key.hex()}iv:{my_iv.hex()}")

            # 测试加解密
            test_data = b"Hello, SM4! This is a test message."
            print(f"\n测试数据: {test_data.decode()}")

            # 加密
            encrypted = sm4_encrypt(key, my_iv, test_data)
            print(f"加密结果: {encrypted.hex()}")

            # 解密
            decrypted = sm4_decrypt(key, my_iv, encrypted)
            print(f"解密结果: {decrypted.decode()}")
            print(f"加解密验证: {'成功' if decrypted == test_data else '失败'}")

    except Exception as e:
        print(f"错误: {e}")
        print(f"请确保OpenSSL路径正确: {OPENSSL_PATH}")
        print("请确保系统已安装支持SM4的OpenSSL版本（1.1.1及以上）")
