#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API路由定义 - 模拟数据版本
"""

from flask import Blueprint, request, jsonify, send_file
from loguru import logger
import traceback
import time
import random
import json
import os
import numpy as np
from datetime import datetime
import io
import zipfile
from werkzeug.utils import secure_filename
import shutil

# 创建蓝图
symbolic_regression_bp = Blueprint('symbolic_regression', __name__)
monte_carlo_bp = Blueprint('monte_carlo', __name__)
data_bp = Blueprint('data', __name__)
data_models_bp = Blueprint('data_models', __name__)

# 数据模型存储路径
DATA_MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data_models')
CSV_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'csv_data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
RESULTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'results')
# docs 目录（用于读取初始的特征影响力）
DOCS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', 'docs'))

os.makedirs(DATA_MODELS_DIR, exist_ok=True)
os.makedirs(CSV_DATA_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# 符号表达式树操作的模拟指标序列（不要从文件读取，直接内嵌）
# 下标1..15分别对应第1~15次树结构变更后的指标；下标0表示基线，不覆盖。
MOCK_INDICATORS_SEQUENCE = [None] + [
    {
        "average_relative_error_test": 2.74596305113801,
        "average_relative_error_training": 2.3574806852981,
        "mean_absolute_error_test": 0.020585454497077455,
        "mean_absolute_error_training": 0.018182586660249123,
        "mean_squared_error_test": 0.00073464638025446673,
        "mean_squared_error_training": 0.00053687909383770235,
        "normalized_mean_squared_error_test": 0.14358163045309327,
        "normalized_mean_squared_error_training": 0.12666355569075083,
        "pearson_r_test": 0.86776941659869888,
        "pearson_r_training": 0.87333644430924906,
        "root_mean_squared_error_test": 0.02710436090843071,
        "root_mean_squared_error_training": 0.0231706515626493,
        "model_depth": 9,
        "model_length": 30
    },
    {
        "average_relative_error_test": 2.74596305113801,
        "average_relative_error_training": 2.3574806852981,
        "mean_absolute_error_test": 0.020585454497077448,
        "mean_absolute_error_training": 0.018182586660249123,
        "mean_squared_error_test": 0.00073464638025446673,
        "mean_squared_error_training": 0.00053687909383770235,
        "normalized_mean_squared_error_test": 0.14358163045309327,
        "normalized_mean_squared_error_training": 0.12666355569075086,
        "pearson_r_test": 0.86776941659869888,
        "pearson_r_training": 0.87333644430924928,
        "root_mean_squared_error_test": 0.02710436090843071,
        "root_mean_squared_error_training": 0.0231706515626493,
        "model_depth": 9,
        "model_length": 30
    },
    {
        "average_relative_error_test": 2.74596305113801,
        "average_relative_error_training": 2.3574806852981,
        "mean_absolute_error_test": 0.020585454497077455,
        "mean_absolute_error_training": 0.018182586660249123,
        "mean_squared_error_test": 0.0007346463802544676,
        "mean_squared_error_training": 0.00053687909383770245,
        "normalized_mean_squared_error_test": 0.14358163045309344,
        "normalized_mean_squared_error_training": 0.12666355569075086,
        "pearson_r_test": 0.86776941659869844,
        "pearson_r_training": 0.87333644430924906,
        "root_mean_squared_error_test": 0.027104360908430724,
        "root_mean_squared_error_training": 0.0231706515626493,
        "model_depth": 9,
        "model_length": 30
    },
    {
        "average_relative_error_test": 2.74596305113801,
        "average_relative_error_training": 2.3574806852981,
        "mean_absolute_error_test": 0.020585454497077455,
        "mean_absolute_error_training": 0.018182586660249123,
        "mean_squared_error_test": 0.00073464638025446673,
        "mean_squared_error_training": 0.00053687909383770235,
        "normalized_mean_squared_error_test": 0.14358163045309327,
        "normalized_mean_squared_error_training": 0.12666355569075083,
        "pearson_r_test": 0.86776941659869888,
        "pearson_r_training": 0.87333644430924906,
        "root_mean_squared_error_test": 0.02710436090843071,
        "root_mean_squared_error_training": 0.0231706515626493,
        "model_depth": 9,
        "model_length": 30
    },
    {
        "average_relative_error_test": 2.84597275187996,
        "average_relative_error_training": 2.48696808718705,
        "mean_absolute_error_test": 0.021330165641595289,
        "mean_absolute_error_training": 0.019181112565881491,
        "mean_squared_error_test": 0.00078426119873988346,
        "mean_squared_error_training": 0.00058318510503991,
        "normalized_mean_squared_error_test": 0.15327850873935517,
        "normalized_mean_squared_error_training": 0.13758833204365606,
        "pearson_r_test": 0.8668991495312971,
        "pearson_r_training": 0.86241166795634416,
        "root_mean_squared_error_test": 0.028004663874788491,
        "root_mean_squared_error_training": 0.024149225764813039,
        "model_depth": 11,
        "model_length": 33
    },
    {
        "average_relative_error_test": 2.84597275187996,
        "average_relative_error_training": 2.48696808718705,
        "mean_absolute_error_test": 0.0213301656415953,
        "mean_absolute_error_training": 0.019181112565881477,
        "mean_squared_error_test": 0.00078426119873988389,
        "mean_squared_error_training": 0.00058318510503990956,
        "normalized_mean_squared_error_test": 0.15327850873935531,
        "normalized_mean_squared_error_training": 0.13758833204365603,
        "pearson_r_test": 0.86689914953129676,
        "pearson_r_training": 0.86241166795634516,
        "root_mean_squared_error_test": 0.028004663874788498,
        "root_mean_squared_error_training": 0.024149225764813032,
        "model_depth": 9,
        "model_length": 29
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024353,
        "mean_absolute_error_training": 0.019199989104899291,
        "mean_squared_error_test": 0.000756269177768846,
        "mean_squared_error_training": 0.00059333589584469092,
        "normalized_mean_squared_error_test": 0.14780765892817582,
        "normalized_mean_squared_error_training": 0.1399831640852911,
        "pearson_r_test": 0.87072209571472137,
        "pearson_r_training": 0.86001683591470957,
        "root_mean_squared_error_test": 0.027500348684495732,
        "root_mean_squared_error_training": 0.024358487141953027,
        "model_depth": 11,
        "model_length": 32
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899284,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469081,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.024358487141953024,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899281,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469059,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529105,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470979,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.02435848714195302,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899281,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469059,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.02435848714195302,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899284,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469081,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.024358487141953024,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899281,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469059,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529105,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470979,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.02435848714195302,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899281,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469059,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.02435848714195302,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899284,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469081,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.024358487141953024,
        "model_depth": 9,
        "model_length": 28
    },
    {
        "average_relative_error_test": 2.82362275136901,
        "average_relative_error_training": 2.48051448622132,
        "mean_absolute_error_test": 0.021248478681024374,
        "mean_absolute_error_training": 0.019199989104899284,
        "mean_squared_error_test": 0.00075626917776884647,
        "mean_squared_error_training": 0.00059333589584469081,
        "normalized_mean_squared_error_test": 0.14780765892817591,
        "normalized_mean_squared_error_training": 0.13998316408529107,
        "pearson_r_test": 0.87072209571472114,
        "pearson_r_training": 0.86001683591470945,
        "root_mean_squared_error_test": 0.027500348684495739,
        "root_mean_squared_error_training": 0.024358487141953024,
        "model_depth": 9,
        "model_length": 28
    }
]

# 符号回归分析的初始特征权重（基线数据）
MOCK_WEIGHTS_BASELINE = [
    {'feature': 'VR', 'importance': 0.40331375862937024},
    {'feature': 'HYP', 'importance': 0.30740076820527074},
    {'feature': 'UA', 'importance': 0.23746410777792382},
    {'feature': 'CA', 'importance': 0.22610791660542262},
    {'feature': 'MA', 'importance': 0.15483347260005331},
    {'feature': 'QA', 'importance': 0.026878474944676545},
    {'feature': 'OA', 'importance': 0.013918586597244875},
    {'feature': 'MDA', 'importance': 0},
    {'feature': 'QUE', 'importance': 0},
    {'feature': 'CRA', 'importance': 0},
    {'feature': 'EPI', 'importance': 0},
    {'feature': 'PC1', 'importance': 0},
    {'feature': 'PB2', 'importance': 0},
    {'feature': 'VG', 'importance': 0},
    {'feature': 'RUT', 'importance': 0},
    {'feature': 'GUA', 'importance': 0},
    {'feature': 'AST', 'importance': 0},
    {'feature': 'PIS', 'importance': 0},
    {'feature': 'CCGA', 'importance': 0},
    {'feature': 'CGA', 'importance': 0},
    {'feature': 'NCGA', 'importance': 0}
]

# 符号表达式树操作的模拟特征权重序列（不要从文件读取，直接内嵌）
# 下标1..15分别对应第1~15次树结构变更后的特征权重；下标0表示基线，不覆盖。
MOCK_WEIGHTS_SEQUENCE = [None] + [
    [
        {'feature': 'VR', 'importance': 0.40331375862937024},
        {'feature': 'HYP', 'importance': 0.30740076820527074},
        {'feature': 'UA', 'importance': 0.23746410777792382},
        {'feature': 'CA', 'importance': 0.22610791660542262},
        {'feature': 'MA', 'importance': 0.15483347260005331},
        {'feature': 'QA', 'importance': 0.026878474944676545},
        {'feature': 'OA', 'importance': 0.013918586597244875},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'VR', 'importance': 0.40331375862937047},
        {'feature': 'HYP', 'importance': 0.30740076820527074},
        {'feature': 'UA', 'importance': 0.23746410777792459},
        {'feature': 'CA', 'importance': 0.22610791660542306},
        {'feature': 'MA', 'importance': 0.15483347260005353},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597245208},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'VR', 'importance': 0.40331375862937041},
        {'feature': 'HYP', 'importance': 0.30740076820527051},
        {'feature': 'UA', 'importance': 0.23746410777792437},
        {'feature': 'CA', 'importance': 0.22610791660542284},
        {'feature': 'MA', 'importance': 0.15483347260005331},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597244986},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'VR', 'importance': 0.40331375862937041},
        {'feature': 'HYP', 'importance': 0.30740076820527051},
        {'feature': 'UA', 'importance': 0.23746410777792437},
        {'feature': 'CA', 'importance': 0.22610791660542284},
        {'feature': 'MA', 'importance': 0.15483347260005331},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597244986},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597244986},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597244986},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'QA', 'importance': 0.026878474944676323},
        {'feature': 'OA', 'importance': 0.013918586597244986},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ],
    [
        {'feature': 'HYP', 'importance': 0.36678996351202248},
        {'feature': 'VR', 'importance': 0.3610819114205992},
        {'feature': 'UA', 'importance': 0.28351747274386141},
        {'feature': 'CA', 'importance': 0.22066636862784783},
        {'feature': 'MA', 'importance': 0.12704990635004476},
        {'feature': 'MDA', 'importance': 0},
        {'feature': 'QUE', 'importance': 0},
        {'feature': 'CRA', 'importance': 0},
        {'feature': 'OA', 'importance': 0},
        {'feature': 'EPI', 'importance': 0},
        {'feature': 'PC1', 'importance': 0},
        {'feature': 'PB2', 'importance': 0},
        {'feature': 'VG', 'importance': 0},
        {'feature': 'RUT', 'importance': 0},
        {'feature': 'GUA', 'importance': 0},
        {'feature': 'AST', 'importance': 0},
        {'feature': 'PIS', 'importance': 0},
        {'feature': 'CCGA', 'importance': 0},
        {'feature': 'CGA', 'importance': 0},
        {'feature': 'NCGA', 'importance': 0},
        {'feature': 'QA', 'importance': 0}
    ]
]

# =============================
# 表达式树（SVG）十五步模拟：内嵌定义
# =============================
# 说明：这组数据对应 docs/mock/impact/impact-*.json 中的15步模拟树。
# 为避免 JSON 重复键的二义性，这里采用“规范化树”结构进行内嵌：
# - 叶子：
#   { 'type': 'var',  'name': 'HYP', 'coef': -1.9105, 'w': 0.21010 }  → 变量（含系数、用于生成“coef * VAR”形式）
#   { 'type': 'const','value': 0.93054, 'w': 0 }                      → 常量
# - 运算：
#   { 'type': 'op', 'op': 'add'|'sub'|'mul'|'div', 'children': [ ... ] }
#
# 我们提供辅助函数将该结构：
# - 转换为用于前端上色的 impact_tree（一个“叶子标签→影响力”的字典，叶子标签如“0.00653 * VR”、“-1.9105 * HYP”、“5.4189”）。
# - 转换为可渲染的表达式字符串（expression_text），以及 LaTeX（expression_latex）。

def _node_var(name: str, coef: float = None, w: float = None):
    return {'type': 'var', 'name': str(name), 'coef': coef, 'w': w}

def _node_const(value: float, w: float = None):
    return {'type': 'const', 'value': float(value), 'w': w}

def _node_op(op: str, *children):
    # 扁平化相同运算符，避免不必要的嵌套
    flat_children = []
    for ch in children:
        if isinstance(ch, dict) and ch.get('type') == 'op' and ch.get('op') == op:
            flat_children.extend(ch.get('children') or [])
        else:
            flat_children.append(ch)
    return {'type': 'op', 'op': op, 'children': flat_children}

def _fmt_num(x: float) -> str:
    # 去除末尾无意义的0；保留必要的小数
    s = ("%0.10f" % float(x)).rstrip('0').rstrip('.')
    # 避免 -0
    if s == '-0':
        s = '0'
    return s

def _leaf_label(node: dict) -> str:
    # 生成 impact_tree 的叶子键名
    if node.get('type') == 'var':
        coef = node.get('coef', None)
        name = node.get('name', '')
        if coef is None or coef == 1:
            return f"{name}"
        return f"{_fmt_num(coef)} * {name}"
    if node.get('type') == 'const':
        return _fmt_num(node.get('value', 0))
    return '?'  # 不应出现

def _collect_impact_map(node: dict, mapping: dict):
    if not isinstance(node, dict):
        return
    tp = node.get('type')
    if tp in ('var', 'const'):
        label = _leaf_label(node)
        w = node.get('w', 0)
        if isinstance(w, (int, float)):
            mapping[label] = float(w)
        else:
            mapping[label] = 0.0
        return
    if tp == 'op':
        for ch in node.get('children') or []:
            _collect_impact_map(ch, mapping)

def _expr_of(node: dict) -> str:
    # 生成纯文本表达式，使用括号保证优先级
    tp = node.get('type')
    if tp == 'var':
        coef = node.get('coef', None)
        name = node.get('name')
        if coef is None:
            return f"{name}"
        return f"({_fmt_num(coef)} * {name})"
    if tp == 'const':
        return _fmt_num(node.get('value', 0.0))
    if tp == 'op':
        op = node.get('op')
        ch = node.get('children') or []
        if op == 'add':
            return '(' + ' + '.join(_expr_of(c) for c in ch) + ')'
        if op == 'sub':
            if len(ch) == 0:
                return '0'
            if len(ch) == 1:
                return _expr_of(ch[0])
            return '(' + ' - '.join(_expr_of(c) for c in ch) + ')'
        if op == 'mul':
            return '(' + ' * '.join(_expr_of(c) for c in ch) + ')'
        if op == 'div':
            a = _expr_of(ch[0]) if len(ch) >= 1 else '1'
            b = _expr_of(ch[1]) if len(ch) >= 2 else '1'
            return f"({a} / {b})"
    return '0'

def _latex_of(node: dict) -> str:
    # 生成 LaTeX（MathJax）
    tp = node.get('type')
    if tp == 'var':
        coef = node.get('coef', None)
        name = node.get('name')
        if coef is None:
            return f"\\text{{{name}}}"
        return f"({_fmt_num(coef)} \\cdot \\text{{{name}}})"
    if tp == 'const':
        return _fmt_num(node.get('value', 0.0))
    if tp == 'op':
        op = node.get('op')
        ch = node.get('children') or []
        if op == 'add':
            return '(' + ' + '.join(_latex_of(c) for c in ch) + ')'
        if op == 'sub':
            if len(ch) == 0:
                return '0'
            if len(ch) == 1:
                return _latex_of(ch[0])
            return '(' + ' - '.join(_latex_of(c) for c in ch) + ')'
        if op == 'mul':
            return '(' + ' \\cdot '.join(_latex_of(c) for c in ch) + ')'
        if op == 'div':
            a = _latex_of(ch[0]) if len(ch) >= 1 else '1'
            b = _latex_of(ch[1]) if len(ch) >= 2 else '1'
            return f"\\cfrac{{{a}}}{{{b}}}"
    return '0'

def _collect_constants(node: dict, bag: list):
    # 提取数字常量（包括变量系数），用于 constants 模块展示
    tp = node.get('type')
    if tp == 'const':
        bag.append(float(node.get('value', 0)))
        return
    if tp == 'var':
        coef = node.get('coef', None)
        if coef is not None:
            bag.append(float(coef))
        return
    if tp == 'op':
        for ch in node.get('children') or []:
            _collect_constants(ch, bag)

def _constants_dict_from_tree(node: dict) -> dict:
    nums = []
    _collect_constants(node, nums)
    # 按出现顺序去重
    ordered = []
    seen = set()
    for v in nums:
        if v not in seen:
            seen.add(v)
            ordered.append(v)
    consts = {}
    for i, v in enumerate(ordered):
        consts[f'c{{{i}}}'] = float(v)
    return consts

def _impact_map_from_tree(node: dict) -> dict:
    mp = {}
    _collect_impact_map(node, mp)
    return mp

def _op_label(op: str) -> str:
    return 'Addition' if op == 'add' else 'Subtraction' if op == 'sub' else 'Multiplication' if op == 'mul' else 'Division' if op == 'div' else str(op)

def _merge_dict(a: dict, b: dict):
    for k, v in (b or {}).items():
        if k in a and isinstance(a[k], dict) and isinstance(v, dict):
            _merge_dict(a[k], v)
        else:
            a[k] = v

def _impact_nested_from_tree(node: dict, wrap_root: bool = True) -> dict:
    """将规范树转换为前端可消费的 impact_tree 嵌套结构。
    规则：
    - 变量/常量叶子 → { 'label': weight }
    - 运算节点 → { OpLabel: merged_children }
    同类运算子树合并到同一 OpLabel 下，避免重复键。
    """
    tp = isinstance(node, dict) and node.get('type')
    if tp == 'var' or tp == 'const':
        return { _leaf_label(node): float(node.get('w', 0) or 0) }
    if tp == 'op':
        op = node.get('op')
        label = _op_label(op)
        merged = {}
        for ch in node.get('children') or []:
            sub = _impact_nested_from_tree(ch, wrap_root=False)
            # 子为运算 → 必须包在其自身的OpLabel下
            if isinstance(ch, dict) and ch.get('type') == 'op':
                sub_label = _op_label(ch.get('op'))
                if sub_label not in merged:
                    merged[sub_label] = {}
                _merge_dict(merged[sub_label], sub.get(sub_label) if sub_label in sub else sub)
            else:
                _merge_dict(merged, sub)
        return { label: merged } if wrap_root else { label: merged }
    return {}

# ============
# 规范化的15步树定义（根据 docs/mock/impact 转写，略化为可渲染且与权重键一致的结构）
# 提示：为保证演示稳定，部分步骤使用一致的结构但替换了关键系数/常量；
# 结构差异较大的第5步/第7步使用了顶层缩放与偏移包裹。
# ============

def _step_tree_1():
    return _node_op('add',
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-28.494, 0.076351789675616), _node_var('HYP'))),
        _node_op('div',
            _node_op('mul', _node_const(0.00653, 0.0208902884673897), _node_var('VR')),
            _node_op('add', _node_var('HYP', -1.9105, 0.210102360045851), _node_const(5.4189, 0))
        ),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('QA', 0.6015, 0.0117584596321174), _node_var('HYP', 2.3379, 0.0228735360067907), _node_var('CA', 1.2977, 0.113928459255378), _node_const(10.458, 0)),
                _node_op('mul', _node_const(0.078141, 0), _node_var('MA', None, 0.108972688038807), _node_op('add', _node_var('UA', 1.2053, 0.108144059957083), _node_var('OA', 1.4812, 0.00688842480665586), _node_const(-1.9323, 0))),
                _node_const(0.0053559, 0)
            ),
            _node_var('VR', 2.9628, 0.279624923755845)
        ),
        _node_const(0.93054, 0)
    )

def _step_tree_2():
    return _node_op('add',
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-28.494, 0.0763517896756718), _node_var('HYP'))),
        _node_op('div',
            _node_op('mul', _node_const(0.00653, 0.0208902884673899), _node_var('VR')),
            _node_op('add', _node_var('HYP', -1.9105, 0.210102360045851), _node_const(5.4189, 0))
        ),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('QA', 0.6015, 0.0117584596321172), _node_var('HYP', 2.3379, 0.0228735360067907), _node_var('CA', 1.2977, 0.113928459255378), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.108972688038807), _node_op('add', _node_var('UA', 1.2053, 0.108144059957083), _node_var('OA', 1.4812, 0.00688842480665564), _node_const(-1.9323, 0))),
                _node_const(0.0053559, 0)
            ),
            _node_var('VR', 2.9628, 0.279624923755845)
        ),
        _node_const(0.93054, 0)
    )

def _step_tree_3():
    return _node_op('add',
        _node_op('div',
            _node_op('mul', _node_const(0.00653, 0.0208902884673897), _node_var('VR')),
            _node_op('add', _node_var('HYP', -1.9105, 0.210102360045851), _node_const(5.4189, 0))
        ),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('HYP', 2.3379, 0.0228735360067904), _node_var('CA', 1.2977, 0.113928459255379), _node_var('QA', 0.6015, 0.0117584596321172), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.108972688038807), _node_op('add', _node_var('UA', 1.2053, 0.108144059957083), _node_var('OA', 1.4812, 0.00688842480665564), _node_const(-1.9323, 0))),
                _node_const(0.0053559, 0)
            ),
            _node_var('VR', 2.9628, 0.279624923755845)
        ),
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-28.494, 0.076351789675672), _node_var('HYP'))),
        _node_const(0.93054, 0)
    )

def _step_tree_4():
    return _node_op('add',
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-28.494, 0.0763517896756716), _node_var('HYP'))),
        _node_op('div',
            _node_op('mul', _node_const(0.00653, 0.0208902884673897), _node_var('VR')),
            _node_op('add', _node_var('HYP', -1.9105, 0.210102360045851), _node_const(5.4189, 0))
        ),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('QA', 0.6015, 0.0117584596321174), _node_var('HYP', 2.3379, 0.0228735360067907), _node_var('CA', 1.2977, 0.113928459255378), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.108972688038807), _node_op('add', _node_var('UA', 1.2053, 0.108144059957083), _node_var('OA', 1.4812, 0.00688842480665586), _node_const(-1.9323, 0))),
                _node_const(0.0053559, 0)
            ),
            _node_var('VR', 2.9628, 0.279624923755845)
        ),
        _node_const(0.93054, 0)
    )

def _step_tree_5():
    inner_add = _node_op('add',
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-28.494, 0.0733317696147618), _node_var('HYP'))),
        _node_op('div', _node_op('mul', _node_const(0.00653, 0.0208950935373927), _node_var('VR')), _node_op('add', _node_var('HYP', -1.9105, 0.247577708475269), _node_const(5.4189, 0))),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('QA', 0.6015, 0.00534718638286213), _node_var('HYP', 2.3379, 0.0283254630009195), _node_var('CA', 1.2977, 0.121817221428969), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.0812579052747987), _node_op('add', _node_var('UA', 1.2053, 0.137119380648784), _node_const(-1.9323, 0))),
                _node_const(0.0053559, 0)
            ),
            _node_var('VR', 2.9628, 0.275874028734677)
        ),
        _node_const(0.93054, 0)
    )
    return _node_op('add', _node_op('mul', inner_add, _node_const(1.1499, 0)), _node_const(-0.14436, 0))

def _step_tree_6():
    return _node_op('add',
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-24.78, 0.0733317696147628), _node_var('HYP'))),
        _node_op('div', _node_op('mul', _node_const(0.0075089, 0.0208950935373935), _node_var('VR')), _node_op('add', _node_var('HYP', -1.9105, 0.24757770847527), _node_const(5.4189, 0))),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('HYP', 2.3379, 0.0283254630009203), _node_var('CA', 1.2977, 0.121817221428969), _node_var('QA', 0.6015, 0.0053471863828628), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.0812579052747997), _node_op('add', _node_var('UA', 1.2053, 0.137119380648785), _node_const(-1.9323, 0))),
                _node_const(0.0061587, 0)
            ),
            _node_var('VR', 2.9628, 0.275874028734678)
        ),
        _node_const(0.92566, 0)
    )

def _step_tree_7():
    inner_add = _node_op('add',
        _node_op('div', _node_op('mul', _node_const(0.0075089, 0.0196564510771616), _node_var('VR')), _node_op('add', _node_var('HYP', -1.9105, 0.255861250843903), _node_const(5.4189, 0))),
        _node_op('div',
            _node_op('mul',
                _node_op('add', _node_var('HYP', 2.3379, 0.0245600888604456), _node_var('CA', 1.2977, 0.134997651842973), _node_const(10.458, 0)),
                _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, 0.0915664689038374), _node_op('add', _node_var('UA', 1.2053, 0.139791872958965), _node_const(-1.9323, 0))),
                _node_const(0.0061587, 0)
            ),
            _node_var('VR', 2.9628, 0.264262090594079)
        ),
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(-24.78, 0.0996617689752506), _node_var('HYP'))),
        _node_const(0.92566, 0)
    )
    return _node_op('add', _node_op('mul', inner_add, _node_const(1.0627, 0)), _node_const(-0.059992, 0))

def _step_tree_late_common(vr_small_coef: float, hyp_div: float, 
                           include_oa: bool, ua_w: float, ma_w: float,
                           hyp2_w: float, ca_w: float, mul_k: float,
                           offset_const: float):
    # 用于步骤8及之后的共用结构（略化）：
    add2 = _node_op('add', _node_var('HYP', 2.3379, hyp2_w), _node_var('CA', 1.2977, ca_w), _node_const(10.458, 0))
    if include_oa:
        inner_add = _node_op('add', _node_var('UA', 1.2053, ua_w), _node_const(-1.9323, 0))
    else:
        inner_add = _node_op('add', _node_var('UA', 1.2053, ua_w), _node_const(-1.9323, 0))
    return _node_op('add',
        _node_op('div',
            _node_op('mul', add2, _node_op('mul', _node_const(-0.078141, 0), _node_var('MA', None, ma_w), inner_add), _node_const(mul_k, 0)),
            _node_var('VR', 2.9628, 0.264262090594078)
        ),
        _node_op('div', _node_const(1, 0), _node_op('mul', _node_const(hyp_div, 0.0996617689752507), _node_var('HYP'))),
        _node_op('div', _node_op('mul', _node_const(vr_small_coef, 0.0196564510771614), _node_var('VR')), _node_op('add', _node_var('HYP', -1.9105, 0.255861250843903), _node_const(5.4189, 0))),
        _node_const(offset_const, 0)
    )

def _step_tree_8():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.0915664689038371, 0.0245600888604455, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_9():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.091566468903837, 0.0245600888604458, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_10():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.0915664689038371, 0.0245600888604455, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_11():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.0915664689038371, 0.0245600888604455, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_12():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.091566468903837, 0.0245600888604458, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_13():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.0915664689038371, 0.0245600888604455, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_14():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.0915664689038371, 0.0245600888604455, 0.134997651842973, 0.0065447, 0.92369)

def _step_tree_15():
    return _step_tree_late_common(0.0079795, -23.318, False, 0.139791872958965, 0.091566468903837, 0.0245600888604458, 0.134997651842973, 0.0065447, 0.92369)

MOCK_IMPACT_TREES = [
    None,
    _step_tree_1(),
    _step_tree_2(),
    _step_tree_3(),
    _step_tree_4(),
    _step_tree_5(),
    _step_tree_6(),
    _step_tree_7(),
    _step_tree_8(),
    _step_tree_9(),
    _step_tree_10(),
    _step_tree_11(),
    _step_tree_12(),
    _step_tree_13(),
    _step_tree_14(),
    _step_tree_15(),
]

def load_data_models():
    """加载所有数据模型"""
    models = []
    if os.path.exists(DATA_MODELS_DIR):
        for filename in os.listdir(DATA_MODELS_DIR):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(DATA_MODELS_DIR, filename), 'r', encoding='utf-8') as f:
                        model = json.load(f)
                        # 检查文件存在性
                        model['metadata'] = model.get('metadata', {})
                        csv_name = model.get('data_files', {}).get('csv_data')
                        reg_name = model.get('data_files', {}).get('regression_model')
                        mc_name = model.get('data_files', {}).get('monte_carlo_results')
                        model['metadata']['has_csv_data'] = bool(csv_name) and os.path.exists(os.path.join(CSV_DATA_DIR, csv_name))
                        model['metadata']['has_regression_model'] = bool(reg_name) and os.path.exists(os.path.join(MODELS_DIR, reg_name))
                        model['metadata']['has_monte_carlo_results'] = bool(mc_name) and os.path.exists(os.path.join(RESULTS_DIR, mc_name))
                        models.append(model)
                except Exception as e:
                    logger.error(f"加载数据模型文件 {filename} 失败: {e}")
    return models

@symbolic_regression_bp.route('/expression-tree/summary', methods=['POST'])
def expression_tree_summary():
    """表达式树页面左侧摘要（空壳模拟）。
    优先使用请求体中的 model（即前端刚跑完的回归结果）；否则若提供 model_id，则从数据模型文件读取；
    若仍不可用，则返回一份固定示例，保证页面可渲染。
    """
    try:
        data = request.get_json(silent=True) or {}
        result = None

        # 1) 直接使用前端传来的回归结果
        if isinstance(data.get('model'), dict):
            result = data['model']
        else:
            # 2) 尝试使用提供的 model_id
            model_id = data.get('model_id')
            if model_id:
                filename = f"{model_id}.json"
                filepath = os.path.join(DATA_MODELS_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        model = json.load(f)
                    # 读取回归模型文件（更完整的数据来源）
                    reg_json = None
                    try:
                        reg_name = (model.get('data_files') or {}).get('regression_model')
                        if reg_name:
                            reg_path = os.path.join(MODELS_DIR, reg_name)
                            if os.path.exists(reg_path):
                                with open(reg_path, 'r', encoding='utf-8') as rf:
                                    reg_json = json.load(rf)
                    except Exception as _:
                        reg_json = None

                    # 合并字段：优先使用回归模型JSON，其次模型元数据，最后给出合理兜底
                    result = {
                        'id': model.get('id'),
                        'expression': (reg_json or {}).get('expression_text') or (reg_json or {}).get('expression') or model.get('expression') or (
                            "(((((1.9105 * HYP + ((((0.6015 * QA + 0.42745 * HYP) + 1.2977 * CA) - (-10.458))))"
                            " * (-1.9323 + -0.078141 * MA * (((-1.9323 + 1.4812 * OA) + 0.59744 * UA) + 0.60783 * UA)))"
                            " / (2.9628 * VR) - 2.6756 / (0.40832 * HYP)) + (1.2192 * VR) / (5.4189 - 1.9105 * HYP))"
                            " * 0.0053559 + 0.93054)"
                        ),
                        'target_variable': (reg_json or {}).get('target_variable') or model.get('target_column', 'Y'),
                        'constants': (reg_json or {}).get('constants') or model.get('constants') or {
                            'c{0}': 1.9105,
                            'c{1}': 0.6015,
                            'c{2}': 0.42745,
                            'c{3}': 1.2977,
                            'c{4}': -10.458,
                            'c{5}': -1.9323,
                            'c{6}': -0.078141,
                            'c{7}': -1.9323,
                            'c{8}': 1.4812,
                            'c{9}': 0.59744,
                            'c{10}': 0.60783,
                            'c{11}': 2.9628,
                            'c{12}': 2.6756,
                            'c{13}': 0.40832,
                            'c{14}': 1.2192,
                            'c{15}': 5.4189,
                            'c{16}': 1.9105,
                            'c{17}': 0.0053559,
                            'c{18}': 0.93054,
                        },
                        'expression_latex': (reg_json or {}).get('expression_latex') or (
                            r"HDL =  \left(  \left(  \left(  \cfrac{  \left( c_{0}  \cdot\text{HYP} +  \left(  \left(  \left( c_{1}  \cdot\text{QA} + c_{2}  \cdot\text{HYP} \right)  + c_{3}  \cdot\text{CA} \right)  - c_{4} \right)  \right)  \cdot  \left( c_{5} + c_{6}  \cdot\text{MA}  \cdot  \left(  \left(  \left( c_{7} + c_{8}  \cdot\text{OA} \right)  + c_{9}  \cdot\text{UA} \right)  + c_{10}  \cdot\text{UA} \right)  \right) }{c_{11}  \cdot\text{VR} }  -  \cfrac{ c_{12}}{c_{13}  \cdot\text{HYP} }  \right)  +  \cfrac{ c_{14}  \cdot\text{VR}}{ \left( c_{15} - c_{16}  \cdot\text{HYP} \right)  }  \right)  \cdot c_{17} + c_{18} \right)"
                        ),
                        'pearson_r_test': (reg_json or {}).get('detailed_metrics', {}).get('pearson_r_test') or model.get('metadata', {}).get('pearson_r_test'),
                        'pearson_r_training': (reg_json or {}).get('detailed_metrics', {}).get('pearson_r_training') or model.get('metadata', {}).get('pearson_r_training'),
                        'mse': (reg_json or {}).get('mse') or model.get('metadata', {}).get('mse_score', 0.12),
                        'feature_importance': (reg_json or {}).get('feature_importance') or model.get('feature_importance') or [],
                        'impact_tree': (reg_json or {}).get('impact_tree') or model.get('symbolic_regression', {}).get('impact_tree') or None,
                        'detailed_metrics': (reg_json or {}).get('detailed_metrics') or model.get('detailed_metrics') or {
                            "average_relative_error_test": 2.74596305113801,
                            "average_relative_error_training": 2.3574806852981,
                            "mean_absolute_error_test": 0.020585454497077455,
                            "mean_absolute_error_training": 0.018182586660249116,
                            "mean_squared_error_test": 0.00073464638025446652,
                            "mean_squared_error_training": 0.00053687909383770213,
                            "model_depth": 14,
                            "model_length": 39,
                            "normalized_mean_squared_error_test": 0.14358163045309325,
                            "normalized_mean_squared_error_training": 0.12666355569075077,
                            "pearson_r_test": 0.86776941659869866,
                            "pearson_r_training": 0.87333644430924906,
                            "root_mean_squared_error_test": 0.027104360908430703,
                            "root_mean_squared_error_training": 0.023170651562649292
                        },
                        'data_model_id': model.get('id')
                    }

        # 3) 兜底固定示例（改为复杂表达式）
        if result is None:
            result = {
                'id': int(time.time()),
                'expression': (
                    "(((((1.9105 * HYP + ((((0.6015 * QA + 0.42745 * HYP) + 1.2977 * CA) - (-10.458))))"
                    " * (-1.9323 + -0.078141 * MA * (((-1.9323 + 1.4812 * OA) + 0.59744 * UA) + 0.60783 * UA)))"
                    " / (2.9628 * VR) - 2.6756 / (0.40832 * HYP)) + (1.2192 * VR) / (5.4189 - 1.9105 * HYP))"
                    " * 0.0053559 + 0.93054)"
                ),
                'expression_latex': (
                    r"HDL =  \left(  \left(  \left(  \cfrac{  \left( c_{0}  \cdot\text{HYP} +  \left(  \left(  \left( c_{1}  \cdot\text{QA} + c_{2}  \cdot\text{HYP} \right)  + c_{3}  \cdot\text{CA} \right)  - c_{4} \right)  \right)  \cdot  \left( c_{5} + c_{6}  \cdot\text{MA}  \cdot  \left(  \left(  \left( c_{7} + c_{8}  \cdot\text{OA} \right)  + c_{9}  \cdot\text{UA} \right)  + c_{10}  \cdot\text{UA} \right)  \right) }{c_{11}  \cdot\text{VR} }  -  \cfrac{ c_{12}}{c_{13}  \cdot\text{HYP} }  \right)  +  \cfrac{ c_{14}  \cdot\text{VR}}{ \left( c_{15} - c_{16}  \cdot\text{HYP} \right)  }  \right)  \cdot c_{17} + c_{18} \right)"
                ),
                'target_variable': 'HDL',
                'constants': {
                    'c{0}': 1.9105,
                    'c{1}': 0.6015,
                    'c{2}': 0.42745,
                    'c{3}': 1.2977,
                    'c{4}': -10.458,
                    'c{5}': -1.9323,
                    'c{6}': -0.078141,
                    'c{7}': -1.9323,
                    'c{8}': 1.4812,
                    'c{9}': 0.59744,
                    'c{10}': 0.60783,
                    'c{11}': 2.9628,
                    'c{12}': 2.6756,
                    'c{13}': 0.40832,
                    'c{14}': 1.2192,
                    'c{15}': 5.4189,
                    'c{16}': 1.9105,
                    'c{17}': 0.0053559,
                    'c{18}': 0.93054,
                },

                'feature_importance': [
                    {'feature': 'HYP', 'importance': 0.85},
                    {'feature': 'QA', 'importance': 0.7},
                    {'feature': 'CA', 'importance': 0.6},
                    {'feature': 'VR', 'importance': 0.55},
                    {'feature': 'OA', 'importance': 0.5},
                    {'feature': 'UA', 'importance': 0.45},
                    {'feature': 'MA', 'importance': 0.4},
                ],
                'impact_tree': {
                    "Addition": {
                        "Multiplication": {
                            "Addition": {
                                "Subtraction": {
                                    "Division": {
                                        "Multiplication": {
                                            "Addition": {
                                                "1.9105 * HYP": 0.0157069022188682,
                                                "Subtraction": {
                                                    "Addition": {
                                                        "Addition": {
                                                            "0.6015 * QA": 0.011758459632117,
                                                            "0.4274 * HYP": 0.00120390671170711
                                                        },
                                                        "1.2977 * CA": 0.113928459255378
                                                    },
                                                    "-10.458": 0
                                                }
                                            },
                                            "Addition": {
                                                "-1.9323": 0,
                                                "Multiplication": {
                                                    "-0.0781 * MA": 0.108972688038807,
                                                    "Addition": {
                                                        "Addition": {
                                                            "Addition": {
                                                                "-1.9323": 0,
                                                                "1.4812 * OA": 0.00688842480665608
                                                            },
                                                            "0.5974 * UA": 0.0111402882791509
                                                        },
                                                        "0.6078 * UA": 0.0120783966067667
                                                    }
                                                }
                                            }
                                        },
                                        "2.9628 * VR": 0.279624923755846
                                    },
                                    "Division": {
                                        "2.6756": 0,
                                        "0.4083 * HYP": 0.0763517896756712
                                    }
                                },
                                "Division": {
                                    "1.2192 * VR": 0.0208902884673905,
                                    "Subtraction": {
                                        "5.4189": 0,
                                        "1.9105 * HYP": 0.21010236004585
                                    }
                                }
                            },
                            "0.0054": 0
                        },
                        "0.9305": 0
                    }
                },
                'detailed_metrics': {
                    "average_relative_error_test": 2.74596305113801,
                    "average_relative_error_training": 2.3574806852981,
                    "mean_absolute_error_test": 0.020585454497077455,
                    "mean_absolute_error_training": 0.018182586660249116,
                    "mean_squared_error_test": 0.00073464638025446652,
                    "mean_squared_error_training": 0.00053687909383770213,
                    "model_depth": 14,
                    "model_length": 39,
                    "normalized_mean_squared_error_test": 0.14358163045309325,
                    "normalized_mean_squared_error_training": 0.12666355569075077,
                    "pearson_r_test": 0.86776941659869866,
                    "pearson_r_training": 0.87333644430924906,
                    "root_mean_squared_error_test": 0.027104360908430703,
                    "root_mean_squared_error_training": 0.023170651562649292
                },
                'data_model_id': None
            }

        return jsonify({'success': True, 'result': result})
    except Exception as e:
        logger.error(f"表达式树摘要返回失败: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

def save_data_model(model):
    """保存数据模型"""
    try:
        model_id = model['id']
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(model, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据模型已保存: {filename}")
        return True
    except Exception as e:
        logger.error(f"保存数据模型失败: {e}")
        return False

def create_data_model_files(model_id, csv_data=None, regression_model=None, monte_carlo_results=None):
    """创建数据模型相关的文件"""
    try:
        # 创建CSV数据文件
        if csv_data:
            csv_filename = f"{model_id}_data.csv"
            csv_filepath = os.path.join(CSV_DATA_DIR, csv_filename)
            with open(csv_filepath, 'w', encoding='utf-8') as f:
                f.write(csv_data)
            logger.info(f"CSV数据文件已创建: {csv_filename}")
        
        # 创建符号回归模型文件
        if regression_model:
            model_filename = f"{model_id}_regression.json"
            model_filepath = os.path.join(MODELS_DIR, model_filename)
            with open(model_filepath, 'w', encoding='utf-8') as f:
                json.dump(regression_model, f, ensure_ascii=False, indent=2)
            logger.info(f"符号回归模型文件已创建: {model_filename}")
        
        # 创建蒙特卡洛分析结果文件
        if monte_carlo_results:
            results_filename = f"{model_id}_monte_carlo.txt"
            results_filepath = os.path.join(RESULTS_DIR, results_filename)
            with open(results_filepath, 'w', encoding='utf-8') as f:
                f.write(monte_carlo_results)
            logger.info(f"蒙特卡洛分析结果文件已创建: {results_filename}")
        
        return True
    except Exception as e:
        logger.error(f"创建数据模型文件失败: {e}")
        return False

def delete_data_model(model_id):
    """删除数据模型及其相关文件"""
    try:
        # 删除主模型文件
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if os.path.exists(filepath):
            # 读取模型信息以获取相关文件
            with open(filepath, 'r', encoding='utf-8') as f:
                model = json.load(f)
            
            # 删除相关文件
            data_files = model.get('data_files', {})
            
            # 删除CSV数据文件
            if 'csv_data' in data_files:
                csv_filepath = os.path.join(CSV_DATA_DIR, data_files['csv_data'])
                if os.path.exists(csv_filepath):
                    os.remove(csv_filepath)
                    logger.info(f"CSV数据文件已删除: {data_files['csv_data']}")
            
            # 删除符号回归模型文件
            if 'regression_model' in data_files:
                model_filepath = os.path.join(MODELS_DIR, data_files['regression_model'])
                if os.path.exists(model_filepath):
                    os.remove(model_filepath)
                    logger.info(f"符号回归模型文件已删除: {data_files['regression_model']}")
            
            # 删除蒙特卡洛分析结果文件
            if 'monte_carlo_results' in data_files:
                results_filepath = os.path.join(RESULTS_DIR, data_files['monte_carlo_results'])
                if os.path.exists(results_filepath):
                    os.remove(results_filepath)
                    logger.info(f"蒙特卡洛分析结果文件已删除: {data_files['monte_carlo_results']}")
            
            # 删除主模型文件
            os.remove(filepath)
            logger.info(f"数据模型已删除: {filename}")
            return True
        else:
            logger.warning(f"数据模型文件不存在: {filename}")
            return False
    except Exception as e:
        logger.error(f"删除数据模型失败: {e}")
        return False

# 数据模型管理路由
@data_models_bp.route('/models', methods=['GET'])
def get_data_models():
    """获取所有数据模型列表"""
    try:
        models = load_data_models()
        
        # 按创建时间排序，最新的在前
        models.sort(key=lambda x: x.get('created_at', 0), reverse=True)
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"获取数据模型列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型列表失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['GET'])
def get_data_model(model_id):
    """获取特定数据模型详情"""
    try:
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        # 兼容：若 regression_model 文件中有 expression_latex，则覆盖主模型的 expression 字段，保持前端统一从数据库读取 MathJax
        try:
            reg_name = (model.get('data_files') or {}).get('regression_model')
            if reg_name:
                reg_path = os.path.join(MODELS_DIR, reg_name)
                if os.path.exists(reg_path):
                    with open(reg_path, 'r', encoding='utf-8') as rf:
                        reg_json = json.load(rf)
                    if isinstance(reg_json, dict) and reg_json.get('expression_latex'):
                        model.setdefault('symbolic_regression', {})['expression_latex'] = reg_json['expression_latex']
        except Exception:
            pass
        
        return jsonify({
            'success': True,
            'model': model
        })
    except Exception as e:
        logger.error(f"获取数据模型详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型详情失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>/files/<file_type>', methods=['GET'])
def get_data_model_file(model_id, file_type):
    """获取数据模型相关文件内容"""
    try:
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        data_files = model.get('data_files', {})
        
        if file_type not in ['csv_data', 'regression_model', 'monte_carlo_results', 'all_as_zip']:
            return jsonify({
                'success': False,
                'error': '不支持的文件类型'
            }), 400
        
        # 打包为 zip：包含 data_model.json、data.csv、regression.json、monte_carlo.json（若存在），统一置于 model_id/ 目录内
        if file_type == 'all_as_zip':
            in_memory = io.BytesIO()
            with zipfile.ZipFile(in_memory, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                base_dir = f"{model_id}/"
                # 写入 data_model.json（规范化）
                zf.writestr(base_dir + 'data_model.json', json.dumps(model, ensure_ascii=False, indent=2))
                # CSV → data.csv（若无则跳过）
                csv_name = data_files.get('csv_data')
                if csv_name:
                    csv_path = os.path.join(CSV_DATA_DIR, csv_name)
                    if os.path.exists(csv_path):
                        with open(csv_path, 'rb') as f:
                            zf.writestr(base_dir + 'data.csv', f.read())
                # 回归模型 JSON → regression.json（若无则跳过）
                reg_name = data_files.get('regression_model')
                if reg_name:
                    reg_path = os.path.join(MODELS_DIR, reg_name)
                    if os.path.exists(reg_path):
                        with open(reg_path, 'r', encoding='utf-8') as f:
                            zf.writestr(base_dir + 'regression.json', f.read())
                # 蒙特卡洛 JSON（可选） → monte_carlo.json
                mc_name = data_files.get('monte_carlo_results')
                if mc_name:
                    mc_path = os.path.join(RESULTS_DIR, mc_name)
                    if os.path.exists(mc_path):
                        with open(mc_path, 'r', encoding='utf-8') as f:
                            zf.writestr(base_dir + 'monte_carlo.json', f.read())

            in_memory.seek(0)
            zip_filename = f"{model_id}.zip"
            return send_file(
                in_memory,
                as_attachment=True,
                download_name=zip_filename,
                mimetype='application/zip'
            )

        # 单文件读取
        file_filename = data_files.get(file_type)
        if not file_filename:
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        if file_type == 'csv_data':
            file_path = os.path.join(CSV_DATA_DIR, file_filename)
        elif file_type == 'regression_model':
            file_path = os.path.join(MODELS_DIR, file_filename)
        elif file_type == 'monte_carlo_results':
            file_path = os.path.join(RESULTS_DIR, file_filename)

        if not os.path.exists(file_path):
            return jsonify({'success': False, 'error': '文件不存在'}), 404

        # 直接返回文件内容（文本）
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return jsonify({'success': True, 'content': content, 'filename': file_filename, 'file_type': file_type})
        
    except Exception as e:
        logger.error(f"获取数据模型文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '获取数据模型文件失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>/files/<file_type>', methods=['PUT'])
def update_data_model_file(model_id, file_type):
    """更新数据模型文件内容"""
    try:
        data = request.get_json()
        
        # 检查模型是否存在
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        # 加载模型
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        # 根据文件类型更新对应文件
        if file_type == 'regression_model':
            reg_filename = model.get('data_files', {}).get('regression_model')
            if reg_filename:
                reg_filepath = os.path.join(MODELS_DIR, reg_filename)
                if os.path.exists(reg_filepath):
                    # 读取现有内容
                    with open(reg_filepath, 'r', encoding='utf-8') as f:
                        reg_content = json.load(f)
                    
                    # 更新字段
                    if 'expression_latex' in data:
                        reg_content['expression_latex'] = data['expression_latex']
                    if 'expression' in data:
                        reg_content['expression'] = data['expression']
                    if 'constants' in data and isinstance(data['constants'], dict):
                        reg_content['constants'] = data['constants']
                    if 'feature_importance' in data and isinstance(data['feature_importance'], list):
                        reg_content['feature_importance'] = data['feature_importance']
                    if 'impact_tree' in data:
                        reg_content['impact_tree'] = data['impact_tree']
                    # 表达式树操作驱动的指标轮换/撤销
                    action = (data or {}).get('expr_tree_action')
                    # 初始化基线指标和特征权重
                    if 'baseline_detailed_metrics' not in reg_content:
                        reg_content['baseline_detailed_metrics'] = reg_content.get('detailed_metrics') or {}
                    if 'baseline_feature_importance' not in reg_content:
                        reg_content['baseline_feature_importance'] = reg_content.get('feature_importance') or []
                    op_index = int(model.get('metadata', {}).get('expr_tree_op_index', 0) or 0)
                    new_index = op_index
                    if action in ('delete', 'simplify', 'optimize'):
                        new_index = op_index + 1
                        # 超过15次：指标固定为第15次的值，但索引持续增长，确保无限撤销回滚可用
                        idx = new_index if new_index <= 15 else 15
                        if idx > 0:
                            seq_metrics = MOCK_INDICATORS_SEQUENCE[idx]
                            seq_weights = MOCK_WEIGHTS_SEQUENCE[idx]
                            # 同步：表达式树与公式（大改造 - 使用内嵌的IMPACT树序列）
                            try:
                                step_tree = MOCK_IMPACT_TREES[idx]
                                if isinstance(step_tree, dict):
                                    # 影响力嵌套结构（供前端着色/定位）
                                    reg_content['impact_tree'] = _impact_nested_from_tree(step_tree)
                                    # 表达式（文本与LaTeX）
                                    expr_text = _expr_of(step_tree)
                                    latex = _latex_of(step_tree)
                                    # 常数表（用于“常数定义”列表）
                                    consts = _constants_dict_from_tree(step_tree)
                                    reg_content['expression_text'] = expr_text
                                    reg_content['expression'] = latex  # 复用字段保持前端兼容
                                    reg_content['expression_latex'] = latex
                                    reg_content['constants'] = consts
                            except Exception as _:
                                pass
                            if isinstance(seq_metrics, dict):
                                reg_content['detailed_metrics'] = seq_metrics
                                model.setdefault('metadata', {})['pearson_r_test'] = seq_metrics.get('pearson_r_test')
                                model['metadata']['pearson_r_training'] = seq_metrics.get('pearson_r_training')
                            if isinstance(seq_weights, list):
                                reg_content['feature_importance'] = seq_weights
                        model.setdefault('metadata', {})['expr_tree_op_index'] = new_index
                    elif action == 'undo':
                        new_index = max(0, op_index - 1)
                        if new_index == 0:
                            base = reg_content.get('baseline_detailed_metrics') or {}
                            base_weights = reg_content.get('baseline_feature_importance') or []
                            if base:
                                reg_content['detailed_metrics'] = base
                                model.setdefault('metadata', {})['pearson_r_test'] = base.get('pearson_r_test')
                                model['metadata']['pearson_r_training'] = base.get('pearson_r_training')
                            if base_weights:
                                reg_content['feature_importance'] = base_weights
                            # 回到基线：如果有基线impact_tree/公式则恢复；否则保持现状
                            try:
                                base_impact = reg_content.get('baseline_impact_tree')
                                base_expr_text = reg_content.get('baseline_expression_text')
                                base_expr_latex = reg_content.get('baseline_expression_latex')
                                base_consts = reg_content.get('baseline_constants')
                                if base_impact:
                                    reg_content['impact_tree'] = base_impact
                                if base_expr_text:
                                    reg_content['expression_text'] = base_expr_text
                                if base_expr_latex:
                                    reg_content['expression'] = base_expr_latex
                                    reg_content['expression_latex'] = base_expr_latex
                                if base_consts:
                                    reg_content['constants'] = base_consts
                            except Exception:
                                pass
                        else:
                            # 对超过 15 的索引进行截断（>=15 视同第15次的指标），支持无限撤销
                            idx = new_index if new_index <= 15 else 15
                            seq_metrics = MOCK_INDICATORS_SEQUENCE[idx]
                            seq_weights = MOCK_WEIGHTS_SEQUENCE[idx]
                            try:
                                step_tree = MOCK_IMPACT_TREES[idx]
                                if isinstance(step_tree, dict):
                                    reg_content['impact_tree'] = _impact_nested_from_tree(step_tree)
                                    expr_text = _expr_of(step_tree)
                                    latex = _latex_of(step_tree)
                                    consts = _constants_dict_from_tree(step_tree)
                                    reg_content['expression_text'] = expr_text
                                    reg_content['expression'] = latex
                                    reg_content['expression_latex'] = latex
                                    reg_content['constants'] = consts
                            except Exception:
                                pass
                            if isinstance(seq_metrics, dict):
                                reg_content['detailed_metrics'] = seq_metrics
                                model.setdefault('metadata', {})['pearson_r_test'] = seq_metrics.get('pearson_r_test')
                                model['metadata']['pearson_r_training'] = seq_metrics.get('pearson_r_training')
                            if isinstance(seq_weights, list):
                                reg_content['feature_importance'] = seq_weights
                        model.setdefault('metadata', {})['expr_tree_op_index'] = new_index
                    else:
                        # 允许直接设置详细指标（不建议在表达式树操作路径外使用）
                        if 'detailed_metrics' in data and isinstance(data['detailed_metrics'], dict):
                            reg_content['detailed_metrics'] = data['detailed_metrics']
                        if 'feature_importance' in data and isinstance(data['feature_importance'], list):
                            reg_content['feature_importance'] = data['feature_importance']
                        if 'impact_tree' in data and isinstance(data['impact_tree'], dict):
                            reg_content['impact_tree'] = data['impact_tree']
                        if 'expression_text' in data and isinstance(data['expression_text'], str):
                            reg_content['expression_text'] = data['expression_text']
                        if 'expression_latex' in data and isinstance(data['expression_latex'], str):
                            reg_content['expression_latex'] = data['expression_latex']
                        if 'constants' in data and isinstance(data['constants'], dict):
                            reg_content['constants'] = data['constants']
                    if 'updated_at' in data:
                        reg_content['updated_at'] = data['updated_at']
                    
                    # 写回文件
                    with open(reg_filepath, 'w', encoding='utf-8') as f:
                        # 首次建立基线（以便无限撤销时回退）
                        if 'baseline_impact_tree' not in reg_content and reg_content.get('impact_tree'):
                            reg_content['baseline_impact_tree'] = reg_content['impact_tree']
                        if 'baseline_expression_text' not in reg_content and reg_content.get('expression_text'):
                            reg_content['baseline_expression_text'] = reg_content['expression_text']
                        if 'baseline_expression_latex' not in reg_content and reg_content.get('expression_latex'):
                            reg_content['baseline_expression_latex'] = reg_content['expression_latex']
                        if 'baseline_constants' not in reg_content and reg_content.get('constants'):
                            reg_content['baseline_constants'] = reg_content['constants']
                        json.dump(reg_content, f, ensure_ascii=False, indent=2)
                    # 若有更新元数据（pearson_r_* / expr_tree_op_index），同步保存主模型文件
                    save_data_model(model)
                    
                    logger.info(f"回归模型文件已更新: {reg_filename}")
                    return jsonify({'success': True, 'message': '回归模型文件更新成功'})
                else:
                    return jsonify({
                        'success': False,
                        'error': '回归模型文件不存在'
                    }), 404
            else:
                return jsonify({
                    'success': False,
                    'error': '回归模型文件未关联'
                }), 404
        else:
            return jsonify({
                'success': False,
                'error': f'不支持更新文件类型: {file_type}'
            }), 400
        
    except Exception as e:
        logger.error(f"更新数据模型文件失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新数据模型文件失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['DELETE'])
def delete_data_model_api(model_id):
    """删除数据模型"""
    try:
        if delete_data_model(model_id):
            return jsonify({
                'success': True,
                'message': '数据模型删除成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型删除失败'
            }), 500
    except Exception as e:
        logger.error(f"删除数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '删除数据模型失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/clear', methods=['POST'])
def clear_all_models():
    """清空所有数据模型及其关联文件（CSV/回归/蒙特卡洛）。"""
    try:
        # 安全起见，仅清空子目录文件，不删除目录本身
        for folder in [DATA_MODELS_DIR, CSV_DATA_DIR, MODELS_DIR, RESULTS_DIR]:
            if os.path.exists(folder):
                for name in os.listdir(folder):
                    file_path = os.path.join(folder, name)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.remove(file_path)
                        elif os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                    except Exception as e:
                        logger.warning(f"清理 {file_path} 失败: {e}")
        return jsonify({'success': True, 'message': '所有数据已清空'})
    except Exception as e:
        logger.error(f"清空数据失败: {e}")
        return jsonify({'success': False, 'error': '清空数据失败', 'message': str(e)}), 500

@data_models_bp.route('/import', methods=['POST'])
def import_models_zip():
    """导入一个包含一个或多个模型目录的ZIP包。支持单模型或多模型ZIP。
    规范结构：每个模型一个目录 model_xxx/，内含 data_model.json、data.csv、regression.json、monte_carlo.json(可选)。
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '缺少文件'}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        # 读取为内存Zip
        file_bytes = file.read()
        in_mem = io.BytesIO(file_bytes)
        def process_zip(zfile: zipfile.ZipFile) -> int:
            names = zfile.namelist()
            top_dirs = set([n.split('/')[0] for n in names if '/' in n]) or set()
            if not top_dirs:
                top_dirs = {''}
            count = 0
            for root in top_dirs:
                base = (root + '/') if root else ''
                try:
                    dm_path = base + 'data_model.json'
                    if dm_path not in names:
                        legacy_jsons = [n for n in names if n.startswith(base) and n.endswith('.json') and '/data_models/' not in n]
                        if legacy_jsons:
                            dm_path = legacy_jsons[0]
                        else:
                            continue
                    model_obj = json.loads(zfile.read(dm_path).decode('utf-8'))
                    model_id = model_obj.get('id') or f"model_{int(time.time())}"
                    csv_filename = f"{model_id}_data.csv"
                    reg_filename = f"{model_id}_regression.json"
                    # CSV
                    has_csv = False
                    data_csv_path_in_zip = base + 'data.csv'
                    if data_csv_path_in_zip in names:
                        with open(os.path.join(CSV_DATA_DIR, csv_filename), 'wb') as f:
                            f.write(zfile.read(data_csv_path_in_zip))
                        has_csv = True
                    # 回归
                    has_reg = False
                    reg_json_path_in_zip = base + 'regression.json'
                    if reg_json_path_in_zip in names:
                        with open(os.path.join(MODELS_DIR, reg_filename), 'w', encoding='utf-8') as f:
                            f.write(zfile.read(reg_json_path_in_zip).decode('utf-8'))
                        has_reg = True
                    # 蒙特卡洛
                    has_mc = False
                    mc_json_path_in_zip = base + 'monte_carlo.json'
                    if mc_json_path_in_zip in names:
                        mc_filename = f"{model_id}_monte_carlo.json"
                        with open(os.path.join(RESULTS_DIR, mc_filename), 'w', encoding='utf-8') as f:
                            f.write(zfile.read(mc_json_path_in_zip).decode('utf-8'))
                        has_mc = True
                    # 保存模型文件
                    model_obj['id'] = model_id
                    model_obj['data_files'] = {
                        'csv_data': csv_filename if has_csv else None,
                        'regression_model': reg_filename if has_reg else None,
                        'monte_carlo_results': (f"{model_id}_monte_carlo.json" if has_mc else None)
                    }
                    model_obj['metadata'] = model_obj.get('metadata', {})
                    model_obj['metadata']['has_csv_data'] = has_csv
                    model_obj['metadata']['has_regression_model'] = has_reg
                    model_obj['metadata']['has_monte_carlo_results'] = has_mc
                    model_obj['created_at'] = model_obj.get('created_at') or time.time()
                    model_obj['updated_at'] = time.time()
                    save_data_model(model_obj)
                    count += 1
                except Exception as ex:
                    logger.warning(f"导入模型 {root or 'root'} 失败: {ex}")
            return count

        with zipfile.ZipFile(in_mem, 'r') as zf:
            imported = process_zip(zf)
            if imported == 0:
                # 兼容"总ZIP内嵌子ZIP"的情况
                for n in zf.namelist():
                    if n.lower().endswith('.zip'):
                        try:
                            sub_bytes = io.BytesIO(zf.read(n))
                            with zipfile.ZipFile(sub_bytes, 'r') as subzf:
                                imported += process_zip(subzf)
                        except Exception as sube:
                            logger.warning(f"解析子ZIP {n} 失败: {sube}")
        return jsonify({'success': True, 'count': imported})
    except Exception as e:
        logger.error(f"导入数据包失败: {e}")
        return jsonify({'success': False, 'error': '导入失败', 'message': str(e)}), 500

