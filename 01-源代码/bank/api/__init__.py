import os

from flask_cors import CORS
from api.v1 import (pay,pay_process)
from config.config import config_dic
from flask import Flask, request, redirect
from utils import db


def create_app(config_name):
    # 创建Flask实例
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # 项目根目录（FlaskProject/）
    project_root = os.path.dirname(current_dir)
    # 模板目录（FlaskProject/templates/）
    template_dir = os.path.join(project_root, 'templates')
    # 静态文件目录（FlaskProject/static/）
    static_dir = os.path.join(project_root, 'static')

    # 创建Flask实例，使用绝对路径
    app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)

    app.config.from_object(config_dic[config_name])#加载模式配置

    _configure_cors(app, config_name)

    db.init_db()

    @app.route('/')
    def index():
        return "Hello, World!"

    api_prefix = ''
    app.register_blueprint(pay.user, url_prefix=api_prefix)
    app.register_blueprint(pay_process.user, url_prefix=api_prefix)
    return app

#工厂函数
def _configure_cors(app, config_name):
    """配置 CORS 跨域设置"""
    # 获取 CORS 配置
    cors_origins = app.config.get('CORS_ORIGINS', [])

    if config_name == 'development':
        # 开发环境：允许所有跨域请求
        CORS(app,
             origins='*',
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization','X-Custom-Header'],
             methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        print(f"CORS 配置: 开发环境 - 允许所有域名跨域访问")
    else:
        # 生产环境：只允许指定域名
        CORS(app,
             origins=cors_origins,
             supports_credentials=True,
             allow_headers=['Content-Type', 'Authorization','X-Custom-Header'],
             methods=['GET', 'POST', 'PUT', 'DELETE'])
        print(f"CORS 配置: 生产环境 - 允许的域名: {cors_origins}")