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
    from app.routes.case_workflow import case_bp
    from app.routes.diagnostic import diag_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(case_bp, url_prefix='/api/case')
    app.register_blueprint(diag_bp, url_prefix='/api/diag')
    
    # 安全中间件
    from app.security import init_security
    init_security(app)
    
    # 静态文件服务
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    return app
