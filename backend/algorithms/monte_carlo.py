#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒙特卡洛分析算法模块
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from loguru import logger
import json
from pathlib import Path
import time
from .symbolic_regression import SymbolicRegression

class MonteCarloAnalysis:
    """蒙特卡洛配比分析算法实现"""
    
    def __init__(self):
        self.results = {}
        self.results_dir = Path("monte_carlo_results")
        self.results_dir.mkdir(exist_ok=True)
        self.regression_engine = SymbolicRegression()
        self._load_saved_results()
    
    def analyze(self, model_id: str, target_efficacy: float, iterations: int = 10000,
                tolerance: float = 0.1, component_ranges: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
        """
        执行蒙特卡洛配比分析
        
        Args:
            model_id: 回归模型ID
            target_efficacy: 目标药效值
            iterations: 采样次数
            tolerance: 容差范围
            component_ranges: 各成分的范围定义
            
        Returns:
            分析结果字典
        """
        try:
            logger.info(f"开始蒙特卡洛分析，模型ID: {model_id}")
            logger.info(f"目标药效: {target_efficacy}, 采样次数: {iterations}")
            
            # 获取回归模型
            model = self.regression_engine.get_model(model_id)
            if not model:
                raise ValueError(f"模型 {model_id} 不存在")
            
            # 执行蒙特卡洛模拟
            result = self._perform_monte_carlo_simulation(
                model, target_efficacy, iterations, tolerance, component_ranges
            )
            
            # 保存结果
            analysis_id = self._save_result(result)
            
            logger.info(f"蒙特卡洛分析完成，分析ID: {analysis_id}")
            return result
            
        except Exception as e:
            logger.error(f"蒙特卡洛分析失败: {str(e)}")
            raise
    
    def _perform_monte_carlo_simulation(self, model: Dict[str, Any], target_efficacy: float,
                                      iterations: int, tolerance: float,
                                      component_ranges: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
        """执行蒙特卡洛模拟"""
        try:
            logger.info("开始执行蒙特卡洛模拟...")
            
            # 模拟计算时间
            time.sleep(3)
            
            # 获取特征信息
            feature_importance = model['feature_importance']
            n_components = len(feature_importance)
            
            # 如果没有提供成分范围，使用默认范围
            if component_ranges is None:
                component_ranges = {}
                for feature in feature_importance:
                    component_ranges[feature['feature']] = [0.0, 1.0]
            
            # 生成随机样本
            valid_samples = []
            all_samples = []
            
            for i in range(iterations):
                # 生成随机配比
                sample = {}
                for feature in feature_importance:
                    feature_name = feature['feature']
                    if feature_name in component_ranges:
                        min_val, max_val = component_ranges[feature_name]
                        sample[feature_name] = np.random.uniform(min_val, max_val)
                    else:
                        sample[feature_name] = np.random.uniform(0.0, 1.0)
                
                # 计算预测药效（模拟）
                predicted_efficacy = self._predict_efficacy(sample, model)
                
                # 检查是否在目标范围内
                if abs(predicted_efficacy - target_efficacy) <= tolerance:
                    valid_samples.append({
                        'sample': sample,
                        'predicted_efficacy': predicted_efficacy
                    })
                
                all_samples.append({
                    'sample': sample,
                    'predicted_efficacy': predicted_efficacy
                })
            
            # 计算统计信息
            valid_count = len(valid_samples)
            valid_rate = valid_count / iterations
            
            # 计算各成分的分布统计
            component_stats = self._calculate_component_statistics(valid_samples, feature_importance)
            
            # 生成分布数据
            distribution_data = self._generate_distribution_data(all_samples)
            
            result = {
                'analysis_id': f"mc_{int(time.time())}",
                'model_id': model.get('model_id'),
                'target_efficacy': target_efficacy,
                'tolerance': tolerance,
                'iterations': iterations,
                'valid_samples_count': valid_count,
                'valid_rate': valid_rate,
                'component_statistics': component_stats,
                'distribution_data': distribution_data,
                'sample_data': {
                    'valid_samples': valid_samples[:100],  # 只保存前100个有效样本
                    'all_samples_summary': {
                        'min_efficacy': min(s['predicted_efficacy'] for s in all_samples),
                        'max_efficacy': max(s['predicted_efficacy'] for s in all_samples),
                        'mean_efficacy': np.mean([s['predicted_efficacy'] for s in all_samples]),
                        'std_efficacy': np.std([s['predicted_efficacy'] for s in all_samples])
                    }
                },
                'timestamp': time.time()
            }
            
            logger.info(f"蒙特卡洛模拟完成，有效样本数: {valid_count}, 有效率: {valid_rate:.2%}")
            return result
            
        except Exception as e:
            logger.error(f"蒙特卡洛模拟执行失败: {str(e)}")
            raise
    
    def _predict_efficacy(self, sample: Dict[str, float], model: Dict[str, Any]) -> float:
        """预测药效值（模拟实现）"""
        try:
            # 这里应该使用真实的模型进行预测
            # 目前使用简单的线性组合作为示例
            
            feature_importance = model['feature_importance']
            total_contribution = 0.0
            total_weight = 0.0
            
            for feature in feature_importance:
                feature_name = feature['feature']
                importance = feature['importance']
                
                if feature_name in sample:
                    contribution = sample[feature_name] * importance
                    total_contribution += contribution
                    total_weight += importance
            
            # 归一化
            if total_weight > 0:
                predicted = total_contribution / total_weight
            else:
                predicted = 0.0
            
            # 添加一些随机噪声
            noise = np.random.normal(0, 0.05)
            predicted += noise
            
            return max(0.0, min(1.0, predicted))  # 限制在[0,1]范围内
            
        except Exception as e:
            logger.error(f"药效预测失败: {str(e)}")
            return 0.0
    
    def _calculate_component_statistics(self, valid_samples: List[Dict], 
                                      feature_importance: List[Dict]) -> Dict[str, Dict]:
        """计算各成分的统计信息"""
        try:
            component_stats = {}
            
            for feature in feature_importance:
                feature_name = feature['feature']
                values = [sample['sample'][feature_name] for sample in valid_samples]
                
                if values:
                    component_stats[feature_name] = {
                        'min': float(np.min(values)),
                        'max': float(np.max(values)),
                        'mean': float(np.mean(values)),
                        'std': float(np.std(values)),
                        'median': float(np.median(values)),
                        'q25': float(np.percentile(values, 25)),
                        'q75': float(np.percentile(values, 75))
                    }
                else:
                    component_stats[feature_name] = {
                        'min': 0.0, 'max': 0.0, 'mean': 0.0, 'std': 0.0,
                        'median': 0.0, 'q25': 0.0, 'q75': 0.0
                    }
            
            return component_stats
            
        except Exception as e:
            logger.error(f"计算成分统计信息失败: {str(e)}")
            return {}
    
    def _generate_distribution_data(self, all_samples: List[Dict]) -> Dict[str, Any]:
        """生成分布数据"""
        try:
            efficacies = [sample['predicted_efficacy'] for sample in all_samples]
            
            # 创建直方图数据
            hist, bins = np.histogram(efficacies, bins=50, range=(0, 1))
            
            return {
                'efficacies': efficacies,
                'histogram': {
                    'counts': hist.tolist(),
                    'bins': bins.tolist()
                },
                'statistics': {
                    'min': float(np.min(efficacies)),
                    'max': float(np.max(efficacies)),
                    'mean': float(np.mean(efficacies)),
                    'std': float(np.std(efficacies)),
                    'median': float(np.median(efficacies))
                }
            }
            
        except Exception as e:
            logger.error(f"生成分布数据失败: {str(e)}")
            return {}
    
    def _save_result(self, result: Dict[str, Any]) -> str:
        """保存分析结果"""
        try:
            analysis_id = result['analysis_id']
            
            # 保存到内存
            self.results[analysis_id] = result
            
            # 保存到文件
            result_file = self.results_dir / f"{analysis_id}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            logger.info(f"分析结果已保存: {result_file}")
            return analysis_id
            
        except Exception as e:
            logger.error(f"结果保存失败: {str(e)}")
            raise
    
    def get_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """获取分析结果"""
        return self.results.get(analysis_id)
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """获取所有分析结果"""
        results = []
        for analysis_id, result in self.results.items():
            results.append({
                'analysis_id': analysis_id,
                'model_id': result.get('model_id'),
                'target_efficacy': result.get('target_efficacy'),
                'valid_rate': result.get('valid_rate'),
                'iterations': result.get('iterations'),
                'timestamp': result.get('timestamp')
            })
        return results
    
    def _load_saved_results(self):
        """加载已保存的结果"""
        try:
            for result_file in self.results_dir.glob("*.json"):
                try:
                    with open(result_file, 'r', encoding='utf-8') as f:
                        result = json.load(f)
                    analysis_id = result.get('analysis_id', result_file.stem)
                    self.results[analysis_id] = result
                except Exception as e:
                    logger.warning(f"加载结果文件失败 {result_file}: {str(e)}")
            
            logger.info(f"已加载 {len(self.results)} 个分析结果")
            
        except Exception as e:
            logger.error(f"加载保存的结果失败: {str(e)}")
    
    def generate_optimal_ranges(self, analysis_id: str, confidence_level: float = 0.95) -> Dict[str, Any]:
        """生成最优配比区间"""
        try:
            result = self.get_result(analysis_id)
            if not result:
                raise ValueError(f"分析结果 {analysis_id} 不存在")
            
            component_stats = result['component_statistics']
            optimal_ranges = {}
            
            for component, stats in component_stats.items():
                # 使用分位数计算置信区间
                alpha = 1 - confidence_level
                lower_percentile = (alpha / 2) * 100
                upper_percentile = (1 - alpha / 2) * 100
                
                # 这里简化处理，使用q25和q75作为区间
                optimal_ranges[component] = {
                    'min': stats['q25'],
                    'max': stats['q75'],
                    'mean': stats['mean'],
                    'confidence_level': confidence_level
                }
            
            return {
                'analysis_id': analysis_id,
                'confidence_level': confidence_level,
                'optimal_ranges': optimal_ranges
            }
            
        except Exception as e:
            logger.error(f"生成最优配比区间失败: {str(e)}")
            raise 