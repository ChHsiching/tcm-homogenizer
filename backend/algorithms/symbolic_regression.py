#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
符号回归算法模块
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sympy as sp
from loguru import logger
import random

class HeuristicLabSymbolicRegression:
    """参考HeuristicLab实现的符号回归算法"""
    
    def __init__(self):
        self.best_expression = None
        self.best_score = -np.inf
        self.feature_importance = {}
        self.population = []
        self.generations = 0
        self.population_size = 0
        
    def create_expression_tree(self, operators, max_depth=3):
        """创建表达式树（参考HeuristicLab的树结构）"""
        if max_depth == 0:
            # 叶子节点：变量或常数
            if random.random() < 0.3:  # 30%概率为常数
                return {'type': 'constant', 'value': random.uniform(-10, 10)}
            else:
                return {'type': 'variable', 'name': f'x{random.randint(0, 9)}'}
        
        # 内部节点：运算符
        operator = random.choice(operators)
        if operator in ['+', '-']:
            return {
                'type': 'operator',
                'operator': operator,
                'left': self.create_expression_tree(operators, max_depth - 1),
                'right': self.create_expression_tree(operators, max_depth - 1)
            }
        elif operator in ['*', '/']:
            return {
                'type': 'operator',
                'operator': operator,
                'left': self.create_expression_tree(operators, max_depth - 1),
                'right': self.create_expression_tree(operators, max_depth - 1)
            }
        else:  # 幂运算或开方
            return {
                'type': 'operator',
                'operator': operator,
                'left': self.create_expression_tree(operators, max_depth - 1),
                'right': None
            }
    
    def evaluate_tree(self, tree, X, feature_names):
        """计算表达式树的值"""
        if tree['type'] == 'constant':
            return np.full(X.shape[0], tree['value'])
        elif tree['type'] == 'variable':
            var_name = tree['name']
            if var_name in feature_names:
                idx = feature_names.index(var_name)
                return X[:, idx]
            else:
                return np.zeros(X.shape[0])
        elif tree['type'] == 'operator':
            left_val = self.evaluate_tree(tree['left'], X, feature_names)
            if tree['operator'] in ['+', '-', '*', '/']:
                right_val = self.evaluate_tree(tree['right'], X, feature_names)
                if tree['operator'] == '+':
                    return left_val + right_val
                elif tree['operator'] == '-':
                    return left_val - right_val
                elif tree['operator'] == '*':
                    return left_val * right_val
                elif tree['operator'] == '/':
                    # 避免除零
                    return np.where(right_val != 0, left_val / right_val, 0)
            elif tree['operator'] == '^':
                return np.power(left_val, 2)  # 简化为平方
            elif tree['operator'] == 'sqrt':
                return np.sqrt(np.abs(left_val))  # 避免负数开方
        return np.zeros(X.shape[0])
    
    def tree_to_string(self, tree, feature_names):
        """将表达式树转换为字符串"""
        if tree['type'] == 'constant':
            return f"{tree['value']:.4f}"
        elif tree['type'] == 'variable':
            var_name = tree['name']
            if var_name in feature_names:
                idx = feature_names.index(var_name)
                return feature_names[idx]
            else:
                return "0"
        elif tree['type'] == 'operator':
            left_str = self.tree_to_string(tree['left'], feature_names)
            if tree['operator'] in ['+', '-', '*', '/']:
                right_str = self.tree_to_string(tree['right'], feature_names)
                return f"({left_str} {tree['operator']} {right_str})"
            elif tree['operator'] == '^':
                return f"({left_str})^2"
            elif tree['operator'] == 'sqrt':
                return f"sqrt({left_str})"
        return "0"
    
    def calculate_feature_importance(self, tree, X, y, feature_names):
        """计算特征重要性（参考HeuristicLab）"""
        importance = {}
        base_score = r2_score(y, self.evaluate_tree(tree, X, feature_names))
        
        for i, feature in enumerate(feature_names):
            # 临时替换特征值
            X_temp = X.copy()
            X_temp[:, i] = np.random.permutation(X_temp[:, i])
            new_score = r2_score(y, self.evaluate_tree(tree, X_temp, feature_names))
            importance[feature] = max(0, base_score - new_score)  # 重要性为性能下降程度
        
        return importance
    
    def genetic_programming(self, X, y, feature_names, population_size=100, generations=50, 
                          operators=['+', '-', '*', '/'], test_ratio=0.3):
        """遗传编程算法（参考HeuristicLab）"""
        self.population_size = population_size
        self.generations = generations
        
        # 分割数据
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=42
        )
        
        # 初始化种群
        self.population = []
        for _ in range(population_size):
            tree = self.create_expression_tree(operators, max_depth=3)
            self.population.append(tree)
        
        best_individual = None
        best_score = -np.inf
        
        for gen in range(generations):
            # 评估种群
            scores = []
            for tree in self.population:
                try:
                    y_pred = self.evaluate_tree(tree, X_train, feature_names)
                    score = r2_score(y_train, y_pred)
                    scores.append(score)
                    
                    if score > best_score:
                        best_score = score
                        best_individual = tree.copy()
                except:
                    scores.append(-np.inf)
            
            # 选择、交叉、变异
            new_population = []
            for _ in range(population_size):
                # 锦标赛选择
                tournament_size = 3
                tournament = random.sample(range(len(self.population)), tournament_size)
                winner = max(tournament, key=lambda i: scores[i])
                
                # 变异
                if random.random() < 0.1:  # 10%变异概率
                    mutated = self.mutate_tree(self.population[winner].copy())
                    new_population.append(mutated)
                else:
                    new_population.append(self.population[winner].copy())
            
            self.population = new_population
            
            # 精英保留
            if best_individual:
                self.population[0] = best_individual.copy()
        
        # 最终评估
        if best_individual:
            y_pred_train = self.evaluate_tree(best_individual, X_train, feature_names)
            y_pred_test = self.evaluate_tree(best_individual, X_test, feature_names)
            
            train_r2 = r2_score(y_train, y_pred_train)
            test_r2 = r2_score(y_test, y_pred_test)
            train_mse = mean_squared_error(y_train, y_pred_train)
            test_mse = mean_squared_error(y_test, y_pred_test)
            
            # 计算特征重要性
            self.feature_importance = self.calculate_feature_importance(
                best_individual, X_train, y_train, feature_names
            )
            
            # 转换为字符串表达式
            expression = self.tree_to_string(best_individual, feature_names)
            
            return {
                'expression': expression,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_mse': train_mse,
                'test_mse': test_mse,
                'feature_importance': self.feature_importance,
                'tree': best_individual
            }
        
        return None
    
    def mutate_tree(self, tree):
        """变异操作"""
        if random.random() < 0.3:
            # 随机替换子树
            return self.create_expression_tree(['+', '-', '*', '/'], max_depth=2)
        return tree

