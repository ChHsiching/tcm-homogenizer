#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
符号回归算法模块
参考HeuristicLab的遗传编程实现
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import sympy as sp
from sympy import symbols, Add, Mul, Pow, Symbol
import random
import copy
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class HeuristicLabSymbolicRegression:
    """参考HeuristicLab的符号回归实现"""
    
    def __init__(self, population_size=100, generations=50, operators=None, 
                 max_depth=6, tournament_size=3, crossover_rate=0.9, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.operators = operators or ['add', 'sub', 'mul', 'div']
        self.max_depth = max_depth
        self.tournament_size = tournament_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
        # 符号变量
        self.variables = []
        self.best_individual = None
        self.best_fitness = float('inf')
        
    def create_individual(self, depth=0):
        """创建个体（表达式树）"""
        if depth >= self.max_depth or random.random() < 0.3:
            # 叶子节点：变量或常数
            if random.random() < 0.7 and self.variables:
                return {'type': 'variable', 'value': random.choice(self.variables)}
            else:
                return {'type': 'constant', 'value': random.uniform(-10, 10)}
        
        # 内部节点：运算符
        operator = random.choice(self.operators)
        if operator in ['add', 'sub']:
            return {
                'type': 'operator',
                'operator': operator,
                'left': self.create_individual(depth + 1),
                'right': self.create_individual(depth + 1)
            }
        elif operator in ['mul', 'div']:
            return {
                'type': 'operator',
                'operator': operator,
                'left': self.create_individual(depth + 1),
                'right': self.create_individual(depth + 1)
            }
    
    def evaluate_individual(self, individual, X, y):
        """评估个体适应度"""
        try:
            # 将表达式树转换为可执行的Python代码
            code = self.tree_to_code(individual)
            
            # 创建变量映射
            var_dict = {}
            for i, var in enumerate(self.variables):
                var_dict[var] = X[:, i]
            
            # 执行表达式
            local_dict = var_dict.copy()
            exec(code, {}, local_dict)
            predictions = local_dict['result']
            
            # 计算适应度（MSE）
            mse = mean_squared_error(y, predictions)
            return mse, predictions
            
        except Exception as e:
            logger.warning(f"Individual evaluation failed: {e}")
            return float('inf'), np.zeros_like(y)
    
    def tree_to_code(self, tree):
        """将表达式树转换为Python代码"""
        if tree['type'] == 'constant':
            return str(tree['value'])
        elif tree['type'] == 'variable':
            return tree['value']
        elif tree['type'] == 'operator':
            left_code = self.tree_to_code(tree['left'])
            right_code = self.tree_to_code(tree['right'])
            
            if tree['operator'] == 'add':
                return f"({left_code} + {right_code})"
            elif tree['operator'] == 'sub':
                return f"({left_code} - {right_code})"
            elif tree['operator'] == 'mul':
                return f"({left_code} * {right_code})"
            elif tree['operator'] == 'div':
                return f"({left_code} / ({right_code} + 1e-8))"  # 避免除零
    
    def tournament_selection(self, population, fitnesses):
        """锦标赛选择"""
        tournament = random.sample(list(enumerate(population)), self.tournament_size)
        tournament_fitnesses = [fitnesses[i] for i, _ in tournament]
        winner_idx = tournament[np.argmin(tournament_fitnesses)][0]
        return population[winner_idx]
    
    def crossover(self, parent1, parent2):
        """交叉操作"""
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        # 深拷贝
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # 随机选择交叉点
        def get_random_node(tree, depth=0):
            if depth >= 3:  # 限制深度
                return None
            if tree['type'] == 'operator':
                if random.random() < 0.3:
                    return tree
                else:
                    left = get_random_node(tree['left'], depth + 1)
                    if left:
                        return left
                    return get_random_node(tree['right'], depth + 1)
            return None
        
        node1 = get_random_node(child1)
        node2 = get_random_node(child2)
        
        if node1 and node2:
            # 交换子树
            node1, node2 = node2, node1
        
        return child1, child2
    
    def mutation(self, individual):
        """变异操作"""
        if random.random() > self.mutation_rate:
            return individual
        
        mutated = copy.deepcopy(individual)
        
        def mutate_node(tree, depth=0):
            if depth >= 3:
                return
            
            if random.random() < 0.1:  # 10%概率变异
                if tree['type'] == 'operator':
                    tree['operator'] = random.choice(self.operators)
                elif tree['type'] == 'variable':
                    if self.variables:
                        tree['value'] = random.choice(self.variables)
                elif tree['type'] == 'constant':
                    tree['value'] = random.uniform(-10, 10)
            
            if tree['type'] == 'operator':
                mutate_node(tree['left'], depth + 1)
                mutate_node(tree['right'], depth + 1)
        
        mutate_node(mutated)
        return mutated
    
    def fit(self, X, y, test_ratio=0.3):
        """训练符号回归模型"""
        # 设置变量名
        self.variables = [f'x{i}' for i in range(X.shape[1])]
        
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=42
        )
        
        # 初始化种群
        population = [self.create_individual() for _ in range(self.population_size)]
        
        # 进化过程
        for generation in range(self.generations):
            # 评估种群
            fitnesses = []
            predictions_list = []
            
            for individual in population:
                fitness, predictions = self.evaluate_individual(individual, X_train, y_train)
                fitnesses.append(fitness)
                predictions_list.append(predictions)
            
            # 更新最佳个体
            best_idx = np.argmin(fitnesses)
            if fitnesses[best_idx] < self.best_fitness:
                self.best_fitness = fitnesses[best_idx]
                self.best_individual = copy.deepcopy(population[best_idx])
            
            # 创建新种群
            new_population = []
            
            # 精英保留
            elite_size = max(1, self.population_size // 10)
            elite_indices = np.argsort(fitnesses)[:elite_size]
            new_population.extend([population[i] for i in elite_indices])
            
            # 生成新个体
            while len(new_population) < self.population_size:
                # 选择父代
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                
                # 交叉
                child1, child2 = self.crossover(parent1, parent2)
                
                # 变异
                child1 = self.mutation(child1)
                child2 = self.mutation(child2)
                
                new_population.extend([child1, child2])
            
            # 确保种群大小
            population = new_population[:self.population_size]
            
            if generation % 10 == 0:
                logger.info(f"Generation {generation}, Best fitness: {self.best_fitness:.6f}")
        
        # 最终评估
        if self.best_individual:
            train_fitness, train_pred = self.evaluate_individual(self.best_individual, X_train, y_train)
            test_fitness, test_pred = self.evaluate_individual(self.best_individual, X_test, y_test)
            
            # 计算指标
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            train_mse = mean_squared_error(y_train, train_pred)
            test_mse = mean_squared_error(y_test, test_pred)
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            
            # 生成表达式字符串
            expression = self.tree_to_expression(self.best_individual)
            
            # 计算特征重要性
            feature_importance = self.calculate_feature_importance(self.best_individual)
            
            return {
                'expression': expression,
                'train_r2': train_r2,
                'test_r2': test_r2,
                'train_mse': train_mse,
                'test_mse': test_mse,
                'train_mae': train_mae,
                'test_mae': test_mae,
                'feature_importance': feature_importance,
                'tree_structure': self.best_individual
            }
        
        return None
    
    def tree_to_expression(self, tree):
        """将表达式树转换为字符串"""
        if tree['type'] == 'constant':
            return str(tree['value'])
        elif tree['type'] == 'variable':
            return tree['value']
        elif tree['type'] == 'operator':
            left = self.tree_to_expression(tree['left'])
            right = self.tree_to_expression(tree['right'])
            
            if tree['operator'] == 'add':
                return f"{left} + {right}"
            elif tree['operator'] == 'sub':
                return f"{left} - {right}"
            elif tree['operator'] == 'mul':
                return f"{left} * {right}"
            elif tree['operator'] == 'div':
                return f"{left} / {right}"
    
    def calculate_feature_importance(self, tree):
        """计算特征重要性"""
        importance = {}
        
        def count_variables(node):
            if node['type'] == 'variable':
                var = node['value']
                importance[var] = importance.get(var, 0) + 1
            elif node['type'] == 'operator':
                count_variables(node['left'])
                count_variables(node['right'])
        
        count_variables(tree)
        
        # 归一化重要性
        total = sum(importance.values())
        if total > 0:
            importance = {k: v / total for k, v in importance.items()}
        
        return importance

def analyze_symbolic_regression(data, target_column, feature_columns, test_ratio=0.3, 
                              population_size=100, generations=50, operators=None):
    """
    符号回归分析主函数
    参考HeuristicLab实现
    """
    try:
        logger.info("Starting HeuristicLab-style symbolic regression analysis")
        
        # 数据预处理
        X = data[feature_columns].values
        y = data[target_column].values
        
        # 数据标准化
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # 创建符号回归模型
        model = HeuristicLabSymbolicRegression(
            population_size=population_size,
            generations=generations,
            operators=operators or ['add', 'sub', 'mul', 'div']
        )
        
        # 训练模型
        result = model.fit(X_scaled, y, test_ratio=test_ratio)
        
        if result:
            logger.info(f"Symbolic regression completed. Best expression: {result['expression']}")
            return result
        else:
            logger.error("Symbolic regression failed to find a valid solution")
            return None
            
    except Exception as e:
        logger.error(f"Symbolic regression analysis failed: {e}")
        return None 