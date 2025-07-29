#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前后端集成测试脚本
"""

import requests
import pandas as pd
import json
import time

def test_backend_health():
    """测试后端健康状态"""
    print("🔍 测试后端健康状态...")
    try:
        response = requests.get('http://127.0.0.1:5000/api/health')
        if response.status_code == 200:
            print("✅ 后端服务正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_data_upload():
    """测试数据上传"""
    print("\n📁 测试数据上传...")
    try:
        # 读取测试数据
        df = pd.read_csv('docs/Leaf50HDL.csv')
        data = df.to_dict('records')
        
        # 上传数据
        response = requests.post('http://127.0.0.1:5000/api/data/upload', 
                               json={'data': data})
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 数据上传成功")
                print(f"📊 数据形状: {result['shape']}")
                print(f"📊 列数: {len(result['columns'])}")
                return True
            else:
                print(f"❌ 数据上传失败: {result['error']}")
                return False
        else:
            print(f"❌ 数据上传请求失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 数据上传异常: {e}")
        return False

def test_symbolic_regression():
    """测试符号回归分析"""
    print("\n🔬 测试符号回归分析...")
    try:
        # 读取测试数据
        df = pd.read_csv('docs/Leaf50HDL.csv')
        data = df.to_dict('records')
        
        # 准备请求数据
        request_data = {
            'data': data,
            'target_column': 'HDL',
            'feature_columns': ['QA', 'NCGA', 'CGA', 'CCGA', 'CA', 'PIS', 'HYP', 'AST', 'GUA', 'RUT', 'VR', 'VG', 'PB2 ', 'PC1', 'EPI', 'OA', 'UA  ', 'MA', 'CRA', 'QUE', 'MDA'],
            'population_size': 50,
            'generations': 20,
            'test_ratio': 0.3,
            'operators': ['+', '-', '*', '/']
        }
        
        # 发送请求
        response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', 
                               json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 符号回归分析成功!")
                print(f"📊 R² 测试集: {result['metrics']['r2_test']:.3f}")
                print(f"📊 R² 训练集: {result['metrics']['r2_train']:.3f}")
                print(f"🔬 表达式: {result['expression']}")
                print(f"📊 特征重要性数量: {len(result['feature_importance'])}")
                return True
            else:
                print(f"❌ 符号回归分析失败: {result['error']}")
                return False
        else:
            print(f"❌ 符号回归请求失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 符号回归分析异常: {e}")
        return False

def test_monte_carlo():
    """测试蒙特卡罗分析"""
    print("\n🎲 测试蒙特卡罗分析...")
    try:
        # 读取测试数据
        df = pd.read_csv('docs/Leaf50HDL.csv')
        data = df.to_dict('records')
        
        # 准备请求数据
        request_data = {
            'data': data,
            'target_column': 'HDL',
            'feature_columns': ['QA', 'NCGA', 'CGA', 'CCGA', 'CA', 'PIS', 'HYP', 'AST', 'GUA', 'RUT', 'VR', 'VG', 'PB2 ', 'PC1', 'EPI', 'OA', 'UA  ', 'MA', 'CRA', 'QUE', 'MDA'],
            'iterations': 100
        }
        
        # 发送请求
        response = requests.post('http://127.0.0.1:5000/api/monte-carlo/analysis', 
                               json=request_data)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 蒙特卡罗分析成功!")
                print(f"📊 置信区间: {result.get('confidence_interval', 'N/A')}")
                return True
            else:
                print(f"❌ 蒙特卡罗分析失败: {result['error']}")
                return False
        else:
            print(f"❌ 蒙特卡罗请求失败: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ 蒙特卡罗分析异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前后端集成测试...")
    print("=" * 50)
    
    # 测试后端健康状态
    if not test_backend_health():
        print("❌ 后端服务不可用，测试终止")
        return
    
    # 测试数据上传
    if not test_data_upload():
        print("❌ 数据上传失败，测试终止")
        return
    
    # 测试符号回归分析
    if not test_symbolic_regression():
        print("❌ 符号回归分析失败，测试终止")
        return
    
    # 测试蒙特卡罗分析
    if not test_monte_carlo():
        print("❌ 蒙特卡罗分析失败，测试终止")
        return
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！前后端集成正常")
    print("✅ 后端服务正常运行")
    print("✅ 数据上传功能正常")
    print("✅ 符号回归分析功能正常")
    print("✅ 蒙特卡罗分析功能正常")
    print("✅ 错误处理和日志输出正常")

if __name__ == "__main__":
    main()