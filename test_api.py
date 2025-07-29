#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
"""

import requests
import pandas as pd
import json
import sys

def test_data_upload():
    """测试数据上传API"""
    print("🔬 测试数据上传API...")
    
    # 读取测试数据
    try:
        df = pd.read_csv('docs/Leaf50HDL.csv')
        print(f"📊 读取数据成功，形状: {df.shape}")
        print(f"📊 列名: {df.columns.tolist()}")
        
        # 准备上传数据
        data = df.to_dict('records')
        
        # 发送请求
        response = requests.post(
            'http://localhost:5000/api/data/upload',
            json={'data': data},
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 数据上传成功")
                print(f"📊 数值列: {result['numeric_columns']}")
                return result
            else:
                print(f"❌ 数据上传失败: {result['error']}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 测试数据上传失败: {str(e)}")
        return None

def test_symbolic_regression(upload_result):
    """测试符号回归API"""
    print("\n🔬 测试符号回归API...")
    
    if not upload_result:
        print("❌ 没有上传数据，跳过符号回归测试")
        return
    
    # 准备参数
    target_column = 'HDL'  # 最后一列是目标变量
    feature_columns = [col for col in upload_result['columns'] if col != target_column]
    
    print(f"🎯 目标变量: {target_column}")
    print(f"📊 特征变量数量: {len(feature_columns)}")
    
    # 发送请求
    response = requests.post(
        'http://localhost:5000/api/regression/symbolic-regression',
        json={
            'data': upload_result['data'],
            'target_column': target_column,
            'feature_columns': feature_columns,
            'population_size': 50,
            'generations': 20,
            'test_ratio': 0.3,
            'operators': ['+', '-', '*', '/']
        },
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"📡 响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if result['success']:
            print("✅ 符号回归分析成功")
            print(f"📊 表达式: {result['expression']}")
            print(f"📊 R²测试: {result['metrics']['r2_test']:.3f}")
            print(f"📊 MSE测试: {result['metrics']['mse_test']:.3f}")
            return result
        else:
            print(f"❌ 符号回归分析失败: {result['error']}")
            return None
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"响应内容: {response.text}")
        return None

def main():
    """主函数"""
    print("🚀 开始API测试...")
    
    # 测试数据上传
    upload_result = test_data_upload()
    
    # 测试符号回归
    regression_result = test_symbolic_regression(upload_result)
    
    if regression_result:
        print("\n🎉 所有测试通过！")
    else:
        print("\n❌ 测试失败")
        sys.exit(1)

if __name__ == '__main__':
    main()