@data_models_bp.route('/models', methods=['POST'])
def create_data_model():
    """创建新的数据模型"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['name', 'description', 'data_source', 'analysis_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 生成模型ID
        model_id = f"model_{int(time.time())}"
        
        # 创建数据模型
        model = {
            'id': model_id,
            'name': data['name'],
            'description': data['description'],
            'data_source': data['data_source'],
            'analysis_type': data['analysis_type'],
            'created_at': time.time(),
            'created_by': data.get('created_by', 'unknown'),
            'status': 'active',
            'symbolic_regression': data.get('symbolic_regression'),
            'monte_carlo': data.get('monte_carlo'),
            'metadata': data.get('metadata', {})
        }
        
        # 保存模型
        if save_data_model(model):
            return jsonify({
                'success': True,
                'model': model,
                'message': '数据模型创建成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"创建数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '创建数据模型失败',
            'message': str(e)
        }), 500

@data_models_bp.route('/models/<model_id>', methods=['PUT'])
def update_data_model(model_id):
    """更新数据模型"""
    try:
        data = request.get_json()
        
        # 检查模型是否存在
        filename = f"{model_id}.json"
        filepath = os.path.join(DATA_MODELS_DIR, filename)
        
        if not os.path.exists(filepath):
            return jsonify({
                'success': False,
                'error': '数据模型不存在'
            }), 404
        
        # 加载现有模型
        with open(filepath, 'r', encoding='utf-8') as f:
            model = json.load(f)
        
        # 更新模型数据（允许写入/更新 MathJax 公式、性能指标等）
        allowed_fields = ['name', 'description', 'status', 'symbolic_regression', 'monte_carlo', 'metadata', 'feature_importance']
        for field in allowed_fields:
            if field in data:
                model[field] = data[field]
        
        model['updated_at'] = time.time()
        
        # 保存更新后的模型
        if save_data_model(model):
            return jsonify({
                'success': True,
                'model': model,
                'message': '数据模型更新成功'
            })
        else:
            return jsonify({
                'success': False,
                'error': '数据模型保存失败'
            }), 500
            
    except Exception as e:
        logger.error(f"更新数据模型失败: {str(e)}")
        return jsonify({
            'success': False,
            'error': '更新数据模型失败',
            'message': str(e)
        }), 500

# 符号回归路由
@symbolic_regression_bp.route('/analyze', methods=['POST'])
def analyze():
    """符号回归分析 - 模拟数据"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['data', 'target_column', 'feature_columns']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 获取参数
        input_data = data['data']
        target_column = data['target_column']
        feature_columns = data['feature_columns']
        population_size = data.get('population_size', 100)
        generations = data.get('generations', 50)
        max_tree_depth = data.get('max_tree_depth', 35)
        max_tree_length = data.get('max_tree_length', 35)
        symbolic_expression_grammar = data.get('symbolic_expression_grammar', ['addition', 'subtraction', 'multiplication', 'division'])
        train_ratio = data.get('train_ratio', 80)
        set_seed_randomly = data.get('set_seed_randomly', False)
        seed_value = int(data.get('seed', 42))
        data_source = data.get('data_source', '数据源')
        
        logger.info(f"开始符号回归分析，目标变量: {target_column}")
        logger.info(f"特征变量: {feature_columns}")
        logger.info(f"输入数据行数: {len(input_data)}")
        logger.info(f"输入数据类型: {type(input_data)}")
        logger.info(f"输入数据内容: {input_data}")
        
        # 模拟处理时间
        time.sleep(2)
        
        # 根据随机种子参数设置随机数生成
        if not set_seed_randomly:
            # 固定模式：使用用户提供或默认的固定种子
            random.seed(seed_value)
            np.random.seed(seed_value)
            logger.info(f"使用固定随机种子: {seed_value}")
        else:
            # 随机模式：前端会下发随机生成的seed，这里也记录并使用该seed
            random.seed(seed_value)
            np.random.seed(seed_value)
            logger.info(f"使用随机种子（每次随机生成）: {seed_value}")
        
        # 生成模拟结果（改为固定的复杂表达式，便于前端验证树形展示）
        model_id = int(time.time())
        expression = (
            "(((((1.9105 * HYP + ((((0.6015 * QA + 0.42745 * HYP) + 1.2977 * CA) - (-10.458))))"
            " * (-1.9323 + -0.078141 * MA * (((-1.9323 + 1.4812 * OA) + 0.59744 * UA) + 0.60783 * UA)))"
            " / (2.9628 * VR) - 2.6756 / (0.40832 * HYP)) + (1.2192 * VR) / (5.4189 - 1.9105 * HYP))"
            " * 0.0053559 + 0.93054)"
        )

        # 对应的 LaTeX 公式（不包含 $ 包裹，直接插入 MathJax 块环境）
        # 使用正确的 MathJax 格式，包含 \cfrac 和 \text{} 等
        latex_expression = (
            r"\begin{align*} \nonumber HDL & =  \left(  \left(  \left(  \cfrac{  \left( c_{0}  \cdot\text{HYP} +  \left(  \left(  \left( c_{1}  \cdot\text{QA} + c_{2}  \cdot\text{HYP} \right)  + c_{3}  \cdot\text{CA} \right)  - c_{4} \right)  \right)  \cdot  \left( c_{5} + c_{6}  \cdot\text{MA} \cdot  \left(  \left(  \left( c_{7} + c_{8}  \cdot\text{OA} \right)  + c_{9}  \cdot\text{UA} \right)  + c_{10}  \cdot\text{UA} \right)  \right) }{c_{11}  \cdot\text{VR} }  -  \cfrac{ c_{12}}{c_{13}  \cdot\text{HYP} }  \right)  +  \cfrac{ c_{14}  \cdot\text{VR}}{ \left( c_{15} - c_{16}  \cdot\text{HYP} \right)  }  \right)  \cdot c_{17} + c_{18} \right) \end{align*}"
        )
        
        # 生成特征影响力：使用基线特征权重数据
        feature_importance = MOCK_WEIGHTS_BASELINE.copy()
        
        # 生成节点影响力数据（写死到代码中，对应树结构）
        # 注意：从上到下对应树分叉从左到右，同名节点不是同一个，要根据位置分配重要性
        # 使用逐步构建的方法，避免语法错误
        impact_tree = {}
        
        # 第一步：创建根节点
        impact_tree["Addition"] = {}
        
        # 第二步：添加第二层
        impact_tree["Addition"]["Multiplication"] = {}
        
        # 第三步：添加第三层
        impact_tree["Addition"]["Multiplication"]["Addition"] = {}
        
        # 第四步：添加第四层
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"] = {}
        
        # 第五步：添加第五层
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"] = {}
        
        # 第六步：添加第六层 - 这是缺失的关键层
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"]["Multiplication"] = {}
        
        # 第七步：添加左侧子树
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"]["Multiplication"]["Addition"] = {
            "1.9105 * HYP": 0.0157069022188682,
            "Subtraction": {
                "Addition": {
                    "Addition": {
                        "0.6015 * QA": 0.011758459632117,
                        "0.4274 * HYP": 0.00120390671170711
                    },
                    "1.2977 * CA": 0.113928459255378
                },
                "-10.458": 0
            }
        }
        
        # 第八步：添加右侧子树
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"]["Multiplication"]["Addition"]["Addition"] = {
            "-1.9323": 0,
            "Multiplication": {
                "-0.0781 * MA": 0.108972688038807,
                "Addition": {
                    "Addition": {
                        "Addition": {
                            "-1.9323": 0,
                            "1.4812 * OA": 0.00688842480665608
                        },
                        "0.5974 * UA": 0.0111402882791509
                    },
                    "0.6078 * UA": 0.0120783966067667
                }
            }
        }
        
        # 第九步：添加VR节点
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"]["2.9628 * VR"] = 0.279624923755846
        
        # 第十步：添加其他Division节点
        impact_tree["Addition"]["Multiplication"]["Addition"]["Subtraction"]["Division"]["Division"] = {
            "2.6756": 0,
            "0.4083 * HYP": 0.0763517896756712
        }
        
        # 第十一步：添加其他Division节点
        impact_tree["Addition"]["Multiplication"]["Addition"]["Division"] = {
            "1.2192 * VR": 0.0208902884673905,
            "Subtraction": {
                "5.4189": 0,
                "1.9105 * HYP": 0.21010236004585
            }
        }
        
        # 最后：添加常数节点
        impact_tree["Addition"]["Multiplication"]["0.0054"] = 0
        impact_tree["Addition"]["0.9305"] = 0
        
        # 生成预测结果
        predictions = []
        for i, row in enumerate(input_data):  # 处理所有数据行
            # 对于列表格式的数据，我们生成随机值作为预测结果
            actual = random.uniform(1.5, 3.0)
            predicted = actual + random.uniform(-0.3, 0.3)
            predictions.append({
                "actual": round(actual, 3),
                "predicted": round(predicted, 3)
            })
        
        # 生成常数 - 固定为给定的 19 个常数
        # 使用 c{index} 形式的键名，避免前端误解析为 c_0 与 c{0} 的不同含义
        constants = {
            'c{0}': 1.9105,
            'c{1}': 0.6015,
            'c{2}': 0.42745,
            'c{3}': 1.2977,
            'c{4}': -10.458,
            'c{5}': -1.9323,
            'c{6}': -0.078141,
            'c{7}': -1.9323,
            'c{8}': 1.4812,
            'c{9}': 0.59744,
            'c{10}': 0.60783,
            'c{11}': 2.9628,
            'c{12}': 2.6756,
            'c{13}': 0.40832,
            'c{14}': 1.2192,
            'c{15}': 5.4189,
            'c{16}': 1.9105,
            'c{17}': 0.0053559,
            'c{18}': 0.93054,
        }
        
        # 生成详细的性能指标（使用完整精度数据）
        detailed_metrics = {
            "average_relative_error_test": 2.74596305113801,
            "average_relative_error_training": 2.3574806852981,
            "mean_absolute_error_test": 0.020585454497077455,
            "mean_absolute_error_training": 0.018182586660249116,
            "mean_squared_error_test": 0.00073464638025446652,
            "mean_squared_error_training": 0.00053687909383770213,
            "model_depth": 14,
            "model_length": 39,
            "normalized_mean_squared_error_test": 0.14358163045309325,
            "normalized_mean_squared_error_training": 0.12666355569075077,
            "pearson_r_test": 0.86776941659869866,
            "pearson_r_training": 0.87333644430924906,
            "root_mean_squared_error_test": 0.027104360908430703,
            "root_mean_squared_error_training": 0.023170651562649292
        }
        
        result = {
            "id": model_id,
            "expression": expression,
            "expression_latex": latex_expression,
            "target_variable": "HDL",
            "constants": constants,
            "feature_importance": feature_importance,
            "impact_tree": impact_tree,
            "predictions": predictions,
            "training_time": round(random.uniform(3.0, 8.0), 1),
            "model_complexity": len(feature_columns[:min(3, len(feature_columns))]),
            "detailed_metrics": detailed_metrics,
            "analysis_params": {
                "population_size": population_size,
                "generations": generations,
                "max_tree_depth": max_tree_depth,
                "max_tree_length": max_tree_length,
                "symbolic_expression_grammar": symbolic_expression_grammar,
                "train_ratio": train_ratio,
                "set_seed_randomly": set_seed_randomly,
                "seed": seed_value,
                "seed_mode": "随机" if set_seed_randomly else "固定"
            }
        }
        
        # 自动创建数据模型
        try:
            # 生成模型ID
            model_id = f"model_{int(time.time())}"
            
            # 确定CSV文件：优先使用上传时保存的原始CSV文件
            server_csv_filename = data.get('server_csv_filename')
            csv_data = None
            if server_csv_filename:
                # 直接引用现有CSV文件，不再重构
                csv_source_path = os.path.join(CSV_DATA_DIR, server_csv_filename)
                if os.path.exists(csv_source_path):
                    # 复制为本模型专属文件名，便于打包
                    csv_filename = f"{model_id}_data.csv"
                    csv_target_path = os.path.join(CSV_DATA_DIR, csv_filename)
                    try:
                        with open(csv_source_path, 'r', encoding='utf-8') as src, open(csv_target_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                        csv_data = None  # 标记已使用文件复制
                        logger.info(f"已复制原始CSV到: {csv_filename}")
                    except Exception as e:
                        logger.error(f"复制原始CSV失败，退回到重构: {e}")
                        csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
                else:
                    logger.warning("提供的 server_csv_filename 不存在，退回到重构CSV")
                    csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
            else:
                # 后备：根据内存数据重构CSV
                csv_data = _prepare_csv_data(input_data, target_column, feature_columns)
            
            # 准备符号回归模型数据（写入 MathJax 公式 expression_latex）
            def _to_latex(expr_text, target):
                # 这里保存一份与前端一致的 MathJax 公式，使用正确的格式
                # 包含 \cfrac 和 \text{} 等，确保与API返回格式一致
                return r"\begin{align*} \nonumber HDL & =  \left(  \left(  \left(  \cfrac{  \left( c_{0}  \cdot\text{HYP} +  \left(  \left(  \left( c_{1}  \cdot\text{QA} + c_{2}  \cdot\text{HYP} \right)  + c_{3}  \cdot\text{CA} \right)  - c_{4} \right)  \right)  \cdot  \left( c_{5} + c_{6}  \cdot\text{MA} \cdot  \left(  \left(  \left( c_{7} + c_{8}  \cdot\text{OA} \right)  + c_{9}  \cdot\text{UA} \right)  + c_{10}  \cdot\text{UA} \right)  \right) }{c_{11}  \cdot\text{VR} }  -  \cfrac{ c_{12}}{c_{13}  \cdot\text{HYP} }  \right)  +  \cfrac{ c_{14}  \cdot\text{VR}}{ \left( c_{15} - c_{16}  \cdot\text{HYP} \right)  }  \right)  \cdot c_{17} + c_{18} \right) \end{align*}"
            regression_model = {
                'id': model_id,
                'expression_text': expression,
                'expression': _to_latex(expression, target_column or 'Y'),
                'expression_latex': _to_latex(expression, target_column or 'Y'),
                'target_variable': target_column,
                'constants': constants,
                'feature_importance': result['feature_importance'],
                'impact_tree': result['impact_tree'],
                'predictions': result['predictions'],
                'training_time': result['training_time'],
                'model_complexity': result['model_complexity'],
                'detailed_metrics': result['detailed_metrics'],
                'baseline_detailed_metrics': result['detailed_metrics'],
                'target_column': target_column,
                'feature_columns': feature_columns,
                'analysis_params': {
                    'population_size': population_size,
                    'generations': generations,
                    'max_tree_depth': max_tree_depth,
                    'max_tree_length': max_tree_length,
                    'symbolic_expression_grammar': symbolic_expression_grammar,
                    'train_ratio': train_ratio,
                    'set_seed_randomly': set_seed_randomly,
                    'seed': seed_value,
                    'seed_mode': '随机' if set_seed_randomly else '固定'
                },
                'created_at': time.time()
            }
            
            # 生成有区分度的模型名称
            model_name = _generate_model_name(target_column, feature_columns, data_source, "符号回归", model_id)
            
            # 生成详细的模型描述
            feature_count = len(feature_columns)
            feature_list = "、".join(feature_columns[:3])
            if feature_count > 3:
                feature_list += f"等{feature_count}个"
            
            model_description = f"基于{data_source}数据，使用{feature_list}成分预测{target_column}的符号回归模型"
            
            # 创建数据模型
            data_model = {
                'id': model_id,
                'name': model_name,
                'description': model_description,
                'analysis_type': '符号回归',
                'target_column': target_column,
                'feature_columns': feature_columns,
                'data_source': data_source,
                'created_at': time.time(),
                'updated_at': time.time(),
                'status': 'active',
                'symbolic_regression': {
                    'expression_latex': _to_latex(expression, target_column or 'Y'),
                    'feature_importance': result['feature_importance'],
                    'impact_tree': result['impact_tree']
                },
                'analysis_params': {
                    'population_size': population_size,
                    'generations': generations,
                    'max_tree_depth': max_tree_depth,
                    'max_tree_length': max_tree_length,
                    'symbolic_expression_grammar': symbolic_expression_grammar,
                    'train_ratio': train_ratio,
                    'set_seed_randomly': set_seed_randomly,
                    'seed': seed_value,
                    'seed_mode': '随机' if set_seed_randomly else '固定'
                },
                'data_files': {
                    'csv_data': f"{model_id}_data.csv",
                    'regression_model': f"{model_id}_regression.json"
                    # 'monte_carlo_results' 将在蒙特卡洛结果生成时填充
                },
                'metadata': {
                    'data_rows': len(input_data),
                    'has_csv_data': True,
                    'has_regression_model': True,
                    'has_monte_carlo_results': False,
                    'feature_count': feature_count,
                    'model_complexity': result['model_complexity'],
                    'pearson_r_test': result['detailed_metrics']['pearson_r_test'],
                    'pearson_r_training': result['detailed_metrics']['pearson_r_training'],
                    'expr_tree_op_index': 0
                }
            }
            
            # 创建相关文件
            if create_data_model_files(model_id, csv_data, regression_model, None):
                # 保存数据模型
                if save_data_model(data_model):
                    logger.info(f"数据模型创建成功: {model_id}")
                    result['data_model_id'] = model_id
                else:
                    logger.warning("数据模型保存失败")
            else:
                logger.warning("数据模型文件创建失败")
                
        except Exception as e:
            logger.error(f"创建数据模型失败: {e}")
        
        logger.info("符号回归分析完成")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"符号回归分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '分析失败',
            'message': str(e),
            'details': traceback.format_exc()
        }), 500

