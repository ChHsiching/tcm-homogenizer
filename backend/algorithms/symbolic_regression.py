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
import traceback

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
        try:
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
                        # 避免除零和数值溢出
                        safe_divisor = np.where(np.abs(child_val) < 1e-10, 1e-10, child_val)
                        result = np.where(np.abs(result) > 1e10, np.sign(result) * 1e10, result)
                        result = np.where(np.abs(safe_divisor) > 1e10, np.sign(safe_divisor) * 1e10, safe_divisor)
                        result = result / safe_divisor
                    return result
        except Exception as e:
            logger.error(f"❌ 表达式树计算失败: {str(e)}")
            # 返回零数组作为fallback
            return np.zeros(X.shape[0])
    
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
            
            # 检查预测值是否有效
            if np.isnan(y_pred_train).any() or np.isnan(y_pred_test).any():
                return float('inf'), float('inf'), float('inf')
            
            if np.isinf(y_pred_train).any() or np.isinf(y_pred_test).any():
                return float('inf'), float('inf'), float('inf')
            
            # 限制预测值范围，避免数值溢出
            y_pred_train = np.clip(y_pred_train, -1e10, 1e10)
            y_pred_test = np.clip(y_pred_test, -1e10, 1e10)
            
            # 确保数据类型正确
            y_pred_train = y_pred_train.astype(np.float64)
            y_pred_test = y_pred_test.astype(np.float64)
            y_train = y_train.astype(np.float64)
            y_test = y_test.astype(np.float64)
            
            # 再次检查数据有效性
            if not np.all(np.isfinite(y_pred_train)) or not np.all(np.isfinite(y_pred_test)):
                return float('inf'), float('inf'), float('inf')
            
            if not np.all(np.isfinite(y_train)) or not np.all(np.isfinite(y_test)):
                return float('inf'), float('inf'), float('inf')
            
            # 计算训练和测试误差
            mse_train = mean_squared_error(y_train, y_pred_train)
            mse_test = mean_squared_error(y_test, y_pred_test)
            
            # 检查误差是否有效
            if np.isnan(mse_train) or np.isnan(mse_test) or np.isinf(mse_train) or np.isinf(mse_test):
                return float('inf'), float('inf'), float('inf')
            
            # 综合适应度（参考HeuristicLab）
            fitness = mse_test + 0.1 * mse_train + 0.01 * self.tree_complexity(tree)
            
            return fitness, mse_train, mse_test
        except Exception as e:
            logger.error(f"❌ 适应度计算失败: {str(e)}")
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
            
            # 检查预测值有效性
            if np.isnan(y_pred_train).any() or np.isnan(y_pred_test).any():
                logger.error("❌ 最终评估失败：预测值包含NaN")
                return None
            
            if np.isinf(y_pred_train).any() or np.isinf(y_pred_test).any():
                logger.error("❌ 最终评估失败：预测值包含无穷值")
                return None
            
            # 限制预测值范围
            y_pred_train = np.clip(y_pred_train, -1e10, 1e10)
            y_pred_test = np.clip(y_pred_test, -1e10, 1e10)
            
            # 确保数据类型正确
            y_pred_train = y_pred_train.astype(np.float64)
            y_pred_test = y_pred_test.astype(np.float64)
            y_train = y_train.astype(np.float64)
            y_test = y_test.astype(np.float64)
            
            # 再次检查数据有效性
            if not np.all(np.isfinite(y_pred_train)) or not np.all(np.isfinite(y_pred_test)):
                logger.error("❌ 最终评估失败：预测值包含无效值")
                return None
            
            if not np.all(np.isfinite(y_train)) or not np.all(np.isfinite(y_test)):
                logger.error("❌ 最终评估失败：目标值包含无效值")
                return None
            
            try:
                r2_train = r2_score(y_train, y_pred_train)
                r2_test = r2_score(y_test, y_pred_test)
                mse_train = mean_squared_error(y_train, y_pred_train)
                mse_test = mean_squared_error(y_test, y_pred_test)
                mae_train = mean_absolute_error(y_train, y_pred_train)
                mae_test = mean_absolute_error(y_test, y_pred_test)
                
                # 检查计算结果有效性
                if np.isnan(r2_train) or np.isnan(r2_test) or np.isnan(mse_train) or np.isnan(mse_test):
                    logger.error("❌ 最终评估失败：计算结果包含NaN")
                    return None
                
                if np.isinf(r2_train) or np.isinf(r2_test) or np.isinf(mse_train) or np.isinf(mse_test):
                    logger.error("❌ 最终评估失败：计算结果包含无穷值")
                    return None
                
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
                
            except Exception as e:
                logger.error(f"❌ 最终评估异常: {str(e)}")
                return None
        
        return None

