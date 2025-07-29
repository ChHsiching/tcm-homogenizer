#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端数据上传测试脚本
"""

import requests
import json
import pandas as pd

def test_frontend_upload():
    """测试前端数据上传功能"""
    
    print("📁 开始测试前端数据上传功能...")
    
    # 读取测试数据
    df = pd.read_csv('docs/Leaf50HDL.csv')
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
        
        print(f"📡 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"📋 完整响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('success'):
                print("✅ 数据上传成功!")
                print(f"📊 数据形状: {result['shape']}")
                print(f"📋 数值列: {result['numeric_columns']}")
                
                # 模拟前端显示数据
                print("\n📊 数据预览:")
                print(f"  样本数量: {result['shape'][0]}")
                print(f"  特征数量: {result['shape'][1] - 1}")  # 减去目标变量
                print(f"  目标变量: HDL")
                print(f"  特征变量: {len(result['numeric_columns']) - 1} 个")
                
                # 显示前几个特征
                feature_columns = [col for col in result['numeric_columns'] if col != 'HDL']
                print(f"  主要特征: {feature_columns[:5]}...")
                
            else:
                print(f"❌ 数据上传失败: {result.get('error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"📋 响应内容: {response.text}")
            
    except Exception as e:
        print(f"❌ 数据上传异常: {str(e)}")
    
    print("\n🎉 前端数据上传测试完成!")

if __name__ == '__main__':
    test_frontend_upload()