def _generate_model_name(target_column, feature_columns, data_source=None, analysis_type="符号回归", model_id=None):
    """生成有区分度的模型名称"""
    try:
        from datetime import datetime
        
        # 获取当前时间
        now = datetime.now()
        time_str = now.strftime("%m%d_%H%M")
        
        # 生成数据源标识
        if data_source:
            source_identifier = data_source.replace('.csv', '').replace('.xlsx', '').replace('.xls', '')
        else:
            source_identifier = "数据"
        
        # 生成特征变量摘要
        if len(feature_columns) <= 3:
            features_summary = "_".join(feature_columns)
        else:
            features_summary = f"{feature_columns[0]}_{feature_columns[1]}_{feature_columns[2]}+{len(feature_columns)-3}个"
        
        # 生成模型名称 - 使用更友好的格式
        if model_id:
            # 使用模型ID和可读描述
            model_name = f"{target_column}分析模型_{model_id}"
        else:
            # 备用格式
            model_name = f"{analysis_type}_{target_column}_{features_summary}_{source_identifier}_{time_str}"
        
        return model_name
        
    except Exception as e:
        logger.error(f"生成模型名称失败: {e}")
        # 备用名称
        return f"{analysis_type}_{target_column}_{int(time.time())}"

def _prepare_csv_data(data, target_column, feature_columns):
    """准备CSV数据字符串"""
    try:
        # 构建CSV头部
        headers = feature_columns + [target_column]
        csv_lines = [','.join(headers)]
        
        # 添加数据行
        for row in data:
            row_values = []
            for col in headers:
                value = row.get(col, 0)
                row_values.append(str(value))
            csv_lines.append(','.join(row_values))
        
        return '\n'.join(csv_lines)
    except Exception as e:
        logger.error(f"准备CSV数据失败: {e}")
        return ""

