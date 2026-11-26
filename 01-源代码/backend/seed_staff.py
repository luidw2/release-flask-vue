# ============================================================================
# seed_staff.py —— 后台演示账号初始化脚本（管理员/审计员）
# 运行方式（在后端flask目录下）：
#   .venv\Scripts\python.exe seed_staff.py
# 作用：1) 调用 db.init_db() 创建缺失的表（含 staff 表，只建新表不影响老表）；
#       2) 创建/重置后台演示账号 admin1(管理员) / audit1(审计员)：
#          - 密码固定为脚本内值，保证发布包/老师环境可登录；
#          - 同时清空 TOTP 绑定状态，首次登录会重新走绑定流程。
# 说明：脚本可重复执行；已存在的 admin1/audit1 会被重置密码与 TOTP 状态。
#       只影响这两个演示账号，不碰其他 staff 账号。
# ============================================================================
from app.utils import db, my_bcrypt
from app.utils.db import Session, Staff


def upsert_staff(username, password, role):
    """创建演示账号；已存在则重置密码、角色、锁定与 TOTP 状态。"""
    with Session() as session:
        staff = session.query(Staff).filter(Staff.username == username).first()
        if staff:
            staff.password = my_bcrypt.bcrypt_password(password)
            staff.role = role
            staff.is_active = True
            staff.failed_attempts = 0
            staff.lock_until = None
            staff.totp_secret_enc = None
            staff.totp_enabled = False
            staff.recovery_hashes = None
            staff.last_totp_step = None
            session.commit()
            print(f'后台账号 {username} 已重置，角色: {role}')
            return staff
    return db.create_staff(username, password, role=role)


def main():
    db.init_db()
    a = upsert_staff('admin1', 'Admin@123456', role='admin')
    b = upsert_staff('audit1', 'Audit@123456', role='auditor')
    print('admin1(管理员):', '成功' if a else '失败')
    print('audit1(审计员):', '成功' if b else '失败')


if __name__ == '__main__':
    main()
