#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户查找修复
"""

import requests
import time
import json

BASE_URL = 'http://127.0.0.1:5000/api/auth'

def test_user_lookup_fix():
    """测试用户查找修复"""
    print("🧪 开始测试用户查找修复")
    
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
    
    # 2. 获取用户列表
    print("\n📝 2. 获取用户列表...")
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
    
    # 3. 测试获取张三用户信息
    print("\n📝 3. 测试获取张三用户信息...")
    try:
        response = session.get(f'{BASE_URL}/users/张三')
        print(f"获取张三用户信息响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_info = data.get('user')
                print(f"✅ 获取张三用户信息成功:")
                print(f"  用户名: {user_info.get('username')}")
                print(f"  角色: {user_info.get('role')}")
            else:
                print(f"❌ 获取张三用户信息失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 获取张三用户信息请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取张三用户信息异常: {e}")
        return False
    
    # 4. 测试获取李四用户信息
    print("\n📝 4. 测试获取李四用户信息...")
    try:
        response = session.get(f'{BASE_URL}/users/李四')
        print(f"获取李四用户信息响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                user_info = data.get('user')
                print(f"✅ 获取李四用户信息成功:")
                print(f"  用户名: {user_info.get('username')}")
                print(f"  角色: {user_info.get('role')}")
            else:
                print(f"❌ 获取李四用户信息失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 获取李四用户信息请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取李四用户信息异常: {e}")
        return False
    
    # 5. 测试编辑张三用户
    print("\n📝 5. 测试编辑张三用户...")
    update_data = {
        'role': 'admin'
    }
    
    try:
        response = session.put(f'{BASE_URL}/users/张三', json=update_data)
        print(f"编辑张三用户响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 编辑张三用户成功")
                
                # 验证更新结果
                response = session.get(f'{BASE_URL}/users/张三')
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        user_info = data.get('user')
                        if user_info.get('role') == 'admin':
                            print("✅ 张三用户角色更新验证成功")
                        else:
                            print("❌ 张三用户角色更新验证失败")
                            return False
                    else:
                        print("❌ 验证张三用户更新失败")
                        return False
                else:
                    print("❌ 验证张三用户更新请求失败")
                    return False
            else:
                print(f"❌ 编辑张三用户失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 编辑张三用户请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 编辑张三用户异常: {e}")
        return False
    
    # 6. 测试删除李四用户
    print("\n📝 6. 测试删除李四用户...")
    try:
        response = session.delete(f'{BASE_URL}/users/李四')
        print(f"删除李四用户响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 删除李四用户成功")
                
                # 验证删除结果
                response = session.get(f'{BASE_URL}/users/李四')
                if response.status_code == 404:
                    print("✅ 李四用户删除验证成功")
                else:
                    print("❌ 李四用户删除验证失败")
                    return False
            else:
                print(f"❌ 删除李四用户失败: {data.get('error')}")
                return False
        else:
            print(f"❌ 删除李四用户请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 删除李四用户异常: {e}")
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
                
                # 检查张三是否还在列表中（应该还在，因为只是编辑了角色）
                zhangsan_found = False
                lisi_found = False
                
                for user in users:
                    if user['username'] == '张三':
                        zhangsan_found = True
                        print(f"✅ 张三仍在列表中，角色: {user['role']}")
                    elif user['username'] == '李四':
                        lisi_found = True
                        print(f"❌ 李四仍在列表中，删除失败")
                
                if zhangsan_found and not lisi_found:
                    print("✅ 用户列表验证成功")
                else:
                    print("❌ 用户列表验证失败")
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
    
    print("\n🎉 用户查找修复测试完成")
    return True

if __name__ == "__main__":
    test_user_lookup_fix() 