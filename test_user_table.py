#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户管理表格功能
"""

import requests
import json
import time

def test_user_management():
    """测试用户管理功能"""
    base_url = "http://127.0.0.1:5000/api/auth"
    
    # 创建会话
    session = requests.Session()
    
    # 1. 登录管理员账户
    print("🔐 登录管理员账户...")
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = session.post(f"{base_url}/login", json=login_data)
    if response.status_code == 200:
        print("✅ 登录成功")
        print(f"响应: {response.json()}")
    else:
        print(f"❌ 登录失败: {response.status_code}")
        print(f"响应: {response.text}")
        return
    
    # 2. 获取用户列表
    print("\n📋 获取用户列表...")
    response = session.get(f"{base_url}/users")
    if response.status_code == 200:
        users_data = response.json()
        print("✅ 获取用户列表成功")
        print(f"用户数量: {len(users_data.get('users', []))}")
        
        # 显示用户信息
        for i, user in enumerate(users_data.get('users', []), 1):
            print(f"用户 {i}:")
            print(f"  用户名: {user.get('username')}")
            print(f"  角色: {user.get('role')}")
            print(f"  创建时间: {user.get('created_at')}")
            print(f"  最后登录: {user.get('last_login')}")
            print()
    else:
        print(f"❌ 获取用户列表失败: {response.status_code}")
        print(f"响应: {response.text}")
        return
    
    # 3. 测试前端页面
    print("🌐 测试前端页面...")
    try:
        response = requests.get("http://127.0.0.1:3000/")
        if response.status_code == 200:
            print("✅ 前端页面可访问")
            
            # 检查是否包含用户管理相关元素
            content = response.text
            if "用户管理" in content and "data-table" in content:
                print("✅ 用户管理页面结构正确")
            else:
                print("❌ 用户管理页面结构有问题")
        else:
            print(f"❌ 前端页面不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ 前端页面测试失败: {e}")
    
    # 4. 测试表格样式页面
    print("\n🎨 测试表格样式页面...")
    try:
        response = requests.get("http://127.0.0.1:3000/test_table_style.html")
        if response.status_code == 200:
            print("✅ 表格样式测试页面可访问")
            
            # 检查是否包含表格元素
            content = response.text
            if "<table>" in content and "role-badge" in content:
                print("✅ 表格样式正确应用")
            else:
                print("❌ 表格样式未正确应用")
        else:
            print(f"❌ 表格样式测试页面不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ 表格样式测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试用户管理表格功能...")
    test_user_management()
    print("\n✨ 测试完成!") 