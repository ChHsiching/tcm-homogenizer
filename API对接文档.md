# API对接文档

## 前端API需求分析

### 1. 符号回归分析 API

**前端调用位置**: `performSymbolicRegression()`
**API端点**: `POST /api/regression/analyze`
**请求参数**:
```javascript
{
  "data": [...], // 数据数组
  "target_column": "HDL", // 目标列名
  "feature_columns": ["QA", "NCGA", ...], // 特征列名数组
  "population_size": 100, // 种群大小
  "generations": 50, // 代数
  "test_ratio": 0.3 // 测试比例
}
```

**期望响应**:
```javascript
{
  "success": true,
  "result": {
    "id": 1234567890,
    "expression": "QA * 0.5 + NCGA * 0.3 + 0.1",
    "r2": 0.85,
    "mse": 0.12,
    "feature_importance": [
      {"feature": "QA", "importance": 0.8},
      {"feature": "NCGA", "importance": 0.6}
    ],
    "predictions": [
      {"actual": 1.2, "predicted": 1.1},
      {"actual": 2.1, "predicted": 2.0}
    ]
  }
}
```

### 2. 蒙特卡罗分析 API

**前端调用位置**: `performMonteCarloAnalysis()`
**API端点**: `POST /api/monte-carlo/analyze`
**请求参数**:
```javascript
{
  "model_id": 1234567890, // 模型ID
  "iterations": 1000, // 迭代次数
  "target_efficacy": 0.8, // 目标药效
  "tolerance": 0.1 // 容差
}
```

**期望响应**:
```javascript
{
  "success": true,
  "result": {
    "iterations": 1000,
    "target_efficacy": 0.8,
    "tolerance": 0.1,
    "valid_samples": 850,
    "success_rate": 0.85,
    "analysis_time": 2.5,
    "optimal_ranges": [
      {"component": "QA", "min": 0.1, "max": 0.3, "mean": 0.2},
      {"component": "NCGA", "min": 0.2, "max": 0.4, "mean": 0.3}
    ]
  }
}
```

### 3. 数据上传 API

**前端调用位置**: `handleFileUpload()`
**API端点**: `POST /api/data/upload`
**请求参数**: FormData 或 JSON
**期望响应**:
```javascript
{
  "success": true,
  "result": {
    "rows": 60,
    "columns": 22,
    "column_names": ["QA", "NCGA", "CGA", ...],
    "data_preview": [...]
  }
}
```

### 4. 健康检查 API

**前端调用位置**: `testBackendConnection()`
**API端点**: `GET /api/health`
**期望响应**:
```javascript
{
  "status": "healthy",
  "service": "中药多组分均化分析后端",
  "version": "1.0.0"
}
```

## 后端API实现计划

### 需要保留的API端点

1. `GET /api/health` - 健康检查
2. `POST /api/regression/analyze` - 符号回归分析
3. `POST /api/monte-carlo/analyze` - 蒙特卡罗分析
4. `POST /api/data/upload` - 数据上传

### 需要删除的后端逻辑

1. 所有算法实现文件
2. 数据处理逻辑
3. 模型保存/加载逻辑
4. 复杂的计算逻辑

### 保留的空壳结构

1. Flask应用框架
2. 路由定义
3. 请求参数验证
4. 响应格式定义
5. 错误处理

## 实现步骤

1. 清理后端算法逻辑
2. 保留API路由框架
3. 实现模拟数据返回
4. 测试前后端对接
5. 验证API响应格式 