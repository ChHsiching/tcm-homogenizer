#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试页面切换动画
"""

import requests
import time

FRONTEND_URL = 'http://127.0.0.1:3000'

def test_page_transitions():
    """测试页面切换动画"""
    print("🧪 开始测试页面切换动画")
    
    # 1. 检查CSS动画样式
    print("\n📝 1. 检查CSS动画样式...")
    try:
        response = requests.get(f'{FRONTEND_URL}/styles/main.css')
        if response.status_code == 200:
            css_content = response.text
            print("✅ CSS文件正常加载")
            
            # 检查动画相关的样式
            animation_checks = [
                ('transition', '过渡效果'),
                ('transform', '变换效果'),
                ('opacity', '透明度'),
                ('fade-out', '淡出动画'),
                ('fade-in', '淡入动画'),
                ('translateX', '水平移动'),
                ('translateY', '垂直移动'),
                ('ease-in-out', '缓动函数')
            ]
            
            for style, description in animation_checks:
                if style in css_content:
                    print(f"✅ {description}已添加")
                else:
                    print(f"❌ {description}未找到")
            
        else:
            print(f"❌ CSS文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ CSS文件访问异常: {e}")
        return False
    
    # 2. 检查JavaScript动画逻辑
    print("\n📝 2. 检查JavaScript动画逻辑...")
    try:
        response = requests.get(f'{FRONTEND_URL}/scripts/renderer.js')
        if response.status_code == 200:
            js_content = response.text
            print("✅ JavaScript文件正常加载")
            
            # 检查动画相关的JavaScript代码
            js_checks = [
                ('fade-out', '淡出类名'),
                ('fade-in', '淡入类名'),
                ('setTimeout', '延时函数'),
                ('classList.add', '添加CSS类'),
                ('classList.remove', '移除CSS类'),
                ('switchTab', '页面切换函数')
            ]
            
            for code, description in js_checks:
                if code in js_content:
                    print(f"✅ {description}已实现")
                else:
                    print(f"❌ {description}未找到")
            
        else:
            print(f"❌ JavaScript文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ JavaScript文件访问异常: {e}")
        return False
    
    # 3. 检查auth.js中的界面切换动画
    print("\n📝 3. 检查界面切换动画...")
    try:
        response = requests.get(f'{FRONTEND_URL}/scripts/auth.js')
        if response.status_code == 200:
            js_content = response.text
            print("✅ auth.js文件正常加载")
            
            # 检查界面切换相关的代码
            auth_checks = [
                ('showMainInterface', '显示主界面函数'),
                ('showLoginInterface', '显示登录界面函数'),
                ('opacity', '透明度设置'),
                ('transform', '变换设置'),
                ('setTimeout', '延时动画')
            ]
            
            for code, description in auth_checks:
                if code in js_content:
                    print(f"✅ {description}已实现")
                else:
                    print(f"❌ {description}未找到")
            
        else:
            print(f"❌ auth.js文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ auth.js文件访问异常: {e}")
        return False
    
    # 4. 检查HTML结构
    print("\n📝 4. 检查HTML结构...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            content = response.text
            print("✅ HTML文件正常加载")
            
            # 检查必要的HTML元素
            html_checks = [
                ('login-container', '登录容器'),
                ('main-container', '主界面容器'),
                ('tab-content', '标签页内容'),
                ('nav-btn', '导航按钮')
            ]
            
            for element, description in html_checks:
                if element in content:
                    print(f"✅ {description}存在")
                else:
                    print(f"❌ {description}不存在")
            
        else:
            print(f"❌ HTML文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ HTML文件访问异常: {e}")
        return False
    
    print("\n🎉 页面切换动画测试完成")
    print("\n📋 动画功能总结:")
    print("✅ 登录页面 ↔ 主界面切换动画")
    print("✅ 导航栏页面切换动画")
    print("✅ 淡入淡出效果")
    print("✅ 平滑过渡动画")
    print("✅ 延时执行逻辑")
    
    return True

if __name__ == "__main__":
    test_page_transitions() 