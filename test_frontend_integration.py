#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端集成测试脚本
模拟前端的完整操作流程
"""

import json
import pandas as pd
import requests
import time

def test_data_upload():
    """测试数据上传"""
    print("📁 测试数据上传...")
    
    # 读取测试数据
    df = pd.read_csv('docs/Leaf50HDL.csv')
    data = df.to_dict('records')
    
    # 准备请求数据
    request_data = {
        'data': data
    }
    
    # 发送请求
    response = requests.post('http://127.0.0.1:5000/api/data/upload', json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 数据上传成功")
            print(f"   - 列数: {result['shape'][1]}")
            print(f"   - 行数: {result['shape'][0]}")
            return True
        else:
            print(f"❌ 数据上传失败: {result['error']}")
            return False
    else:
        print(f"❌ 数据上传请求失败: {response.status_code}")
        return False

def test_symbolic_regression():
    """测试符号回归分析"""
    print("🔬 测试符号回归分析...")
    
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
    response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 符号回归分析成功")
            print(f"   - 表达式: {result['expression']}")
            print(f"   - R²: {result['metrics']['r2_test']:.3f}")
            return True
        else:
            print(f"❌ 符号回归分析失败: {result['error']}")
            return False
    else:
        print(f"❌ 符号回归分析请求失败: {response.status_code}")
        return False

def test_monte_carlo_analysis():
    """测试蒙特卡罗分析"""
    print("🎲 测试蒙特卡罗分析...")
    
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
    response = requests.post('http://127.0.0.1:5000/api/monte-carlo/analysis', json=request_data)
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 蒙特卡罗分析成功")
            print(f"   - 分析ID: {result['result']['analysis_id']}")
            print(f"   - 有效样本数: {result['result']['valid_samples_count']}")
            print(f"   - 目标均值: {result['result']['target_statistics']['mean']:.3f}")
            return True
        else:
            print(f"❌ 蒙特卡罗分析失败: {result['error']}")
            return False
    else:
        print(f"❌ 蒙特卡罗分析请求失败: {response.status_code}")
        return False

def test_backend_health():
    """测试后端健康状态"""
    print("🏥 测试后端健康状态...")
    
    response = requests.get('http://127.0.0.1:5000/api/health')
    
    if response.status_code == 200:
        result = response.json()
        print("✅ 后端服务正常")
        print(f"   - 服务: {result['service']}")
        print(f"   - 状态: {result['status']}")
        print(f"   - 版本: {result['version']}")
        return True
    else:
        print(f"❌ 后端服务异常: {response.status_code}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前端集成测试...")
    print("=" * 50)
    
    # 测试后端健康状态
    if not test_backend_health():
        print("❌ 后端服务不可用，停止测试")
        return
    
    print()
    
    # 测试数据上传
    if not test_data_upload():
        print("❌ 数据上传失败，停止测试")
        return
    
    print()
    
    # 测试符号回归分析
    if not test_symbolic_regression():
        print("❌ 符号回归分析失败，停止测试")
        return
    
    print()
    
    # 测试蒙特卡罗分析
    if not test_monte_carlo_analysis():
        print("❌ 蒙特卡罗分析失败，停止测试")
        return
    
    print()
    print("🎉 所有测试通过！前端集成测试成功")
    print("=" * 50)

if __name__ == '__main__':
    main()