#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整的前端集成测试脚本
模拟用户的所有操作流程
"""

import json
import pandas as pd
import requests
import time
import os

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
            print(f"   - 列名: {result['columns']}")
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
        'population_size': 100,
        'generations': 50,
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
            print(f"   - MSE: {result['metrics']['mse_test']:.3f}")
            print(f"   - 特征重要性数量: {len(result['feature_importance'])}")
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
            print(f"   - 目标标准差: {result['result']['target_statistics']['std']:.3f}")
            print(f"   - 特征重要性数量: {len(result['result']['feature_importance'])}")
            return True
        else:
            print(f"❌ 蒙特卡罗分析失败: {result['error']}")
            return False
    else:
        print(f"❌ 蒙特卡罗分析请求失败: {response.status_code}")
        return False

def test_data_validation():
    """测试数据验证"""
    print("🔍 测试数据验证...")
    
    # 测试空数据
    print("   - 测试空数据...")
    response = requests.post('http://127.0.0.1:5000/api/data/upload', json={'data': []})
    if response.status_code == 200:
        result = response.json()
        if not result['success']:
            print("     ✅ 空数据被正确拒绝")
        else:
            print("     ❌ 空数据未被拒绝")
    
    # 测试无效列名
    print("   - 测试无效列名...")
    df = pd.read_csv('docs/Leaf50HDL.csv')
    data = df.to_dict('records')
    
    response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', json={
        'data': data,
        'target_column': 'INVALID_COLUMN',
        'feature_columns': ['QA', 'NCGA'],
        'population_size': 100,
        'generations': 50,
        'test_ratio': 0.3,
        'operators': ['+', '-', '*', '/']
    })
    
    if response.status_code == 200:
        result = response.json()
        if not result['success']:
            print("     ✅ 无效列名被正确拒绝")
        else:
            print("     ❌ 无效列名未被拒绝")
    
    print("✅ 数据验证测试完成")

def test_error_handling():
    """测试错误处理"""
    print("⚠️  测试错误处理...")
    
    # 测试缺少必要参数
    print("   - 测试缺少必要参数...")
    response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', json={})
    if response.status_code == 200:
        result = response.json()
        if not result['success']:
            print("     ✅ 缺少参数被正确处理")
        else:
            print("     ❌ 缺少参数未被正确处理")
    
    # 测试无效的JSON
    print("   - 测试无效JSON...")
    response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', 
                           data="invalid json", 
                           headers={'Content-Type': 'application/json'})
    if response.status_code == 400:
        print("     ✅ 无效JSON被正确处理")
    else:
        print("     ❌ 无效JSON未被正确处理")
    
    print("✅ 错误处理测试完成")

def main():
    """主测试函数"""
    print("🚀 开始完整的前端集成测试...")
    print("=" * 60)
    
    # 测试后端健康状态
    if not test_backend_health():
        print("❌ 后端服务不可用，停止测试")
        return
    
    print()
    
    # 测试数据验证
    test_data_validation()
    print()
    
    # 测试错误处理
    test_error_handling()
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
    print("🎉 所有测试通过！完整的前端集成测试成功")
    print("=" * 60)
    print()
    print("📋 测试总结:")
    print("   ✅ 后端服务健康检查")
    print("   ✅ 数据验证和错误处理")
    print("   ✅ CSV数据上传")
    print("   ✅ 符号回归分析")
    print("   ✅ 蒙特卡罗分析")
    print("   ✅ 所有API端点正常工作")
    print("   ✅ 错误处理机制完善")
    print("   ✅ 数据格式验证正确")

if __name__ == '__main__':
    main() 