def _generate_monte_carlo_report(result, target_efficacy, iterations):
    """生成蒙特卡洛分析报告文本"""
    try:
        from datetime import datetime
        
        # 生成推荐配比方案
        recommendations = []
        components = ["QA", "NCGA", "CGA", "CCGA", "CA"]
        
        for i in range(10):
            # 生成随机配比
            ratios = []
            for j, component in enumerate(components):
                ratio = round(random.uniform(0.1, 0.4), 1)
                ratios.append(f"{component} {ratio}")
            
            # 计算预期药效（基于目标药效的随机偏差）
            expected_efficacy = target_efficacy + random.uniform(-0.5, 0.5)
            expected_efficacy = round(expected_efficacy, 1)
            
            recommendations.append({
                'ratios': ratios,
                'efficacy': expected_efficacy
            })
        
        # 按药效排序
        recommendations.sort(key=lambda x: x['efficacy'], reverse=True)
        
        # 生成报告文本
        report_lines = [
            "=" * 60,
            "中药成分配比推荐方案",
            "=" * 60,
            "",
            f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"目标药效: {target_efficacy}",
            f"采样次数: {iterations:,}",
            f"有效样本: {result['valid_samples']:,}",
            f"成功率: {result['success_rate']*100:.1f}%",
            "",
            "推荐配比方案 (按药效排序):",
            "-" * 60
        ]
        
        for i, rec in enumerate(recommendations, 1):
            ratios_str = ", ".join(rec['ratios'])
            report_lines.append(f"推荐方案 {i}: {ratios_str}, 预期药效: {rec['efficacy']}")
        
        report_lines.extend([
            "",
            "=" * 60,
            "说明: 以上推荐方案基于蒙特卡洛采样分析生成，",
            "成分含量单位为相对比例，药效单位为预期目标值。",
            "=" * 60
        ])
        
        return '\n'.join(report_lines)
        
    except Exception as e:
        logger.error(f"生成蒙特卡洛报告失败: {e}")
        return f"报告生成失败: {str(e)}"

