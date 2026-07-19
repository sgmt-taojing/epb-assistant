"""EPB Assistant API 自动化测试"""
import pytest
import json
import sys
import os

# 确保app可导入
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestHealth:
    def test_health(self, client):
        r = client.get('/api/health')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] == True
        assert data['status'] == 'healthy'

class TestCases:
    def test_cases_list(self, client):
        r = client.get('/api/cases')
        assert r.status_code == 200
        data = r.get_json()
        assert 'cases' in data
        assert 'total' in data
        assert data['total'] > 0
    
    def test_case_structure(self, client):
        r = client.get('/api/cases')
        case = r.get_json()['cases'][0]
        assert 'id' in case
        assert 'title' in case
        assert 'type' in case
        assert 'status' in case
        assert 'risk_level' in case

class TestEnterprises:
    def test_enterprises(self, client):
        r = client.get('/api/enterprises')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] == True
        assert data['total'] >= 1

class TestDevices:
    def test_devices(self, client):
        r = client.get('/api/devices')
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] == True
        assert data['total'] >= 1

class TestUsers:
    def test_users_no_password(self, client):
        r = client.get('/api/users')
        assert r.status_code == 200
        users = r.get_json()['users']
        for u in users:
            assert 'password_hash' not in u

class TestRoles:
    def test_roles(self, client):
        r = client.get('/api/roles')
        assert r.status_code == 200
        roles = r.get_json()['roles']
        assert len(roles) == 5

class TestAuth:
    def test_login_success(self, client):
        r = client.post('/api/auth/login', json={'username': 'admin', 'password': 'admin123'})
        assert r.status_code == 200
        data = r.get_json()
        assert data['ok'] == True
        assert 'token' in data
    
    def test_login_wrong_password(self, client):
        r = client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrong'})
        assert r.status_code == 401
    
    def test_login_no_user(self, client):
        r = client.post('/api/auth/login', json={'username': 'nobody', 'password': 'x'})
        assert r.status_code == 404
    
    def test_register(self, client):
        r = client.post('/api/auth/register', json={'username': 'testuser', 'password': 'test123', 'role': 'public'})
        assert r.status_code == 200
        assert r.get_json()['ok'] == True

class TestStaticPages:
    @pytest.mark.parametrize('page', [
        'index.html', 'overview.html', 'ops-monitor.html', 'iot-diagnostic.html',
        'equipment-mall.html', 'eco-frontier.html', 'energy.html', 'm-portal.html'
    ])
    def test_page_200(self, client, page):
        r = client.get('/' + page)
        assert r.status_code == 200
