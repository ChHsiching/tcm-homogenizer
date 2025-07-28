#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
符号回归算法实现
参考HeuristicLab的遗传编程实现
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from loguru import logger
import random
import math
from typing import Dict, List, Tuple, Optional

class SymbolicRegressionEngine:
    """符号回归引擎，参考HeuristicLab实现"""
    
    def __init__(self):
        self.best_expression = None
        self.best_fitness = float('inf')
        self.population = []
        self.generation = 0
        
    def analyze(self, data: pd.DataFrame, target_column: str, feature_columns: List[str],
                population_size: int = 100, generations: int = 50, 
                test_ratio: float = 0.3, operators: List[str] = None) -> Dict:
        """
        执行符号回归分析
        
        Args:
            data: 输入数据
            target_column: 目标列名
            feature_columns: 特征列名列表
            population_size: 种群大小
            generations: 进化代数
            test_ratio: 测试集比例
            operators: 运算符列表 ['add', 'sub', 'mul', 'div']
        """
        try:
            logger.info(f"开始符号回归分析，参数: population_size={population_size}, generations={generations}")
            
            # 数据预处理
            X = data[feature_columns].values
            y = data[target_column].values
            
            # 数据标准化
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # 划分训练集和测试集
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_scaled, test_size=test_ratio, random_state=42
            )
            
            # 设置运算符
            if operators is None:
                operators = ['add', 'sub', 'mul', 'div']
            
            # 初始化种群
            self.population = self._initialize_population(population_size, len(feature_columns), operators)
            
            # 进化过程
            for gen in range(generations):
                self.generation = gen + 1
                logger.info(f"第 {gen + 1} 代进化...")
                
                # 评估适应度
                fitness_scores = []
                for individual in self.population:
                    fitness = self._evaluate_fitness(individual, X_train, y_train, feature_columns)
                    fitness_scores.append(fitness)
                
                # 选择最佳个体
                best_idx = np.argmin(fitness_scores)
                if fitness_scores[best_idx] < self.best_fitness:
                    self.best_fitness = fitness_scores[best_idx]
                    self.best_expression = self.population[best_idx]
                
                # 生成新一代
                new_population = []
                for _ in range(population_size):
                    parent1 = self._tournament_selection(fitness_scores)
                    parent2 = self._tournament_selection(fitness_scores)
                    child = self._crossover(parent1, parent2)
                    child = self._mutation(child, operators)
                    new_population.append(child)
                
                self.population = new_population
            
            # 使用最佳表达式进行预测
            best_expression_str = self._expression_to_string(self.best_expression, feature_columns)
            predictions_train = self._evaluate_expression(self.best_expression, X_train, feature_columns)
            predictions_test = self._evaluate_expression(self.best_expression, X_test, feature_columns)
            
            # 计算性能指标（使用原始数据）
            y_train_orig = scaler_y.inverse_transform(y_train.reshape(-1, 1)).flatten()
            y_test_orig = scaler_y.inverse_transform(y_test.reshape(-1, 1)).flatten()
            pred_train_orig = scaler_y.inverse_transform(predictions_train.reshape(-1, 1)).flatten()
            pred_test_orig = scaler_y.inverse_transform(predictions_test.reshape(-1, 1)).flatten()
            
            r2_train = r2_score(y_train_orig, pred_train_orig)
            r2_test = r2_score(y_test_orig, pred_test_orig)
            mse_train = mean_squared_error(y_train_orig, pred_train_orig)
            mse_test = mean_squared_error(y_test_orig, pred_test_orig)
            mae_train = mean_absolute_error(y_train_orig, pred_train_orig)
            mae_test = mean_absolute_error(y_test_orig, pred_test_orig)
            
            # 计算特征重要性
            feature_importance = self._calculate_feature_importance(self.best_expression, feature_columns)
            
            result = {
                'success': True,
                'expression': best_expression_str,
                'r2_train': r2_train,
                'r2_test': r2_test,
                'mse_train': mse_train,
                'mse_test': mse_test,
                'mae_train': mae_train,
                'mae_test': mae_test,
                'rmse_train': math.sqrt(mse_train),
                'rmse_test': math.sqrt(mse_test),
                'feature_importance': feature_importance,
                'predictions': {
                    'train': pred_train_orig.tolist(),
                    'test': pred_test_orig.tolist()
                },
                'parameters': {
                    'population_size': population_size,
                    'generations': generations,
                    'test_ratio': test_ratio,
                    'operators': operators
                }
            }
            
            logger.info(f"符号回归分析完成，最佳表达式: {best_expression_str}")
            logger.info(f"R² (训练): {r2_train:.4f}, R² (测试): {r2_test:.4f}")
            
            return result
            
        except Exception as e:
            logger.error(f"符号回归分析失败: {str(e)}")
            return {
                'success': False,
                'error': f'符号回归分析失败: {str(e)}'
            }
    
    def _initialize_population(self, size: int, num_features: int, operators: List[str]) -> List:
        """初始化种群"""
        population = []
        for _ in range(size):
            individual = self._create_random_expression(num_features, operators)
            population.append(individual)
        return population
    
    def _create_random_expression(self, num_features: int, operators: List[str]) -> List:
        """创建随机表达式"""
        # 使用树结构表示表达式
        if random.random() < 0.3:  # 30%概率创建简单变量
            return ['var', random.randint(0, num_features - 1)]
        else:  # 70%概率创建复合表达式
            operator = random.choice(operators)
            left = self._create_random_expression(num_features, operators)
            right = self._create_random_expression(num_features, operators)
            return [operator, left, right]
    
    def _evaluate_fitness(self, expression: List, X: np.ndarray, y: np.ndarray, feature_names: List[str]) -> float:
        """评估个体适应度"""
        try:
            predictions = self._evaluate_expression(expression, X, feature_names)
            mse = mean_squared_error(y, predictions)
            # 添加复杂度惩罚
            complexity = self._calculate_complexity(expression)
            return mse + 0.01 * complexity
        except:
            return float('inf')
    
    def _evaluate_expression(self, expression: List, X: np.ndarray, feature_names: List[str]) -> np.ndarray:
        """计算表达式值"""
        if expression[0] == 'var':
            feature_idx = expression[1]
            return X[:, feature_idx]
        else:
            operator = expression[0]
            left = self._evaluate_expression(expression[1], X, feature_names)
            right = self._evaluate_expression(expression[2], X, feature_names)
            
            if operator == 'add':
                return left + right
            elif operator == 'sub':
                return left - right
            elif operator == 'mul':
                return left * right
            elif operator == 'div':
                # 避免除零
                return np.where(right != 0, left / right, 0)
            else:
                return left
    
    def _expression_to_string(self, expression: List, feature_names: List[str]) -> str:
        """将表达式转换为字符串"""
        if expression[0] == 'var':
            return feature_names[expression[1]]
        else:
            operator = expression[0]
            left = self._expression_to_string(expression[1], feature_names)
            right = self._expression_to_string(expression[2], feature_names)
            
            if operator == 'add':
                return f"({left} + {right})"
            elif operator == 'sub':
                return f"({left} - {right})"
            elif operator == 'mul':
                return f"({left} * {right})"
            elif operator == 'div':
                return f"({left} / {right})"
            else:
                return left
    
    def _calculate_complexity(self, expression: List) -> int:
        """计算表达式复杂度"""
        if expression[0] == 'var':
            return 1
        else:
            return 1 + self._calculate_complexity(expression[1]) + self._calculate_complexity(expression[2])
    
    def _tournament_selection(self, fitness_scores: List[float]) -> List:
        """锦标赛选择"""
        tournament_size = 3
        tournament_indices = random.sample(range(len(self.population)), tournament_size)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmin(tournament_fitness)]
        return self.population[winner_idx]
    
    def _crossover(self, parent1: List, parent2: List) -> List:
        """交叉操作"""
        if random.random() < 0.8:  # 80%概率进行交叉
            return self._subtree_crossover(parent1, parent2)
        else:
            return parent1
    
    def _subtree_crossover(self, parent1: List, parent2: List) -> List:
        """子树交叉"""
        # 随机选择交叉点
        crossover_point1 = self._get_random_subtree(parent1)
        crossover_point2 = self._get_random_subtree(parent2)
        
        # 创建新个体
        child = self._copy_expression(parent1)
        self._replace_subtree(child, crossover_point1, crossover_point2)
        
        return child
    
    def _mutation(self, individual: List, operators: List[str]) -> List:
        """变异操作"""
        if random.random() < 0.1:  # 10%概率进行变异
            return self._subtree_mutation(individual, operators)
        else:
            return individual
    
    def _subtree_mutation(self, individual: List, operators: List[str]) -> List:
        """子树变异"""
        # 随机选择变异点
        mutation_point = self._get_random_subtree(individual)
        
        # 创建新的子树
        new_subtree = self._create_random_expression(len(mutation_point), operators)
        
        # 替换子树
        child = self._copy_expression(individual)
        self._replace_subtree(child, mutation_point, new_subtree)
        
        return child
    
    def _get_random_subtree(self, expression: List) -> List:
        """获取随机子树"""
        if expression[0] == 'var':
            return expression
        
        if random.random() < 0.3:  # 30%概率选择当前节点
            return expression
        else:  # 70%概率选择子节点
            child = random.choice([expression[1], expression[2]])
            return self._get_random_subtree(child)
    
    def _copy_expression(self, expression: List) -> List:
        """复制表达式"""
        if expression[0] == 'var':
            return expression.copy()
        else:
            return [expression[0], 
                   self._copy_expression(expression[1]), 
                   self._copy_expression(expression[2])]
    
    def _replace_subtree(self, expression: List, old_subtree: List, new_subtree: List):
        """替换子树"""
        if expression[0] == 'var':
            return
        
        if expression[1] == old_subtree:
            expression[1] = new_subtree
        elif expression[2] == old_subtree:
            expression[2] = new_subtree
        else:
            self._replace_subtree(expression[1], old_subtree, new_subtree)
            self._replace_subtree(expression[2], old_subtree, new_subtree)
    
    def _calculate_feature_importance(self, expression: List, feature_names: List[str]) -> List[Dict]:
        """计算特征重要性"""
        importance = {}
        
        def count_features(expr):
            if expr[0] == 'var':
                feature = feature_names[expr[1]]
                importance[feature] = importance.get(feature, 0) + 1
            else:
                count_features(expr[1])
                count_features(expr[2])
        
        count_features(expression)
        
        # 转换为列表格式
        result = []
        total_usage = sum(importance.values())
        for feature, count in importance.items():
            result.append({
                'feature': feature,
                'importance': count / total_usage if total_usage > 0 else 0,
                'usage_count': count
            })
        
        # 按重要性排序
        result.sort(key=lambda x: x['importance'], reverse=True)
        return result

# 全局实例
symbolic_regression_engine = SymbolicRegressionEngine() 