@symbolic_regression_bp.route('/models', methods=['GET'])
def get_models():
    """获取已保存的模型列表 - 模拟数据"""
    try:
        # 生成模拟模型列表
        models = []
        for i in range(3):
            model_id = int(time.time()) - i * 3600  # 每小时一个模型
            models.append({
                "id": model_id,
                "expression": f"QA * {0.4 + i*0.1:.1f} + NCGA * {0.2 + i*0.05:.2f} + 0.1",
                "r2": round(0.75 + i * 0.05, 3),
                "created_at": datetime.now().isoformat()
            })
        
        return jsonify({
            'success': True,
            'models': models
        })
    except Exception as e:
        logger.error(f"获取模型列表失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

@symbolic_regression_bp.route('/models/<model_id>', methods=['GET'])
def get_model(model_id):
    """获取特定模型详情 - 模拟数据"""
    try:
        # 生成模拟模型详情
        model = {
            "id": int(model_id),
            "expression": "QA * 0.5 + NCGA * 0.3 + 0.1",
            "r2": 0.85,
            "mse": 0.12,
            "feature_importance": [
                {"feature": "QA", "importance": 0.8},
                {"feature": "NCGA", "importance": 0.6},
                {"feature": "CGA", "importance": 0.4}
            ],
            "predictions": [
                {"actual": 2.1, "predicted": 2.05},
                {"actual": 2.3, "predicted": 2.28}
            ],
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'model': model
        })
    except Exception as e:
        logger.error(f"获取模型详情失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 蒙特卡洛采样分析路由
@monte_carlo_bp.route('/analyze', methods=['POST'])
def monte_carlo_analyze():
    """蒙特卡洛采样配比分析 - 模拟数据"""
    try:
        data = request.get_json()
        
        # 验证必要参数
        required_fields = ['model_id', 'target_efficacy', 'iterations']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'error': '参数缺失',
                    'message': f'缺少必要参数: {field}'
                }), 400
        
        # 获取参数
        model_id = data['model_id']
        target_efficacy = data['target_efficacy']
        iterations = data['iterations']
        tolerance = data.get('tolerance', 0.1)
        component_ranges = data.get('component_ranges', {})
        
        logger.info(f"开始蒙特卡洛采样分析，模型ID: {model_id}")
        logger.info(f"目标药效: {target_efficacy}, 采样次数: {iterations}")
        
        # 模拟处理时间
        time.sleep(3)
        
        # 生成模拟结果
        analysis_id = f"mc_{int(time.time())}"
        valid_samples = int(iterations * random.uniform(0.1, 0.2))
        
        # 读取模型信息以获取目标名与特征
        target_name = "药效"
        features = ["QA", "NCGA", "CGA", "CCGA", "CA"]
        # 如果指定了数据模型，加载其特征
        try:
            filename = f"{model_id}.json"
            filepath = os.path.join(DATA_MODELS_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing_model = json.load(f)
                target_name = existing_model.get('target_column', target_name)
                features = existing_model.get('feature_columns', features) or features
        except Exception as _e:
            pass

        # 生成Top10最优样本（仅模拟）
        req_ranges = data.get('component_ranges', {}) or {}
        def sample_value(var):
            vr = req_ranges.get(var) or {}
            vmin = float(vr.get('min', 0) if vr.get('min') is not None else 0)
            vmax = vr.get('max', None)
            if vmax is None:
                # 无穷大用一个较大的上界模拟
                vmax = vmin + 1.0
            return round(random.uniform(vmin, vmax), 2)

        top10 = []
        for i in range(10):
            comps = []
            for var in features[:min(8, len(features))]:
                comps.append({"name": var, "value": sample_value(var)})
            # 让前几条更接近目标
            eff = round(target_efficacy + random.uniform(-0.1, 0.1) - i*0.02, 3)
            top10.append({"rank": i+1, "efficacy": eff, "components": comps})
        
        result = {
            "analysis_id": analysis_id,
            "iterations": iterations,
            "target_efficacy": target_efficacy,
            "tolerance": tolerance,
            "valid_samples": valid_samples,
            "success_rate": round(valid_samples / iterations, 3),
            "analysis_time": round(random.uniform(5.0, 12.0), 1),
            "top10": top10,
            "component_ranges": req_ranges,
            "target_name": target_name
        }
        
        # 自动创建或更新数据模型
        try:
            # 检查是否已有对应的数据模型
            model_id = data.get('model_id')
            if model_id:
                # 尝试更新现有模型
                filename = f"{model_id}.json"
                filepath = os.path.join(DATA_MODELS_DIR, filename)
                
                if os.path.exists(filepath):
                    with open(filepath, 'r', encoding='utf-8') as f:
                        existing_model = json.load(f)
                    
                    # 保存蒙特卡洛分析结果为 JSON 文件
                    results_filename = f"{model_id}_monte_carlo.json"
                    results_filepath = os.path.join(RESULTS_DIR, results_filename)
                    with open(results_filepath, 'w', encoding='utf-8') as f:
                        json.dump(result, f, ensure_ascii=False, indent=2)
                    
                    # 更新模型元数据
                    existing_model['updated_at'] = time.time()
                    existing_model['metadata']['has_monte_carlo_results'] = True
                    # 更新数据文件映射
                    existing_model.setdefault('data_files', {})['monte_carlo_results'] = results_filename
                    
                    if save_data_model(existing_model):
                        logger.info(f"数据模型更新成功: {model_id}")
                        result['data_model_id'] = model_id
                    else:
                        logger.warning("数据模型更新失败")
                else:
                    logger.warning(f"指定的数据模型不存在: {model_id}")
                    return jsonify({
                        'success': False,
                        'error': '指定的数据模型不存在',
                        'message': f'模型ID {model_id} 不存在'
                    }), 404
            else:
                logger.warning("未指定数据模型ID")
                return jsonify({
                    'success': False,
                    'error': '缺少数据模型ID',
                    'message': '进行蒙特卡洛采样时必须指定一个现有的数据模型'
                }), 400
                    
        except Exception as e:
            logger.error(f"更新数据模型失败: {e}")
        
        logger.info("蒙特卡洛采样分析完成")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"蒙特卡洛采样分析失败: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': '分析失败',
            'message': str(e)
        }), 500

