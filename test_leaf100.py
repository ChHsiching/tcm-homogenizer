#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Leaf100HDL.csv文件
"""

import requests
import json
import pandas as pd

def test_leaf100():
    """测试Leaf100HDL.csv文件"""
    
    print("🔬 开始测试Leaf100HDL.csv文件...")
    
    # 读取测试数据
    df = pd.read_csv('docs/Leaf100HDL.csv')
    print(f"📊 数据形状: {df.shape}")
    print(f"📋 列名: {list(df.columns)}")
    
    # 模拟前端数据上传
    upload_data = {
        'data': df.to_dict('records')
    }
    
    try:
        response = requests.post(
            'http://127.0.0.1:5000/api/data/upload',
            headers={'Content-Type': 'application/json'},
            json=upload_data
        )
        
        print(f"📡 上传响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ 数据上传成功!")
                print(f"📊 数据形状: {result['shape']}")
                
                # 模拟符号回归分析
                target_column = 'HDL'
                feature_columns = [col for col in df.columns if col != target_column]
                
                regression_data = {
                    'data': df.to_dict('records'),
                    'target_column': target_column,
                    'feature_columns': feature_columns,
                    'population_size': 50,
                    'generations': 20,
                    'test_ratio': 0.3,
                    'operators': ['add', 'subtract', 'multiply', 'divide']
                }
                
                regression_response = requests.post(
                    'http://127.0.0.1:5000/api/regression/symbolic-regression',
                    headers={'Content-Type': 'application/json'},
                    json=regression_data
                )
                
                print(f"📡 回归响应状态: {regression_response.status_code}")
                
                if regression_response.status_code == 200:
                    regression_result = regression_response.json()
                    if regression_result.get('success'):
                        print("✅ 符号回归分析成功!")
                        print(f"📊 表达式: {regression_result['expression'][:100]}...")
                        print(f"📈 R²: {regression_result['metrics']['r2_test']:.3f}")
                        print(f"📉 MSE: {regression_result['metrics']['mse_test']:.3f}")
                        
                        # 显示特征重要性
                        if 'feature_importance' in regression_result:
                            print("\n📊 特征重要性 (前5名):")
                            sorted_features = sorted(regression_result['feature_importance'], 
                                                  key=lambda x: x['importance'], reverse=True)
                            for i, feature in enumerate(sorted_features[:5]):
                                print(f"  {i+1}. {feature['feature']}: {feature['importance']:.3f}")
                    else:
                        print(f"❌ 符号回归分析失败: {regression_result.get('error')}")
                else:
                    print(f"❌ 回归HTTP错误: {regression_response.status_code}")
                    
            else:
                print(f"❌ 数据上传失败: {result.get('error')}")
        else:
            print(f"❌ 上传HTTP错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    print("\n🎉 Leaf100HDL.csv测试完成!")

if __name__ == '__main__':
    test_leaf100()