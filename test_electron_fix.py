#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Electron权限修复
"""

import requests
import json

def test_electron_permissions():
    """测试Electron中的权限修复"""
    print('🚀 测试Electron权限修复...')
    
    # 1. 先登录获取session
    session = requests.Session()
    login_data = {"username": "admin", "password": "admin123"}
    
    print('🔐 登录管理员账户...')
    response = session.post("http://127.0.0.1:5000/api/auth/login", json=login_data)
    if response.status_code != 200:
        print(f'❌ 登录失败: {response.status_code}')
        return
    
    print('✅ 登录成功')
    
    # 2. 测试使用X-Username请求头创建用户
    print('\n📝 测试使用X-Username请求头创建用户...')
    headers = {
        'Content-Type': 'application/json',
        'X-Username': 'admin'
    }
    
    user_data = {
        'username': 'ElectronTestUser',
        'password': '123456',
        'role': 'user'
    }
    
    response = requests.post(
        "http://127.0.0.1:5000/api/auth/users",
        headers=headers,
        json=user_data
    )
    
    print(f'响应状态: {response.status_code}')
    result = response.json()
    print(f'响应内容: {result}')
    
    if response.status_code == 200 and result.get('success'):
        print('✅ 使用X-Username请求头创建用户成功')
    else:
        print('❌ 使用X-Username请求头创建用户失败')
    
    # 3. 测试使用X-Username请求头删除用户
    print('\n🗑️ 测试使用X-Username请求头删除用户...')
    response = requests.delete(
        "http://127.0.0.1:5000/api/auth/users/ElectronTestUser",
        headers={'X-Username': 'admin'}
    )
    
    print(f'响应状态: {response.status_code}')
    result = response.json()
    print(f'响应内容: {result}')
    
    if response.status_code == 200 and result.get('success'):
        print('✅ 使用X-Username请求头删除用户成功')
    else:
        print('❌ 使用X-Username请求头删除用户失败')
    
    # 4. 测试使用X-Username请求头获取用户列表
    print('\n📋 测试使用X-Username请求头获取用户列表...')
    response = requests.get(
        "http://127.0.0.1:5000/api/auth/users",
        headers={'X-Username': 'admin'}
    )
    
    print(f'响应状态: {response.status_code}')
    result = response.json()
    print(f'用户数量: {len(result.get("users", []))}')
    
    if response.status_code == 200 and result.get('success'):
        print('✅ 使用X-Username请求头获取用户列表成功')
    else:
        print('❌ 使用X-Username请求头获取用户列表失败')
    
    print('\n✨ 测试完成!')

if __name__ == "__main__":
    test_electron_permissions() 