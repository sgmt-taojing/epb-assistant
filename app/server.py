"""Flask服务器入口 — 替代 file_server.py"""
from app import create_app
from app.models import init_db
import os

# 自动初始化数据库
if not os.path.exists('epb.db'):
    init_db()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8900, debug=True)