@monte_carlo_bp.route('/results/<analysis_id>', methods=['GET'])
def get_monte_carlo_result(analysis_id):
    """获取蒙特卡洛采样分析结果 - 模拟数据"""
    try:
        # 生成模拟结果
        result = {
            "analysis_id": analysis_id,
            "iterations": 10000,
            "target_efficacy": 2.5,
            "valid_samples": 1500,
            "optimal_ranges": [
                {
                    "component": "QA",
                    "min": 0.2,
                    "max": 0.4,
                    "mean": 0.3,
                    "std": 0.05
                },
                {
                    "component": "NCGA",
                    "min": 0.1,
                    "max": 0.3,
                    "mean": 0.2,
                    "std": 0.04
                }
            ],
            "distribution": [random.uniform(0.1, 2.0) for _ in range(100)],
            "created_at": datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        logger.error(f"获取蒙特卡洛结果失败: {str(e)}")
        return jsonify({
            'error': '获取失败',
            'message': str(e)
        }), 500

# 数据处理路由
@data_bp.route('/upload', methods=['POST'])
def upload_data():
    """上传数据文件 - 真实实现"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': '文件缺失',
                'message': '请选择要上传的文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'error': '文件缺失',
                'message': '请选择要上传的文件'
            }), 400
        
        # 检查文件扩展名
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'error': '文件格式错误',
                'message': '只支持CSV格式文件'
            }), 400
        
        # 读取文件内容
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        if len(lines) < 2:
            return jsonify({
                'error': '文件格式错误',
                'message': 'CSV文件至少需要包含表头和数据行'
            }), 400
        
        # 解析CSV行，处理引号内的逗号
        def parse_csv_line(line):
            result = []
            current = ''
            in_quotes = False
            
            for char in line:
                if char == '"':
                    in_quotes = not in_quotes
                elif char == ',' and not in_quotes:
                    result.append(current)
                    current = ''
                else:
                    current += char
            
            result.append(current)
            return result
        
        # 解析表头
        headers = [h.strip() for h in parse_csv_line(lines[0])]
        # 移除列名中的多余空格
        headers = [h.strip() for h in headers]
        if len(headers) == 0:
            return jsonify({
                'error': '文件格式错误',
                'message': 'CSV文件没有有效的表头'
            }), 400
        
        # 解析数据行
        data = []
        for i in range(1, len(lines)):
            line = lines[i].strip()
            if line == '':
                continue
            
            values = parse_csv_line(line)
            row = {}
            
            for j, header in enumerate(headers):
                value = values[j].strip() if j < len(values) else ''
                # 尝试转换为数字
                try:
                    row[header] = float(value) if value else 0.0
                except ValueError:
                    row[header] = value
            
            data.append(row)
        
        # 生成预览数据（前10行）
        preview_data = data[:10] if len(data) > 10 else data
        
        # 保存原始CSV文件到服务器（保持原样）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = secure_filename(file.filename)
        server_csv_filename = f"upload_{timestamp}_{safe_name}"
        server_csv_path = os.path.join(CSV_DATA_DIR, server_csv_filename)
        try:
            with open(server_csv_path, 'w', encoding='utf-8', newline='') as out:
                out.write(content)
        except Exception as e:
            logger.error(f"保存原始CSV失败: {e}")
            return jsonify({'error': '保存失败', 'message': '服务器保存CSV失败'}), 500

        result = {
            "filename": file.filename,
            "rows": len(data),
            "columns": len(headers),
            "columns_list": headers,
            "data_preview": preview_data,
            "full_data": data,  # 包含完整数据
            "server_csv_filename": server_csv_filename
        }
        
        logger.info(f"文件上传成功: {file.filename}, 行数: {len(data)}, 列数: {len(headers)}，已保存为 {server_csv_filename}")
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'error': '上传失败',
            'message': str(e)
        }), 500

@data_bp.route('/validate', methods=['POST'])
def validate_data():
    """验证数据格式 - 模拟数据"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要验证的数据'
            }), 400
        
        # 模拟数据验证
        input_data = data['data']
        
        # 生成验证结果
        data_types = {}
        for key in input_data[0].keys():
            data_types[key] = "numeric"
        
        validation_result = {
            "is_valid": True,
            "rows": len(input_data),
            "columns": len(input_data[0]) if input_data else 0,
            "missing_values": 0,
            "outliers": random.randint(0, 5),
            "data_types": data_types
        }
        
        return jsonify({
            'success': True,
            'result': validation_result
        })
        
    except Exception as e:
        logger.error(f"数据验证失败: {str(e)}")
        return jsonify({
            'error': '验证失败',
            'message': str(e)
        }), 500

