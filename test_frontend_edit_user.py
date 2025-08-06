#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端编辑用户功能
"""

import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000/api/auth'
FRONTEND_URL = 'http://127.0.0.1:3000'

def test_frontend_edit_user():
    """测试前端编辑用户功能"""
    print("🧪 开始测试前端编辑用户功能")
    
    # 1. 检查前端页面是否正常
    print("\n📝 1. 检查前端页面...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            content = response.text
            # 检查编码问题，尝试不同的编码方式
            if '用户管理' in content or 'user-management' in content:
                print("✅ 前端页面正常，包含用户管理功能")
            else:
                print("❌ 前端页面缺少用户管理功能")
                print(f"页面内容片段: {content[:200]}...")
                return False
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面访问异常: {e}")
        return False
    
    # 2. 创建测试用户
    print("\n📝 2. 创建测试用户...")
    session = requests.Session()
    
    # 登录管理员
    login_data = {"username": "admin", "password": "admin123"}
    response = session.post(f'{BASE_URL}/login', json=login_data)
    if response.status_code != 200:
        print("❌ 登录失败")
        return False
    
    # 创建测试用户
    test_username = f"edituser_{int(time.time())}"
    user_data = {
        'username': test_username,
        'password': 'testpass123',
        'role': 'user'
    }
    
    response = session.post(f'{BASE_URL}/users', json=user_data)
    if response.status_code != 200:
        print("❌ 创建测试用户失败")
        return False
    
    print(f"✅ 创建测试用户成功: {test_username}")
    
    # 3. 模拟前端编辑用户流程
    print("\n📝 3. 模拟前端编辑用户流程...")
    
    # 获取用户信息（模拟点击编辑按钮）
    response = session.get(f'{BASE_URL}/users/{test_username}')
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            user_info = data.get('user')
            print(f"✅ 获取用户信息成功:")
            print(f"  用户名: {user_info.get('username')}")
            print(f"  角色: {user_info.get('role')}")
            
            # 模拟编辑用户（更新角色和密码）
            update_data = {
                'role': 'admin',
                'password': 'newpassword123'
            }
            
            response = session.put(f'{BASE_URL}/users/{test_username}', json=update_data)
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ 编辑用户成功")
                    
                    # 验证更新结果
                    response = session.get(f'{BASE_URL}/users/{test_username}')
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('success'):
                            user_info = data.get('user')
                            if user_info.get('role') == 'admin':
                                print("✅ 用户角色更新验证成功")
                            else:
                                print("❌ 用户角色更新验证失败")
                                return False
                        else:
                            print("❌ 验证更新结果失败")
                            return False
                    else:
                        print("❌ 验证更新结果请求失败")
                        return False
                else:
                    print(f"❌ 编辑用户失败: {data.get('error')}")
                    return False
            else:
                print(f"❌ 编辑用户请求失败: {response.status_code}")
                return False
        else:
            print(f"❌ 获取用户信息失败: {data.get('error')}")
            return False
    else:
        print(f"❌ 获取用户信息请求失败: {response.status_code}")
        return False
    
    # 4. 清理测试用户
    print("\n📝 4. 清理测试用户...")
    response = session.delete(f'{BASE_URL}/users/{test_username}')
    if response.status_code == 200:
        print(f"✅ 删除测试用户成功: {test_username}")
    else:
        print(f"❌ 删除测试用户失败: {response.status_code}")
    
    print("\n🎉 前端编辑用户功能测试完成")
    return True

if __name__ == "__main__":
    test_frontend_edit_user() 