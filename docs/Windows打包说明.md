# Windows打包说明

## 打包概述

我们已经成功将中药多组分均化分析客户端的M1版本打包成Windows便携版本。这个版本可以在Windows 11 x64系统上直接运行，无需复杂的安装过程。

## 打包内容

### 生成的文件结构
```
dist/
├── backend/              # Python后端文件
│   ├── api/              # API接口
│   ├── algorithms/       # 算法模块
│   ├── utils/            # 工具模块
│   ├── main.py           # 主程序
│   ├── requirements.txt  # Python依赖
│   └── start_backend.bat # 后端启动脚本
├── frontend/             # Electron前端文件
│   ├── main.js           # 主进程
│   ├── index.html        # 主界面
│   ├── scripts/          # 渲染进程脚本
│   ├── styles/           # 样式文件
│   ├── assets/           # 静态资源
│   ├── node_modules/     # Node.js依赖
│   └── package.json      # 前端配置
├── 启动程序.bat          # 主启动脚本
├── 安装依赖.bat          # 依赖安装脚本
├── 测试后端.bat          # 后端测试脚本
└── 使用说明.txt          # 使用说明
```

## 系统要求

### 必需软件
- **Windows 10/11 (x64)**
- **Python 3.10+** (需要添加到系统PATH)
- **Node.js** (需要添加到系统PATH)

### 硬件要求
- 至少 **2GB 内存**
- 至少 **1GB 磁盘空间**
- 支持 **x64 架构**

## 安装步骤

### 1. 环境准备
确保Windows机器已安装：
- Python 3.10+ (从 [python.org](https://www.python.org/downloads/) 下载)
- Node.js (从 [nodejs.org](https://nodejs.org/) 下载)

### 2. 解压文件
将打包文件解压到任意目录，例如：`C:\tcm-homogenizer`

### 3. 安装依赖
双击运行 `安装依赖.bat`，等待安装完成

### 4. 启动应用
双击运行 `启动程序.bat` 启动应用

## 使用说明

### 启动应用
1. 双击 `启动程序.bat`
2. 程序会自动检查环境
3. 安装必要的依赖
4. 启动后端服务
5. 打开Electron前端界面

### 测试后端
1. 双击 `测试后端.bat`
2. 程序会启动后端服务
3. 测试API连接
4. 显示测试结果

### 单独启动后端
1. 进入 `backend` 目录
2. 双击 `start_backend.bat`
3. 后端服务将在控制台运行

## 故障排除

### 常见问题

#### 1. Python未找到
**错误**: `❌ 错误: 未找到Python环境`
**解决**: 
- 确保已安装Python 3.10+
- 将Python添加到系统PATH
- 重启命令提示符

#### 2. Node.js未找到
**错误**: `❌ 错误: 未找到Node.js环境`
**解决**:
- 确保已安装Node.js
- 将Node.js添加到系统PATH
- 重启命令提示符

#### 3. 依赖安装失败
**错误**: `❌ 后端依赖安装失败`
**解决**:
- 检查网络连接
- 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/`
- 确保pip版本最新：`python -m pip install --upgrade pip`

#### 4. 端口被占用
**错误**: 后端服务启动失败
**解决**:
- 检查端口5000是否被占用
- 关闭其他占用端口的程序
- 修改配置文件中的端口

#### 5. 杀毒软件报警
**现象**: 杀毒软件阻止程序运行
**解决**:
- 将程序目录添加到杀毒软件白名单
- 临时关闭实时保护
- 信任程序签名

### 日志查看
程序运行日志保存在：
- 后端日志：`%TEMP%\tcm-homogenizer\logs\`
- 前端日志：在Electron开发者工具中查看

## 技术细节

### 后端技术栈
- **Python 3.13**: 主要编程语言
- **Flask**: Web框架
- **NumPy/SciPy**: 科学计算
- **PySR**: 符号回归
- **Pandas**: 数据处理

### 前端技术栈
- **Electron**: 桌面应用框架
- **HTML/CSS/JavaScript**: 界面开发
- **Node.js**: 运行时环境

### 通信机制
- **HTTP API**: 前后端通信
- **RESTful接口**: 标准API设计
- **JSON数据格式**: 数据交换

## 版本信息

- **版本**: M1 原型版本
- **构建日期**: 2025-07-27
- **Python版本**: 3.13.5
- **Node.js版本**: 20.19.4
- **Electron版本**: 37.2.4

## 更新说明

### M1版本特性
- ✅ 基础架构搭建
- ✅ 前后端通信
- ✅ 用户界面框架
- ✅ 开发工具链
- 🔄 核心算法实现（进行中）
- 🔄 数据可视化（进行中）

### 后续版本计划
- **M2版本**: 核心算法实现
- **M3版本**: 完整功能发布

## 技术支持

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 项目文档
- 开发团队邮箱

---

**注意**: 这是一个测试版本，主要用于验证基础功能和架构设计。生产环境使用前请进行充分测试。 