@data_bp.route('/preview', methods=['POST'])
def preview_data():
    """预览数据 - 模拟数据"""
    try:
        data = request.get_json()
        
        if 'data' not in data:
            return jsonify({
                'error': '数据缺失',
                'message': '请提供要预览的数据'
            }), 400
        
        input_data = data['data']
        
        # 生成预览数据
        preview = input_data[:5]  # 只取前5行
        
        # 生成统计信息
        statistics = {}
        for key in input_data[0].keys():
            values = [float(row.get(key, 0)) for row in input_data if row.get(key)]
            if values:
                statistics[key] = {
                    "min": round(min(values), 2),
                    "max": round(max(values), 2),
                    "mean": round(sum(values) / len(values), 2),
                    "std": round(sum((x - sum(values)/len(values))**2 for x in values) / len(values), 3)
                }
        
        result = {
            "preview": preview,
            "statistics": statistics
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"数据预览失败: {str(e)}")
        return jsonify({
            'error': '预览失败',
            'message': str(e)
        }), 500 

@symbolic_regression_bp.route('/split-plan', methods=['POST'])
def split_plan():
    """返回训练/测试划分方案（空壳模拟）"""
    try:
        data = request.get_json() or {}
        train_ratio = int(data.get('train_ratio', 80))
        test_ratio = 100 - train_ratio
        # 简单回传占比与示例行数（模拟）
        plan = {
            'train_ratio': train_ratio,
            'test_ratio': test_ratio,
            'train_rows': int(0.01 * train_ratio * 100),
            'test_rows': int(0.01 * test_ratio * 100)
        }
        return jsonify({'success': True, 'plan': plan})
    except Exception as e:
        logger.error(f"生成划分方案失败: {e}")
        return jsonify({'success': False, 'error': '生成划分方案失败', 'message': str(e)}), 500