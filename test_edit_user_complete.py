#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整测试编辑用户功能
"""

import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000/api/auth'
FRONTEND_URL = 'http://127.0.0.1:3000'

def test_complete_edit_user_flow():
    """完整测试编辑用户功能流程"""
    print("🧪 开始完整测试编辑用户功能")
    
    # 创建session来保持登录状态
    session = requests.Session()
    
    # 1. 登录管理员账号
    print("\n📝 1. 登录管理员账号...")
    login_data = {"username": "admin", "password": "admin123"}
    
    try:
        response = session.post(f'{BASE_URL}/login', json=login_data)
        print(f"登录响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 登录成功")
            else:
                print(f"❌ 登录失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 登录请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 2. 创建测试用户
    print("\n📝 2. 创建测试用户...")
    test_username = f"complete_test_{int(time.time())}"
    user_data = {
        'username': test_username,
        'password': 'testpass123',
        'role': 'user'
    }
    
    try:
        response = session.post(f'{BASE_URL}/users', json=user_data)
        print(f"创建用户响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 创建测试用户成功: {test_username}")
            else:
                print(f"❌ 创建用户失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 创建用户请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 创建用户异常: {e}")
        return False
    
    # 3. 获取用户列表
    print("\n📝 3. 获取用户列表...")
    try:
        response = session.get(f'{BASE_URL}/users')
        print(f"获取用户列表响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                users = data.get('users', [])
                print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
                for user in users:
                    print(f"  - {user['username']} ({user['role']})")
            else:
                print(f"❌ 获取用户列表失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 获取用户列表请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户列表异常: {e}")
        return False
    
    # 4. 获取单个用户信息（模拟点击编辑按钮）
    print("\n📝 4. 获取单个用户信息...")
    try:
        response = session.get(f'{BASE_URL}/users/{test_username}')
        print(f"获取用户信息响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_info = data.get('user')
                print(f"✅ 获取用户信息成功:")
                print(f"  用户名: {user_info.get('username')}")
                print(f"  角色: {user_info.get('role')}")
                print(f"  创建时间: {user_info.get('created_at')}")
                print(f"  最后登录: {user_info.get('last_login')}")
            else:
                print(f"❌ 获取用户信息失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 获取用户信息请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return False
    
    # 5. 更新用户信息（模拟编辑表单提交）
    print("\n📝 5. 更新用户信息...")
    update_data = {
        'role': 'admin',
        'password': 'newpassword123'
    }
    
    try:
        response = session.put(f'{BASE_URL}/users/{test_username}', json=update_data)
        print(f"更新用户响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 更新用户信息成功")
            else:
                print(f"❌ 更新用户失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 更新用户请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 更新用户异常: {e}")
        return False
    
    # 6. 验证更新结果
    print("\n📝 6. 验证更新结果...")
    try:
        response = session.get(f'{BASE_URL}/users/{test_username}')
        print(f"验证更新响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_info = data.get('user')
                print(f"✅ 验证更新结果成功:")
                print(f"  用户名: {user_info.get('username')}")
                print(f"  角色: {user_info.get('role')} (已更新为管理员)")
                print(f"  创建时间: {user_info.get('created_at')}")
                
                if user_info.get('role') == 'admin':
                    print("✅ 角色更新验证成功")
                else:
                    print("❌ 角色更新验证失败")
                    return False
            else:
                print(f"❌ 验证更新失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 验证更新请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 验证更新异常: {e}")
        return False
    
    # 7. 再次获取用户列表验证
    print("\n📝 7. 再次获取用户列表验证...")
    try:
        response = session.get(f'{BASE_URL}/users')
        print(f"获取用户列表响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                users = data.get('users', [])
                print(f"✅ 获取用户列表成功，共 {len(users)} 个用户")
                
                # 查找测试用户
                test_user = None
                for user in users:
                    if user['username'] == test_username:
                        test_user = user
                        break
                
                if test_user:
                    print(f"✅ 找到测试用户: {test_user['username']} ({test_user['role']})")
                    if test_user['role'] == 'admin':
                        print("✅ 用户列表中角色更新验证成功")
                    else:
                        print("❌ 用户列表中角色更新验证失败")
                        return False
                else:
                    print("❌ 在用户列表中未找到测试用户")
                    return False
            else:
                print(f"❌ 获取用户列表失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 获取用户列表请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取用户列表异常: {e}")
        return False
    
    # 8. 清理测试用户
    print("\n📝 8. 清理测试用户...")
    try:
        response = session.delete(f'{BASE_URL}/users/{test_username}')
        print(f"删除用户响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ 删除测试用户成功: {test_username}")
            else:
                print(f"❌ 删除用户失败: {data.get('error')}")
        else:
            print(f"❌ 删除用户请求失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 删除用户异常: {e}")
    
    print("\n🎉 完整编辑用户功能测试完成")
    return True

if __name__ == "__main__":
    test_complete_edit_user_flow() 