"""EPB Assistant Flask Application"""
from flask import Flask
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'epb.db')

def create_app():
    app = Flask(__name__, static_folder='../web', static_url_path='')
    app.config['DB_PATH'] = DB_PATH
    
    # 注册蓝图
    from app.routes.api import api_bp
    from app.routes.auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # 静态文件服务
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app
