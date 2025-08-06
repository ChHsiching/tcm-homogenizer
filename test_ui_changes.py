#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试UI修改
"""

import requests

FRONTEND_URL = 'http://127.0.0.1:3000'

def test_ui_changes():
    """测试UI修改"""
    print("🧪 开始测试UI修改")
    
    # 1. 检查前端页面是否正常加载
    print("\n📝 1. 检查前端页面...")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            content = response.text
            print("✅ 前端页面正常加载")
            
            # 检查项目名称更新
            if '本草智配' in content:
                print("✅ 项目名称已更新为'本草智配'")
            else:
                print("❌ 项目名称未更新")
                return False
            
            # 检查是否还有旧的项目名称
            if '中药多组分均化分析' in content:
                print("⚠️ 发现旧项目名称，需要进一步更新")
            else:
                print("✅ 旧项目名称已完全替换")
            
            # 检查logo引用
            if 'assets/icons/logo.png' in content:
                print("✅ Logo引用已添加")
            else:
                print("❌ Logo引用未找到")
                return False
                
        else:
            print(f"❌ 前端页面访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端页面访问异常: {e}")
        return False
    
    # 2. 检查CSS样式更新
    print("\n📝 2. 检查CSS样式...")
    try:
        response = requests.get(f'{FRONTEND_URL}/styles/main.css')
        if response.status_code == 200:
            css_content = response.text
            print("✅ CSS文件正常加载")
            
            # 检查新的样式类
            style_checks = [
                ('login-logo', '登录页面Logo样式'),
                ('logo-image', 'Logo图片样式'),
                ('header-logo', '头部Logo样式'),
                ('header-logo-image', '头部Logo图片样式'),
                ('backdrop-filter', '背景模糊效果'),
                ('radial-gradient', '径向渐变背景'),
                ('@keyframes float', '浮动动画')
            ]
            
            for style, description in style_checks:
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
    
    # 3. 检查Logo文件是否存在
    print("\n📝 3. 检查Logo文件...")
    try:
        response = requests.get(f'{FRONTEND_URL}/assets/icons/logo.png')
        if response.status_code == 200:
            print("✅ Logo文件存在且可访问")
        else:
            print(f"❌ Logo文件访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Logo文件访问异常: {e}")
        return False
    
    print("\n🎉 UI修改测试完成")
    return True

if __name__ == "__main__":
    test_ui_changes() 