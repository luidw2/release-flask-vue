"""
email_iii.py —— 邮箱格式校验模块

历史背景：
    早期注册流程使用“邮箱 + 6 位验证码”，相关代码（generate_verification_code /
    send_verification_email / verify_email / EMAIL_CODE_STORE）属于已废弃流程，
    且 verify_email 中曾存在写死的万能验证码（VULN-03，CWE-912/798）。
    当前注册已改为“国密证书签发 + 直接建号”，不再使用邮箱验证码，因此：
      - 删除全部验证码生成 / 存储 / 校验逻辑；
      - 只保留注册仍在使用的 validate_email_enhanced() 邮箱格式校验。

注意：不要再把验证码逻辑加回本模块；如未来需要邮箱验证，应使用随机数安全源
（secrets）、哈希存储、限时一次性校验，并单独评审。
"""
import re


# 增强版邮箱格式校验：
# 作用：按常见邮箱规则做格式合法性检查（基本正则、总长度、本地部分、域名部分）。
# 参数：email —— 待校验的邮箱地址
# 返回：格式合法返回 True；不合法打印原因并返回 False
def validate_email_enhanced(email: str) -> bool:
    """
    邮箱格式验证
    Args:
        email: 要验证的邮箱地址

    Returns:
        bool: 邮箱格式是否正确
    """
    if not email or not isinstance(email, str):
        print("邮箱不能为空")
        return False

    email = email.strip()

    # 基本格式检查
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        print("邮箱格式不正确")
        return False

    # 长度检查
    if len(email) > 254:
        print("邮箱地址过长")
        return False

    # 分割本地部分和域名
    parts = email.split('@')
    local_part = parts[0]
    domain = parts[1]

    # 本地部分检查
    if len(local_part) > 64:
        print("邮箱用户名部分过长")
        return False

    if local_part.startswith('.') or local_part.endswith('.'):
        print("邮箱用户名不能以点开头或结尾")
        return False

    if '..' in local_part:
        print("邮箱用户名不能包含连续的点")
        return False

    # 域名检查
    if domain.startswith('-') or domain.endswith('-'):
        print("域名不能以连字符开头或结尾")
        return False

    if '..' in domain:
        print("域名不能包含连续的点")
        return False

    # 如果通过所有检查，返回True
    return True
