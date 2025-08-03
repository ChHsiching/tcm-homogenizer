#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端模拟测试脚本
使用docs目录下的真实CSV文件，模拟前端API调用
"""

import json
import pandas as pd
import requests
import time
import os
import sys

def test_backend_health():
    """测试后端健康状态"""
    print("🏥 测试后端健康状态...")
    
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 后端服务正常")
            print(f"   - 服务: {result.get('service', 'unknown')}")
            print(f"   - 状态: {result.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到后端服务: {e}")
        return False

def test_data_upload_with_real_csv():
    """使用真实CSV文件测试数据上传"""
    print("📁 测试数据上传（使用真实CSV文件）...")
    
    # 使用docs目录下的CSV文件
    csv_files = ['docs/Leaf50HDL.csv', 'docs/Leaf100HDL.csv']
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"❌ CSV文件不存在: {csv_file}")
            continue
            
        print(f"📊 测试文件: {csv_file}")
        
        try:
            # 读取CSV文件
            df = pd.read_csv(csv_file)
            data = df.to_dict('records')
            
            # 准备请求数据
            request_data = {
                'data': data
            }
            
            # 发送请求
            response = requests.post('http://127.0.0.1:5000/api/data/upload', 
                                  json=request_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result['success']:
                    print("✅ 数据上传成功")
                    print(f"   - 文件: {csv_file}")
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
                
        except Exception as e:
            print(f"❌ 处理文件 {csv_file} 时出错: {e}")
            return False
    
    return False

def test_symbolic_regression_with_real_data():
    """使用真实数据测试符号回归分析"""
    print("🔬 测试符号回归分析（使用真实数据）...")
    
    # 使用Leaf50HDL.csv文件
    csv_file = 'docs/Leaf50HDL.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        return False
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        data = df.to_dict('records')
        
        # 目标变量是HDL，其他所有列都是特征变量
        target_column = 'HDL'
        feature_columns = [col for col in df.columns if col != 'HDL']
        
        # 准备请求数据
        request_data = {
            'data': data,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'population_size': 100,
            'generations': 50,
            'test_ratio': 0.3,
            'operators': ['+', '-', '*', '/']
        }
        
        print(f"🎯 目标变量: {target_column}")
        print(f"📊 特征变量数量: {len(feature_columns)}")
        print(f"📊 特征变量: {feature_columns}")
        
        # 发送请求
        response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', 
                              json=request_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 符号回归分析成功")
                print(f"   - 公式: {result['formula']}")
                print(f"   - R² (测试): {result['metrics']['r2_test']:.3f}")
                print(f"   - MSE (测试): {result['metrics']['mse_test']:.3f}")
                print(f"   - 特征重要性数量: {len(result['feature_importance'])}")
                
                # 显示前5个最重要的特征
                sorted_features = sorted(result['feature_importance'].items(), 
                                      key=lambda x: x[1], reverse=True)[:5]
                print("   - 前5个重要特征:")
                for feature, importance in sorted_features:
                    print(f"     * {feature}: {importance:.3f}")
                
                return True
            else:
                print(f"❌ 符号回归分析失败: {result['error']}")
                return False
        else:
            print(f"❌ 符号回归分析请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 符号回归分析出错: {e}")
        return False

def test_monte_carlo_analysis_with_real_data():
    """使用真实数据测试蒙特卡罗分析"""
    print("🎲 测试蒙特卡罗分析（使用真实数据）...")
    
    # 使用Leaf100HDL.csv文件
    csv_file = 'docs/Leaf100HDL.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV文件不存在: {csv_file}")
        return False
    
    try:
        # 读取CSV文件
        df = pd.read_csv(csv_file)
        data = df.to_dict('records')
        
        # 目标变量是HDL，其他所有列都是特征变量
        target_column = 'HDL'
        feature_columns = [col for col in df.columns if col != 'HDL']
        
        # 准备请求数据
        request_data = {
            'data': data,
            'target_column': target_column,
            'feature_columns': feature_columns,
            'iterations': 1000
        }
        
        print(f"🎯 目标变量: {target_column}")
        print(f"📊 特征变量数量: {len(feature_columns)}")
        print(f"🔄 迭代次数: {request_data['iterations']}")
        
        # 发送请求
        response = requests.post('http://127.0.0.1:5000/api/monte-carlo/analysis', 
                              json=request_data, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            if result['success']:
                print("✅ 蒙特卡罗分析成功")
                print(f"   - 结果ID: {result['result_id']}")
                print(f"   - 目标变量统计:")
                stats = result['target_statistics']
                print(f"     * 均值: {stats['mean']:.3f}")
                print(f"     * 标准差: {stats['std']:.3f}")
                print(f"     * 最小值: {stats['min']:.3f}")
                print(f"     * 最大值: {stats['max']:.3f}")
                
                print(f"   - 特征重要性数量: {len(result['feature_importance'])}")
                
                # 显示前5个最重要的特征
                sorted_features = sorted(result['feature_importance'].items(), 
                                      key=lambda x: x[1], reverse=True)[:5]
                print("   - 前5个重要特征:")
                for feature, importance in sorted_features:
                    print(f"     * {feature}: {importance:.3f}")
                
                return True
            else:
                print(f"❌ 蒙特卡罗分析失败: {result['error']}")
                return False
        else:
            print(f"❌ 蒙特卡罗分析请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 蒙特卡罗分析出错: {e}")
        return False

def test_error_handling():
    """测试错误处理"""
    print("⚠️  测试错误处理...")
    
    # 测试无效数据
    invalid_data = {
        'data': [],
        'target_column': 'HDL',
        'feature_columns': ['QA', 'NCGA']
    }
    
    response = requests.post('http://127.0.0.1:5000/api/regression/symbolic-regression', 
                          json=invalid_data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if not result['success']:
            print("✅ 错误处理正常 - 空数据被正确拒绝")
            return True
        else:
            print("❌ 错误处理异常 - 空数据应该被拒绝")
            return False
    else:
        print(f"❌ 错误处理请求失败: {response.status_code}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始前端模拟测试")
    print("=" * 50)
    
    # 测试后端健康状态
    if not test_backend_health():
        print("❌ 后端服务不可用，停止测试")
        return False
    
    print("\n" + "=" * 50)
    
    # 测试数据上传
    if not test_data_upload_with_real_csv():
        print("❌ 数据上传测试失败")
        return False
    
    print("\n" + "=" * 50)
    
    # 测试符号回归分析
    if not test_symbolic_regression_with_real_data():
        print("❌ 符号回归分析测试失败")
        return False
    
    print("\n" + "=" * 50)
    
    # 测试蒙特卡罗分析
    if not test_monte_carlo_analysis_with_real_data():
        print("❌ 蒙特卡罗分析测试失败")
        return False
    
    print("\n" + "=" * 50)
    
    # 测试错误处理
    if not test_error_handling():
        print("❌ 错误处理测试失败")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过！")
    print("✅ 前后端API通信正常")
    print("✅ 使用真实CSV文件测试成功")
    print("✅ Mock数据返回正常")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 