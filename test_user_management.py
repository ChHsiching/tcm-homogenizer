#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理功能测试脚本
"""

import requests
import json
import time

# 配置
BASE_URL = 'http://127.0.0.1:5000/api/auth'
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

def test_login():
    """测试管理员登录"""
    print("🔐 测试管理员登录...")
    
    response = requests.post(f'{BASE_URL}/login', 
                           json={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD},
                           headers={'Content-Type': 'application/json'})
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✅ 登录成功")
            return response.cookies
        else:
            print("❌ 登录失败")
            return None
    else:
        print("❌ 登录请求失败")
        return None

def test_get_users(cookies):
    """测试获取用户列表"""
    print("\n👥 测试获取用户列表...")
    
    response = requests.get(f'{BASE_URL}/users', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            users = data.get('users', [])
            print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
            for user in users:
                print(f"  - {user['username']} ({user['role']})")
            return True
        else:
            print("❌ 获取用户列表失败")
            return False
    else:
        print("❌ 获取用户列表请求失败")
        return False

def test_create_user(cookies):
    """测试创建用户"""
    print("\n➕ 测试创建用户...")
    
    new_username = f"testuser_{int(time.time())}"
    new_password = "123456"
    new_role = "user"
    
    response = requests.post(f'{BASE_URL}/users',
                           json={'username': new_username, 'password': new_password, 'role': new_role},
                           headers={'Content-Type': 'application/json'},
                           cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 创建用户成功: {new_username}")
            return new_username
        else:
            print("❌ 创建用户失败")
            return None
    else:
        print("❌ 创建用户请求失败")
        return None

def test_delete_user(cookies, username):
    """测试删除用户"""
    print(f"\n🗑️ 测试删除用户: {username}")
    
    response = requests.delete(f'{BASE_URL}/users/{username}', cookies=cookies)
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print(f"✅ 删除用户成功: {username}")
            return True
        else:
            print("❌ 删除用户失败")
            return False
    else:
        print("❌ 删除用户请求失败")
        return False

def main():
    """主测试函数"""
    print("🚀 开始用户管理功能测试")
    print("=" * 50)
    
    # 1. 测试登录
    cookies = test_login()
    if not cookies:
        print("❌ 登录失败，无法继续测试")
        return
    
    # 2. 测试获取用户列表
    if not test_get_users(cookies):
        print("❌ 获取用户列表失败")
        return
    
    # 3. 测试创建用户
    new_username = test_create_user(cookies)
    if not new_username:
        print("❌ 创建用户失败")
        return
    
    # 4. 再次获取用户列表，验证新用户是否创建成功
    print("\n🔄 验证新用户是否创建成功...")
    test_get_users(cookies)
    
    # 5. 测试删除用户
    test_delete_user(cookies, new_username)
    
    # 6. 最终验证用户列表
    print("\n🔄 最终验证用户列表...")
    test_get_users(cookies)
    
    print("\n✅ 用户管理功能测试完成")

if __name__ == "__main__":
    main() 