# API文档

## 概述

中药多组分均化分析客户端API文档，定义了前端与后端之间的通信接口。

## 基础信息

- **基础URL**: `http://127.0.0.1:5000`
- **协议**: HTTP/1.1
- **数据格式**: JSON
- **字符编码**: UTF-8

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "result": {
    // 具体数据
  }
}
```

### 错误响应
```json
{
  "error": "错误类型",
  "message": "错误描述"
}
```

## API端点

### 1. 健康检查

#### GET /api/health
检查后端服务状态

**响应示例**:
```json
{
  "status": "healthy",
  "service": "中药多组分均化分析后端",
  "version": "1.0.0"
}
```

### 2. 数据上传

#### POST /api/data/upload
上传数据文件

**请求参数**:
- `file`: 文件对象 (multipart/form-data)

**响应示例**:
```json
{
  "success": true,
  "result": {
    "filename": "data.csv",
    "rows": 60,
    "columns": 22,
    "columns_list": ["QA", "NCGA", "CGA", "CCGA", "CA", "PIS", "HYP", "AST", "GUA", "RUT", "VR", "VG", "PB2", "PC1", "EPI", "OA", "UA", "MA", "CRA", "QUE", "MDA", "HDL"],
    "data_preview": [
      {"QA": 1.2, "NCGA": 0.8, "HDL": 2.1},
      {"QA": 1.5, "NCGA": 1.1, "HDL": 2.3}
    ]
  }
}
```

### 3. 符号回归分析

#### POST /api/regression/analyze
执行符号回归分析

**请求参数**:
```json
{
  "data": [
    {"QA": 1.2, "NCGA": 0.8, "HDL": 2.1},
    {"QA": 1.5, "NCGA": 1.1, "HDL": 2.3}
  ],
  "target_column": "HDL",
  "feature_columns": ["QA", "NCGA", "CGA"],
  "population_size": 100,
  "generations": 50,
  "test_ratio": 0.3,
  "operators": ["+", "-", "*", "/"]
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "id": 1234567890,
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
    "training_time": 5.2,
    "model_complexity": 3
  }
}
```

#### GET /api/regression/models
获取已保存的模型列表

**响应示例**:
```json
{
  "success": true,
  "models": [
    {
      "id": 1234567890,
      "expression": "QA * 0.5 + NCGA * 0.3 + 0.1",
      "r2": 0.85,
      "created_at": "2025-08-03T19:00:00Z"
    }
  ]
}
```

#### GET /api/regression/models/{model_id}
获取特定模型详情

**响应示例**:
```json
{
  "success": true,
  "model": {
    "id": 1234567890,
    "expression": "QA * 0.5 + NCGA * 0.3 + 0.1",
    "r2": 0.85,
    "mse": 0.12,
    "feature_importance": [...],
    "predictions": [...],
    "created_at": "2025-08-03T19:00:00Z"
  }
}
```

### 4. 蒙特卡罗分析

#### POST /api/monte-carlo/analyze
执行蒙特卡罗配比分析

**请求参数**:
```json
{
  "model_id": 1234567890,
  "target_efficacy": 2.5,
  "iterations": 10000,
  "tolerance": 0.1,
  "component_ranges": {
    "QA": {"min": 0.1, "max": 2.0},
    "NCGA": {"min": 0.1, "max": 1.5},
    "CGA": {"min": 0.05, "max": 1.0}
  }
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "analysis_id": "mc_1234567890",
    "iterations": 10000,
    "target_efficacy": 2.5,
    "tolerance": 0.1,
    "valid_samples": 1500,
    "success_rate": 0.15,
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
    "distribution": [0.25, 0.28, 0.31, ...],
    "analysis_time": 8.5
  }
}
```

#### GET /api/monte-carlo/results/{analysis_id}
获取蒙特卡罗分析结果

**响应示例**:
```json
{
  "success": true,
  "result": {
    "analysis_id": "mc_1234567890",
    "iterations": 10000,
    "target_efficacy": 2.5,
    "valid_samples": 1500,
    "optimal_ranges": [...],
    "distribution": [...],
    "created_at": "2025-08-03T19:00:00Z"
  }
}
```

### 5. 数据验证

#### POST /api/data/validate
验证数据格式

**请求参数**:
```json
{
  "data": [
    {"QA": 1.2, "NCGA": 0.8, "HDL": 2.1},
    {"QA": 1.5, "NCGA": 1.1, "HDL": 2.3}
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "is_valid": true,
    "rows": 60,
    "columns": 22,
    "missing_values": 0,
    "outliers": 2,
    "data_types": {
      "QA": "numeric",
      "NCGA": "numeric",
      "HDL": "numeric"
    }
  }
}
```

### 6. 数据预览

#### POST /api/data/preview
生成数据预览

**请求参数**:
```json
{
  "data": [
    {"QA": 1.2, "NCGA": 0.8, "HDL": 2.1},
    {"QA": 1.5, "NCGA": 1.1, "HDL": 2.3}
  ]
}
```

**响应示例**:
```json
{
  "success": true,
  "result": {
    "preview": [
      {"QA": 1.2, "NCGA": 0.8, "HDL": 2.1},
      {"QA": 1.5, "NCGA": 1.1, "HDL": 2.3}
    ],
    "statistics": {
      "QA": {"min": 0.1, "max": 2.0, "mean": 1.2, "std": 0.3},
      "NCGA": {"min": 0.1, "max": 1.5, "mean": 0.8, "std": 0.2},
      "HDL": {"min": 1.5, "max": 3.0, "mean": 2.2, "std": 0.4}
    }
  }
}
```

## 错误代码

| 状态码 | 错误类型 | 描述 |
|--------|----------|------|
| 400 | 参数错误 | 请求参数缺失或格式错误 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器错误 | 服务器内部错误 |

## 前端调用示例

### JavaScript Fetch API

```javascript
// 健康检查
async function checkHealth() {
  const response = await fetch('http://127.0.0.1:5000/api/health');
  return await response.json();
}

// 符号回归分析
async function performRegression(params) {
  const response = await fetch('http://127.0.0.1:5000/api/regression/analyze', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params)
  });
  return await response.json();
}

// 文件上传
async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch('http://127.0.0.1:5000/api/data/upload', {
    method: 'POST',
    body: formData
  });
  return await response.json();
}
```

## 注意事项

1. 所有API调用都应该包含错误处理
2. 文件上传支持CSV、Excel格式
3. 数据应该包含数值型列
4. 符号回归分析可能需要较长时间
5. 蒙特卡罗分析建议迭代次数不超过10000次 