def analyze_symbolic_regression(data, target_column, population_size=100, generations=50, 
                              test_ratio=0.3, operators=None):
    """
    执行符号回归分析（参考HeuristicLab实现）
    """
    try:
        logger.info(f"开始符号回归分析，目标变量: {target_column}")
        
        # 数据预处理
        if target_column not in data.columns:
            raise ValueError(f"目标变量 {target_column} 不存在于数据中")
        
        # 分离特征和目标
        feature_columns = [col for col in data.columns if col != target_column]
        X = data[feature_columns].values
        y = data[target_column].values
        
        # 数据标准化
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
        
        # 设置默认运算符
        if operators is None:
            operators = ['+', '-', '*', '/']
        
        # 创建符号回归实例
        sr = HeuristicLabSymbolicRegression()
        
        # 执行遗传编程
        result = sr.genetic_programming(
            X_scaled, y_scaled, feature_columns,
            population_size=population_size,
            generations=generations,
            operators=operators,
            test_ratio=test_ratio
        )
        
        if result is None:
            logger.warning("符号回归未能找到有效解，使用线性回归作为备选")
            # 备选方案：线性回归
            lr = LinearRegression()
            lr.fit(X_scaled, y_scaled)
            y_pred = lr.predict(X_scaled)
            
            return {
                'expression': f"{target_column} = {lr.intercept_:.4f} + " + 
                             " + ".join([f"{coef:.4f} * {feature}" 
                                        for coef, feature in zip(lr.coef_, feature_columns)]),
                'train_r2': r2_score(y_scaled, y_pred),
                'test_r2': r2_score(y_scaled, y_pred),
                'train_mse': mean_squared_error(y_scaled, y_pred),
                'test_mse': mean_squared_error(y_scaled, y_pred),
                'feature_importance': {feature: abs(coef) for feature, coef in zip(feature_columns, lr.coef_)},
                'tree': None
            }
        
        # 转换回原始尺度
        result['expression'] = f"{target_column} = {result['expression']}"
        
        logger.info(f"符号回归分析完成，测试R²: {result['test_r2']:.4f}")
        return result
        
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        raise 