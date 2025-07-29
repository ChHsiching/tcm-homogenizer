#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端API测试脚本
"""

import requests
import json
import pandas as pd

def test_frontend_workflow():
    """测试前端工作流程"""
    
    print("🔬 开始测试前端工作流程...")
    
    # 1. 读取测试数据
    df = pd.read_csv('docs/Leaf50HDL.csv')
    print(f"📊 数据形状: {df.shape}")
    print(f"📋 列名: {list(df.columns)}")
    
    # 2. 模拟数据上传
    print("\n📁 步骤1: 数据上传")
    upload_data = {
        'data': df.to_dict('records')
    }
    
    try:
        upload_response = requests.post(
            'http://127.0.0.1:5000/api/data/upload',
            headers={'Content-Type': 'application/json'},
            json=upload_data
        )
        
        print(f"📡 上传响应状态: {upload_response.status_code}")
        
        if upload_response.status_code == 200:
            upload_result = upload_response.json()
            if upload_result.get('success'):
                print("✅ 数据上传成功!")
                print(f"📊 数据形状: {upload_result['shape']}")
                print(f"📋 数值列: {upload_result['numeric_columns']}")
            else:
                print(f"❌ 数据上传失败: {upload_result.get('error')}")
                return
        else:
            print(f"❌ 上传HTTP错误: {upload_response.status_code}")
            print(f"📋 响应内容: {upload_response.text}")
            return
            
    except Exception as e:
        print(f"❌ 数据上传异常: {str(e)}")
        return
    
    # 3. 模拟符号回归分析
    print("\n🔬 步骤2: 符号回归分析")
    
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
    
    try:
        regression_response = requests.post(
            'http://127.0.0.1:5000/api/regression/symbolic-regression',
            headers={'Content-Type': 'application/json'},
            json=regression_data
        )
        
        print(f"📡 回归响应状态: {regression_response.status_code}")
        
        if regression_response.status_code == 200:
            regression_result = regression_response.json()
            print(f"📋 完整响应: {json.dumps(regression_result, indent=2, ensure_ascii=False)}")
            
            if regression_result.get('success'):
                print("✅ 符号回归分析成功!")
                if 'expression' in regression_result:
                    print(f"📊 表达式: {regression_result['expression']}")
                if 'metrics' in regression_result:
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
            print(f"📋 响应内容: {regression_response.text}")
            
    except Exception as e:
        print(f"❌ 符号回归分析异常: {str(e)}")
    
    print("\n🎉 前端工作流程测试完成!")

if __name__ == '__main__':
    test_frontend_workflow()