#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
"""

import requests
import json
import pandas as pd

def test_symbolic_regression():
    """测试符号回归API"""
    
    # 读取测试数据
    df = pd.read_csv('docs/Leaf50HDL.csv')
    print(f"📊 数据形状: {df.shape}")
    print(f"📋 列名: {list(df.columns)}")
    
    # 准备数据
    target_column = 'HDL'
    feature_columns = [col for col in df.columns if col != target_column]
    
    # 转换为字典格式
    data = df.to_dict('records')
    
    # 准备请求
    request_data = {
        'data': data,
        'target_column': target_column,
        'feature_columns': feature_columns,
        'population_size': 50,
        'generations': 20,
        'test_ratio': 0.3,
        'operators': ['add', 'subtract', 'multiply', 'divide']
    }
    
    print(f"🎯 目标变量: {target_column}")
    print(f"📊 特征变量: {feature_columns}")
    print(f"📋 数据样本数: {len(data)}")
    
    # 发送请求
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/regression/symbolic-regression',
            headers={'Content-Type': 'application/json'},
            json=request_data
        )
        
        print(f"📡 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ 符号回归分析成功!")
                if 'result' in result and 'expression' in result['result']:
                    print(f"📊 表达式: {result['result']['expression']}")
                if 'result' in result and 'metrics' in result['result']:
                    print(f"📈 R²: {result['result']['metrics']['r2_test']:.3f}")
                    print(f"📉 MSE: {result['result']['metrics']['mse_test']:.3f}")
            else:
                print(f"❌ 符号回归分析失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"📋 响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")

if __name__ == '__main__':
    test_symbolic_regression()