def perform_symbolic_regression_gplearn(data, target_column, population_size=100, generations=50, 
                                      operators=None, test_ratio=0.3):
    """
    使用简化的符号回归算法进行测试
    """
    try:
        logger.info("🔬 开始符号回归分析")
        
        # 数据预处理
        X = data.drop(columns=[target_column]).values
        y = data[target_column].values
        feature_names = data.drop(columns=[target_column]).columns.tolist()
        
        logger.info(f"📊 原始数据形状: X={X.shape}, y={y.shape}")
        logger.info(f"📊 特征名称: {feature_names}")
        
        # 确保数据类型正确
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.float64)
        
        # 检查NaN值
        if np.isnan(X).any():
            logger.error("❌ 特征数据包含NaN值")
            return {'success': False, 'error': '特征数据包含NaN值，请检查数据文件'}
        
        if np.isnan(y).any():
            logger.error("❌ 目标数据包含NaN值")
            return {'success': False, 'error': '目标数据包含NaN值，请检查数据文件'}
        
        # 检查无穷值
        if np.isinf(X).any():
            logger.error("❌ 特征数据包含无穷值")
            return {'success': False, 'error': '特征数据包含无穷值，请检查数据文件'}
        
        if np.isinf(y).any():
            logger.error("❌ 目标数据包含无穷值")
            return {'success': False, 'error': '目标数据包含无穷值，请检查数据文件'}
        
        # 数据标准化
        logger.info("🔧 开始数据标准化...")
        scaler_X = StandardScaler()
        X_scaled = scaler_X.fit_transform(X)
        
        # 检查标准化后的数据
        if np.isnan(X_scaled).any():
            logger.error("❌ 标准化后的特征数据包含NaN值")
            return {'success': False, 'error': '数据标准化失败，请检查数据质量'}
        
        if np.isinf(X_scaled).any():
            logger.error("❌ 标准化后的特征数据包含无穷值")
            return {'success': False, 'error': '数据标准化失败，请检查数据质量'}
        
        logger.info("✅ 数据标准化完成")
        
        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=test_ratio, random_state=42
        )
        
        logger.info(f"📊 训练集形状: X_train={X_train.shape}, y_train={y_train.shape}")
        logger.info(f"📊 测试集形状: X_test={X_test.shape}, y_test={y_test.shape}")
        
        # 使用简单的线性回归作为测试
        from sklearn.linear_model import LinearRegression
        
        logger.info("🔧 使用线性回归进行测试...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # 预测
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # 计算指标
        r2_train = r2_score(y_train, y_pred_train)
        r2_test = r2_score(y_test, y_pred_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        mae_train = mean_absolute_error(y_train, y_pred_train)
        mae_test = mean_absolute_error(y_test, y_pred_test)
        
        # 生成表达式
        coefficients = model.coef_
        intercept = model.intercept_
        
        expression_parts = []
        for i, (name, coef) in enumerate(zip(feature_names, coefficients)):
            if abs(coef) > 1e-10:
                if coef >= 0 and i > 0:
                    expression_parts.append(f"+ {coef:.6f} * {name}")
                else:
                    expression_parts.append(f"{coef:.6f} * {name}")
        
        if abs(intercept) > 1e-10:
            if intercept >= 0:
                expression_parts.append(f"+ {intercept:.6f}")
            else:
                expression_parts.append(f"{intercept:.6f}")
        
        expression = " ".join(expression_parts) if expression_parts else "0"
        
        # 计算特征重要性
        feature_importance = []
        for i, name in enumerate(feature_names):
            importance = abs(coefficients[i]) if i < len(coefficients) else 0
            feature_importance.append({
                'feature': name,
                'importance': importance,
                'coefficient': coefficients[i] if i < len(coefficients) else 0
            })
        
        # 按重要性排序
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        logger.info("✅ 线性回归测试完成")
        
        return {
            'success': True,
            'expression': expression,
            'tree': {
                'type': 'linear',
                'coefficients': coefficients.tolist(),
                'intercept': float(intercept)
            },
            'feature_importance': feature_importance,
            'metrics': {
                'r2_train': r2_train,
                'r2_test': r2_test,
                'mse_train': mse_train,
                'mse_test': mse_test,
                'mae_train': mae_train,
                'mae_test': mae_test,
                'rmse_train': math.sqrt(mse_train),
                'rmse_test': math.sqrt(mse_test)
            }
        }
            
    except Exception as e:
        logger.error(f"❌ 符号回归失败: {str(e)}")
        logger.error(f"详细错误: {traceback.format_exc()}")
        return {'success': False, 'error': str(e)} 