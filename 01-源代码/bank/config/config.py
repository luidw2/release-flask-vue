import os
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量
class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'

    # MySQL 配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'user_management'

    DEBUG = False
    # CORS 配置
    CORS_ORIGINS = []  # 生产环境允许的域名列表



class DevelopmentConfig(Config):
    DEBUG = True
    # 开发环境允许所有跨域请求
    CORS_ORIGINS = ['*']  # 允许所有域名


class ProductionConfig(Config):
    DEBUG = False
    # 生产环境只允许特定域名
    CORS_ORIGINS = [
        'https://yourdomain.com',
        'https://www.yourdomain.com'
    ]


# 配置字典
config_dic = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
