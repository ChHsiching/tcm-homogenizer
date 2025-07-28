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
import math

class HeuristicLabSymbolicRegression:
    """参考HeuristicLab实现的符号回归算法"""
    
    def __init__(self, population_size=100, generations=50, operators=None, test_ratio=0.3):
        self.population_size = population_size
        self.generations = generations
        self.operators = operators or ['+', '-', '*', '/']
        self.test_ratio = test_ratio
        self.best_individual = None
        self.best_fitness = float('inf')
        self.feature_names = None
        self.target_name = None
        
    def create_expression_tree(self, max_depth=6):
        """创建表达式树（参考HeuristicLab的树结构）"""
        if max_depth <= 1:
            # 叶子节点：变量或常数
            if random.random() < 0.3:  # 30%概率是常数
                return {'type': 'constant', 'value': random.uniform(-10, 10)}
            else:
                return {'type': 'variable', 'name': random.choice(self.feature_names)}
        
        # 内部节点：运算符
        operator = random.choice(self.operators)
        if operator in ['+', '-']:
            # 加减法可以有多个子节点
            num_children = random.randint(2, 4)
            children = [self.create_expression_tree(max_depth - 1) for _ in range(num_children)]
        else:
            # 乘除法只有两个子节点
            children = [self.create_expression_tree(max_depth - 1) for _ in range(2)]
            
        return {
            'type': 'operator',
            'operator': operator,
            'children': children
        }
    
    def evaluate_tree(self, tree, X):
        """计算表达式树的值"""
        if tree['type'] == 'constant':
            return np.full(X.shape[0], tree['value'])
        elif tree['type'] == 'variable':
            var_idx = self.feature_names.index(tree['name'])
            return X[:, var_idx]
        else:
            # 运算符节点
            children_values = [self.evaluate_tree(child, X) for child in tree['children']]
            
            if tree['operator'] == '+':
                result = children_values[0]
                for child_val in children_values[1:]:
                    result += child_val
                return result
            elif tree['operator'] == '-':
                result = children_values[0]
                for child_val in children_values[1:]:
                    result -= child_val
                return result
            elif tree['operator'] == '*':
                result = children_values[0]
                for child_val in children_values[1:]:
                    result *= child_val
                return result
            elif tree['operator'] == '/':
                result = children_values[0]
                for child_val in children_values[1:]:
                    # 避免除零
                    result = np.where(child_val != 0, result / child_val, result)
                return result
    
    def tree_to_expression(self, tree):
        """将表达式树转换为字符串表达式"""
        if tree['type'] == 'constant':
            return str(tree['value'])
        elif tree['type'] == 'variable':
            return tree['name']
        else:
            children_expr = [self.tree_to_expression(child) for child in tree['children']]
            if tree['operator'] == '+':
                return ' + '.join(children_expr)
            elif tree['operator'] == '-':
                return ' - '.join(children_expr)
            elif tree['operator'] == '*':
                return ' * '.join(children_expr)
            elif tree['operator'] == '/':
                return ' / '.join(children_expr)
    
    def calculate_fitness(self, tree, X_train, y_train, X_test, y_test):
        """计算适应度（MSE）"""
        try:
            y_pred_train = self.evaluate_tree(tree, X_train)
            y_pred_test = self.evaluate_tree(tree, X_test)
            
            # 计算训练和测试误差
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            
            # 综合适应度（参考HeuristicLab）
            fitness = mse_test + 0.1 * mse_train + 0.01 * self.tree_complexity(tree)
            
            return fitness, mse_train, mse_test
        except:
            return float('inf'), float('inf'), float('inf')
    
    def tree_complexity(self, tree):
        """计算树的复杂度（用于正则化）"""
        if tree['type'] in ['constant', 'variable']:
            return 1
        else:
            return 1 + sum(self.tree_complexity(child) for child in tree['children'])
    
    def crossover(self, parent1, parent2):
        """交叉操作"""
        if random.random() < 0.5:
            return parent1.copy()
        else:
            return parent2.copy()
    
    def mutation(self, tree, mutation_rate=0.1):
        """变异操作"""
        if random.random() > mutation_rate:
            return tree
            
        # 随机选择一个节点进行变异
        if tree['type'] in ['constant', 'variable']:
            if random.random() < 0.5:
                return {'type': 'constant', 'value': random.uniform(-10, 10)}
            else:
                return {'type': 'variable', 'name': random.choice(self.feature_names)}
        else:
            # 变异运算符
            new_operator = random.choice(self.operators)
            return {
                'type': 'operator',
                'operator': new_operator,
                'children': tree['children']
            }
    
    def fit(self, X, y, feature_names):
        """训练符号回归模型"""
        self.feature_names = feature_names
        self.target_name = 'target'
        
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_ratio, random_state=42
        )
        
        # 初始化种群
        population = [self.create_expression_tree() for _ in range(self.population_size)]
        
        logger.info(f"开始符号回归训练，种群大小: {self.population_size}, 代数: {self.generations}")
        
        for generation in range(self.generations):
            # 计算适应度
            fitness_scores = []
            for individual in population:
                fitness, mse_train, mse_test = self.calculate_fitness(
                    individual, X_train, y_train, X_test, y_test
                )
                fitness_scores.append((fitness, individual, mse_train, mse_test))
            
            # 排序并更新最佳个体
            fitness_scores.sort(key=lambda x: x[0])
            best_fitness, best_individual, best_mse_train, best_mse_test = fitness_scores[0]
            
            if best_fitness < self.best_fitness:
                self.best_fitness = best_fitness
                self.best_individual = best_individual
                logger.info(f"第{generation+1}代发现更优解，适应度: {best_fitness:.6f}")
            
            # 选择、交叉、变异
            new_population = []
            elite_size = max(1, self.population_size // 10)  # 保留10%精英
            
            # 精英保留
            for i in range(elite_size):
                new_population.append(fitness_scores[i][1])
            
            # 生成新个体
            while len(new_population) < self.population_size:
                # 锦标赛选择
                tournament_size = 3
                parent1 = min(random.sample(fitness_scores, tournament_size), key=lambda x: x[0])[1]
                parent2 = min(random.sample(fitness_scores, tournament_size), key=lambda x: x[0])[1]
                
                # 交叉
                child = self.crossover(parent1, parent2)
                
                # 变异
                child = self.mutation(child)
                
                new_population.append(child)
            
            population = new_population
            
            if (generation + 1) % 10 == 0:
                logger.info(f"第{generation+1}代完成，最佳适应度: {best_fitness:.6f}")
        
        # 最终评估
        if self.best_individual:
            y_pred_train = self.evaluate_tree(self.best_individual, X_train)
            y_pred_test = self.evaluate_tree(self.best_individual, X_test)
            
            r2_train = r2_score(y_train, y_pred_train)
            r2_test = r2_score(y_test, y_pred_test)
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            mae_train = mean_absolute_error(y_train, y_pred_train)
            mae_test = mean_absolute_error(y_test, y_pred_test)
            
            expression = self.tree_to_expression(self.best_individual)
            
            return {
                'expression': expression,
                'tree': self.best_individual,
                'r2_train': r2_train,
                'r2_test': r2_test,
                'mse_train': mse_train,
                'mse_test': mse_test,
                'mae_train': mae_train,
                'mae_test': mae_test,
                'rmse_train': math.sqrt(mse_train),
                'rmse_test': math.sqrt(mse_test),
                'fitness': self.best_fitness
            }
        
        return None

def perform_symbolic_regression_gplearn(data, target_column, population_size=100, generations=50, 
                                      operators=None, test_ratio=0.3):
    """
    使用参考HeuristicLab的算法进行符号回归
    """
    try:
        # 数据预处理
        X = data.drop(columns=[target_column]).values
        y = data[target_column].values
        feature_names = data.drop(columns=[target_column]).columns.tolist()
        
        # 检查数据一致性
        if len(X) != len(y):
            raise ValueError(f"特征数据长度({len(X)})与目标数据长度({len(y)})不匹配")
        
        if len(X) == 0:
            raise ValueError("数据为空，无法进行分析")
        
        # 检查特征数量
        if len(feature_names) == 0:
            raise ValueError("没有可用的特征变量")
        
        # 数据标准化
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # 创建符号回归模型
        model = HeuristicLabSymbolicRegression(
            population_size=population_size,
            generations=generations,
            operators=operators,
            test_ratio=test_ratio
        )
        
        # 训练模型
        result = model.fit(X_scaled, y, feature_names)
        
        if result:
            # 计算特征重要性（基于树结构）
            feature_importance = calculate_feature_importance(result['tree'], feature_names)
            
            return {
                'success': True,
                'expression': result['expression'],
                'tree': result['tree'],
                'feature_importance': feature_importance,
                'metrics': {
                    'r2_train': result['r2_train'],
                    'r2_test': result['r2_test'],
                    'mse_train': result['mse_train'],
                    'mse_test': result['mse_test'],
                    'mae_train': result['mae_train'],
                    'mae_test': result['mae_test'],
                    'rmse_train': result['rmse_train'],
                    'rmse_test': result['rmse_test']
                }
            }
        else:
            return {'success': False, 'error': '无法找到有效解'}
            
    except Exception as e:
        logger.error(f"符号回归失败: {str(e)}")
        return {'success': False, 'error': str(e)}

def calculate_feature_importance(tree, feature_names):
    """计算特征重要性（基于在树中的出现频率）"""
    importance = {name: 0.0 for name in feature_names}
    
    def count_features(node):
        if node['type'] == 'variable':
            if node['name'] in importance:
                importance[node['name']] += 1.0
        elif node['type'] == 'operator':
            for child in node['children']:
                count_features(child)
    
    count_features(tree)
    
    # 归一化重要性
    total = sum(importance.values())
    if total > 0:
        importance = {k: v/total for k, v in importance.items()}
    
    return importance 