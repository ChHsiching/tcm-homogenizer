#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试前端用户管理功能
"""

import requests
import json
import time

def test_frontend_user_management():
    """测试前端用户管理功能"""
    
    # 1. 测试主页面结构
    print("🌐 测试主页面结构...")
    try:
        response = requests.get("http://127.0.0.1:3000/")
        if response.status_code == 200:
            print("✅ 主页面可访问")
            
            content = response.text
            
            # 检查用户管理相关元素
            if 'id="user-management"' in content:
                print("✅ 用户管理div存在")
                
                # 检查用户操作按钮
                if 'id="add-user-btn"' in content and 'id="refresh-users-btn"' in content:
                    print("✅ 用户操作按钮存在")
                else:
                    print("❌ 用户操作按钮缺失")
                
                # 检查用户表格容器
                if 'id="users-table"' in content and 'class="data-table"' in content:
                    print("✅ 用户表格容器存在且样式正确")
                else:
                    print("❌ 用户表格容器有问题")
            else:
                print("❌ 用户管理div不存在")
        else:
            print(f"❌ 主页面不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页面测试失败: {e}")
    
    # 2. 测试表格样式页面
    print("\n🎨 测试表格样式页面...")
    try:
        response = requests.get("http://127.0.0.1:3000/test_table_style.html")
        if response.status_code == 200:
            print("✅ 表格样式测试页面可访问")
            
            content = response.text
            
            # 检查表格结构
            if '<table>' in content:
                print("✅ 表格元素存在")
                
                # 检查表头
                if '<thead>' in content and '<th>' in content:
                    print("✅ 表格表头存在")
                    
                    # 检查是否包含基本的表头内容
                    if '用户名' in content and '角色' in content and '操作' in content:
                        print("✅ 表格表头内容正确")
                    else:
                        print("❌ 表格表头内容不完整")
                else:
                    print("❌ 表格表头不存在")
                
                # 检查表格内容
                if '<tbody>' in content and '<tr>' in content:
                    print("✅ 表格内容存在")
                    
                    # 检查角色徽章
                    if 'role-badge' in content:
                        print("✅ 角色徽章样式存在")
                    else:
                        print("❌ 角色徽章样式不存在")
                    
                    # 检查状态指示器
                    if 'status-indicator' in content:
                        print("✅ 状态指示器存在")
                    else:
                        print("❌ 状态指示器不存在")
                    
                    # 检查操作按钮
                    if 'btn-sm' in content:
                        print("✅ 操作按钮样式存在")
                    else:
                        print("❌ 操作按钮样式不存在")
                else:
                    print("❌ 表格内容不存在")
            else:
                print("❌ 表格元素不存在")
        else:
            print(f"❌ 表格样式测试页面不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ 表格样式测试失败: {e}")
    
    # 3. 测试CSS样式文件
    print("\n🎨 测试CSS样式文件...")
    try:
        response = requests.get("http://127.0.0.1:3000/styles/main.css")
        if response.status_code == 200:
            print("✅ CSS样式文件可访问")
            
            css_content = response.text
            
            # 检查关键样式类
            required_classes = [
                '.data-table table',
                '.data-table th',
                '.data-table td',
                '.role-badge',
                '.status-indicator',
                '.btn-sm'
            ]
            
            missing_classes = []
            for class_name in required_classes:
                if class_name not in css_content:
                    missing_classes.append(class_name)
            
            if not missing_classes:
                print("✅ 所有必需的CSS样式类都存在")
            else:
                print(f"❌ 缺少CSS样式类: {missing_classes}")
        else:
            print(f"❌ CSS样式文件不可访问: {response.status_code}")
    except Exception as e:
        print(f"❌ CSS样式文件测试失败: {e}")
    
    # 4. 测试后端API
    print("\n🔧 测试后端API...")
    try:
        session = requests.Session()
        
        # 登录
        login_data = {"username": "admin", "password": "admin123"}
        response = session.post("http://127.0.0.1:5000/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            print("✅ 后端登录API正常")
            
            # 获取用户列表
            response = session.get("http://127.0.0.1:5000/api/auth/users")
            if response.status_code == 200:
                users_data = response.json()
                print(f"✅ 后端用户列表API正常，返回 {len(users_data.get('users', []))} 个用户")
            else:
                print(f"❌ 后端用户列表API失败: {response.status_code}")
        else:
            print(f"❌ 后端登录API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 后端API测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始测试前端用户管理功能...")
    test_frontend_user_management()
    print("\n✨ 测试完成!") 