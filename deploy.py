#!/usr/bin/env python3
"""环保智慧执法平台 · 一键部署脚本
用法: python3 deploy.py [local|docker|github|all]
"""
import subprocess, sys, os, time, urllib.request, json

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(PROJECT_DIR)
PORT = int(os.environ.get('PORT', '8900'))

def run(cmd, check=True):
    print(f'  $ {cmd}')
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 and check:
        print(f'  ERROR: {r.stderr[:200]}')
    return r

def health_check():
    try:
        with urllib.request.urlopen(f'http://127.0.0.1:{PORT}/api/health', timeout=5) as resp:
            data = json.loads(resp.read())
            return data.get('status') == 'healthy'
    except:
        return False

def check_files():
    print('📋 检查文件...')
    for f in ['scripts/file_server.py', 'web/index.html']:
        if not os.path.isfile(f):
            print(f'❌ 缺少: {f}'); sys.exit(1)
    pages = len([f for f in os.listdir('web') if f.endswith('.html')])
    print(f'  ✅ 文件检查通过 ({pages} 个HTML页面)')

def deploy_local():
    print('📦 本地部署...')
    # 停旧进程
    r = run(f'lsof -nP -iTCP:{PORT} -t 2>/dev/null', check=False)
    if r.stdout.strip():
        print(f'  停止旧进程 PID: {r.stdout.strip()}')
        run(f'kill {r.stdout.strip()} 2>/dev/null', check=False)
        time.sleep(2)
    # 启动
    print(f'  启动服务 (端口: {PORT})...')
    subprocess.Popen(['python3', 'scripts/file_server.py'], stdout=open('/tmp/epb-assistant.log','w'), stderr=subprocess.STDOUT)
    time.sleep(3)
    if health_check():
        print('  ✅ 服务启动成功')
        print('=' * 44)
        print(f'🌿 部署完成！')
        print(f'  访问: http://127.0.0.1:{PORT}')
        print(f'  移动端: http://127.0.0.1:{PORT}/m-portal.html')
        print(f'  总览: http://127.0.0.1:{PORT}/overview.html')
        print(f'  日志: /tmp/epb-assistant.log')
        print('=' * 44)
    else:
        print('  ❌ 启动失败，查看日志: /tmp/epb-assistant.log'); sys.exit(1)

def deploy_docker():
    print('🐳 Docker部署...')
    r = run('docker --version', check=False)
    if r.returncode != 0:
        print('❌ Docker未安装'); sys.exit(1)
    run('docker stop epb-assistant 2>/dev/null || true', check=False)
    run('docker rm epb-assistant 2>/dev/null || true', check=False)
    print('  构建镜像...')
    run('docker build -t epb-assistant .')
    print('  启动容器...')
    run(f'docker run -d --name epb-assistant -p {PORT}:8900 -v {PROJECT_DIR}/db:/app/db --restart unless-stopped epb-assistant')
    time.sleep(3)
    if health_check():
        print(f'  ✅ Docker启动成功 → http://127.0.0.1:{PORT}')
    else:
        print('  ❌ 启动失败: docker logs epb-assistant'); sys.exit(1)

def deploy_github():
    print('📤 推送GitHub...')
    run('git add -A')
    r = run(f'git commit -m "deploy: {time.strftime("%Y-%m-%d %H:%M")} 自动部署"', check=False)
    run('git push origin main')
    print('  同步gh-pages...')
    run('git checkout gh-pages', check=False)
    run('git checkout main -- web/ scripts/ db/ api-data/', check=False)
    run('cp web/*.html web/*.js . 2>/dev/null', check=False)
    run('git add -A')
    run(f'git commit -m "deploy: {time.strftime("%Y-%m-%d %H:%M")} 同步gh-pages"', check=False)
    run('git push origin gh-pages')
    run('git checkout main', check=False)
    print('=' * 44)
    print('🌿 GitHub部署完成！')
    print('  Pages: https://sgmt-taojing.github.io/epb-assistant/')
    print('  仓库: https://github.com/sgmt-taojing/epb-assistant')
    print('=' * 44)

def run_selfcheck():
    print('🔍 自检...')
    pages = len([f for f in os.listdir('web') if f.endswith('.html')])
    print(f'  HTML页面: {pages}')
    print(f'  API健康: {"✅" if health_check() else "❌"}')
    alerts = len([f for f in os.listdir('web') if f.endswith('.html') and 'alert(' in open(f'web/{f}').read() and 'epbToast' not in f'web/{f}'])
    print(f'  alert残留: {alerts}')
    print('  ✅ 自检完成')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'local'
    print(f'🌿 环保智慧执法平台 — 部署模式: {mode}')
    print('=' * 44)
    check_files()
    
    if mode in ('local', 'l'):
        deploy_local(); run_selfcheck()
    elif mode in ('docker', 'd'):
        deploy_docker(); run_selfcheck()
    elif mode in ('github', 'g'):
        deploy_github()
    elif mode in ('all', 'a'):
        deploy_local(); deploy_github()
    else:
        print('用法: python3 deploy.py [local|docker|github|all]')
        print('  local  - 本地Python运行(默认)')
        print('  docker - Docker容器')
        print('  github - 推送GitHub Pages')
        print('  all    - 本地+GitHub')
