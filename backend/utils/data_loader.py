#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据加载和处理模块
"""

import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger
import json
from typing import Dict, List, Any, Optional

class DataLoader:
    """数据加载器"""
    
    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.json']
        self.upload_folder = Path('uploads')
        self.upload_folder.mkdir(exist_ok=True)
    
    def upload_file(self, file) -> Dict[str, Any]:
        """上传并处理文件"""
        try:
            filename = file.filename
            file_ext = Path(filename).suffix.lower()
            
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 保存文件
            file_path = self.upload_folder / filename
            file.save(str(file_path))
            
            # 读取数据
            data = self.read_file(file_path)
            
            # 验证数据
            validation_result = self.validate_data(data)
            
            return {
                'filename': filename,
                'file_path': str(file_path),
                'data': data,
                'validation': validation_result
            }
            
        except Exception as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise
    
    def read_file(self, file_path: Path) -> Dict[str, Any]:
        """读取文件内容"""
        file_ext = file_path.suffix.lower()
        
        try:
            if file_ext == '.csv':
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_ext == '.xlsx':
                df = pd.read_excel(file_path)
            elif file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # 如果是JSON格式，尝试转换为DataFrame
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict) and 'data' in data:
                    df = pd.DataFrame(data['data'])
                else:
                    raise ValueError("不支持的JSON格式")
            else:
                raise ValueError(f"不支持的文件格式: {file_ext}")
            
            # 转换为字典格式
            return {
                'columns': df.columns.tolist(),
                'data': df.to_dict('records'),
                'shape': df.shape,
                'dtypes': df.dtypes.to_dict()
            }
            
        except Exception as e:
            logger.error(f"文件读取失败: {str(e)}")
            raise
    
    def validate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """验证数据格式和内容"""
        try:
            validation_result = {
                'is_valid': True,
                'errors': [],
                'warnings': [],
                'info': {}
            }
            
            # 检查必要字段
            required_fields = ['columns', 'data']
            for field in required_fields:
                if field not in data:
                    validation_result['is_valid'] = False
                    validation_result['errors'].append(f"缺少必要字段: {field}")
            
            if not validation_result['is_valid']:
                return validation_result
            
            # 检查数据类型
            if not isinstance(data['columns'], list):
                validation_result['is_valid'] = False
                validation_result['errors'].append("columns字段必须是列表")
            
            if not isinstance(data['data'], list):
                validation_result['is_valid'] = False
                validation_result['errors'].append("data字段必须是列表")
            
            # 检查数据一致性
            if data['columns'] and data['data']:
                expected_columns = set(data['columns'])
                for i, row in enumerate(data['data']):
                    if not isinstance(row, dict):
                        validation_result['is_valid'] = False
                        validation_result['errors'].append(f"第{i+1}行数据格式错误")
                        continue
                    
                    row_columns = set(row.keys())
                    if row_columns != expected_columns:
                        validation_result['warnings'].append(f"第{i+1}行列数不匹配")
            
            # 统计信息
            if validation_result['is_valid']:
                validation_result['info'] = {
                    'row_count': len(data['data']),
                    'column_count': len(data['columns']),
                    'numeric_columns': self._get_numeric_columns(data),
                    'categorical_columns': self._get_categorical_columns(data)
                }
            
            return validation_result
            
        except Exception as e:
            logger.error(f"数据验证失败: {str(e)}")
            return {
                'is_valid': False,
                'errors': [f"验证过程出错: {str(e)}"],
                'warnings': [],
                'info': {}
            }
    
    def generate_preview(self, data: Dict[str, Any], max_rows: int = 10) -> Dict[str, Any]:
        """生成数据预览"""
        try:
            if not data.get('data'):
                return {'error': '没有数据可预览'}
            
            # 限制预览行数
            preview_data = data['data'][:max_rows]
            
            # 统计信息
            df = pd.DataFrame(data['data'])
            stats = {}
            
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    stats[col] = {
                        'type': 'numeric',
                        'min': float(df[col].min()),
                        'max': float(df[col].max()),
                        'mean': float(df[col].mean()),
                        'std': float(df[col].std()),
                        'null_count': int(df[col].isnull().sum())
                    }
                else:
                    stats[col] = {
                        'type': 'categorical',
                        'unique_count': int(df[col].nunique()),
                        'null_count': int(df[col].isnull().sum()),
                        'sample_values': df[col].dropna().unique()[:5].tolist()
                    }
            
            return {
                'preview_data': preview_data,
                'total_rows': len(data['data']),
                'columns': data['columns'],
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"生成预览失败: {str(e)}")
            return {'error': f'生成预览失败: {str(e)}'}
    
    def _get_numeric_columns(self, data: Dict[str, Any]) -> List[str]:
        """获取数值型列"""
        try:
            df = pd.DataFrame(data['data'])
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            return numeric_cols
        except:
            return []
    
    def _get_categorical_columns(self, data: Dict[str, Any]) -> List[str]:
        """获取分类型列"""
        try:
            df = pd.DataFrame(data['data'])
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            return categorical_cols
        except:
            return []
    
    def export_data(self, data: Dict[str, Any], format: str = 'csv', file_path: Optional[str] = None) -> str:
        """导出数据"""
        try:
            df = pd.DataFrame(data['data'])
            
            if not file_path:
                file_path = f"exported_data.{format}"
            
            if format.lower() == 'csv':
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif format.lower() == 'xlsx':
                df.to_excel(file_path, index=False)
            elif format.lower() == 'json':
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            else:
                raise ValueError(f"不支持的导出格式: {format}")
            
            logger.info(f"数据导出成功: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            raise 