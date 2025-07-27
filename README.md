# 中药多组分均化分析客户端

## 项目概述

本项目旨在开发一款**跨平台客户端应用**，用于中药多组分均化分析，协助药企和科研人员优化中药配方、保证效用一致性。

### 核心功能

- **符号回归模块**：通过遗传编程自动回归出数学表达式，提供可视化的公式树图和拟合曲线
- **蒙特卡罗配比分析模块**：基于回归模型和药典标准，通过蒙特卡罗模拟确定药物配比的合理区间
- **跨平台支持**：支持 Windows 与 Linux 平台

### 技术架构

- **前端**：Electron + JavaScript/HTML/CSS
- **后端**：Python（符号回归、蒙特卡罗模拟算法）
- **通信**：HTTP/RPC 接口
- **可视化**：ECharts/D3.js

## 项目结构

```
tcm-homogenizer/
├── frontend/          # Electron 前端项目
│   ├── main.js        # 主进程
│   ├── index.html     # 主界面
│   ├── scripts/       # 渲染进程脚本
│   ├── styles/        # 样式文件
│   └── assets/        # 静态资源
├── backend/           # Python 后端算法
│   ├── api/           # API接口
│   ├── algorithms/    # 核心算法
│   ├── utils/         # 工具函数
│   ├── venv/          # Python虚拟环境
│   └── main.py        # 服务入口
├── docs/             # 项目文档
│   └── Windows虚拟机打包指南.md  # Windows打包指南
├── scripts/          # 自动化脚本
│   ├── start-dev.sh  # 启动开发环境
│   ├── stop-dev.sh   # 停止开发环境
│   └── status.sh     # 检查项目状态
├── 项目背景与目标.md
├── 中药配比客户端软件开发计划文档.md
└── README.md
```

## 开发环境要求

- **操作系统**：Linux (Arch Linux) / Windows / macOS
- **Node.js**：18.20.8+ (LTS/Hydrogen)
- **Python**：3.10+
- **Git**：最新版本
- **Cursor IDE**：推荐使用 (集成AI助手)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd tcm-homogenizer
```

### 2. 环境初始化

#### 自动初始化 (推荐)

```bash
# 运行初始化脚本
./scripts/setup-dev.sh
```

#### 手动初始化

**前端环境：**
```bash
cd frontend
npm install
```

**后端环境：**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. 启动开发环境

#### 一键启动 (推荐)

```bash
# 启动所有服务
./scripts/start-dev.sh
```

#### 分别启动

**启动后端服务：**
```bash
cd backend
source venv/bin/activate
python main.py
```

**启动前端应用：**
```bash
cd frontend
npm start
```

### 4. 验证安装

```bash
# 检查项目状态
./scripts/status.sh

# 测试后端API
curl http://127.0.0.1:5000/api/health
```

## 开发指南

### 开发环境管理

```bash
# 启动开发环境
./scripts/start-dev.sh

# 停止开发环境
./scripts/stop-dev.sh

# 检查项目状态
./scripts/status.sh

# 查看后端日志
tail -f backend/backend.log
```

### 服务访问地址

- **后端API**：http://127.0.0.1:5000
- **健康检查**：http://127.0.0.1:5000/api/health
- **前端应用**：Electron 桌面窗口

### 开发工作流

1. **启动开发环境**：`./scripts/start-dev.sh`
2. **修改代码**：使用 Cursor IDE 进行开发
3. **测试功能**：在 Electron 应用中测试
4. **查看日志**：`tail -f backend/backend.log`
5. **停止服务**：`./scripts/stop-dev.sh`

### 调试技巧

- **后端调试**：在 `backend/main.py` 中设置断点
- **前端调试**：在 Electron 中按 F12 打开开发者工具
- **API测试**：使用 curl 或 Postman 测试后端接口

## 开发规范

### Git 提交规范

本项目使用 **Conventional Commits** 规范和 **Gitmoji** 进行版本控制：

- 🎉 `feat:` 新功能
- 🐛 `fix:` 修复bug
- 📝 `docs:` 文档更新
- 🎨 `style:` 代码格式调整
- ♻️ `refactor:` 代码重构
- ⚡ `perf:` 性能优化
- ✅ `test:` 测试相关
- 🔧 `chore:` 构建过程或辅助工具的变动

### 分支管理

- `main`: 主分支，存放稳定代码
- `develop`: 开发分支，用于日常开发
- `feature/*`: 功能分支
- `hotfix/*`: 紧急修复分支

### 代码风格

- **Python**：遵循 PEP 8 规范，使用 Black 格式化
- **JavaScript**：使用 ESLint 和 Prettier
- **HTML/CSS**：保持语义化和模块化

## 开发计划

项目采用敏捷开发模式，分为以下阶段：

1. **M1 原型** (第2-4周)：核心框架搭建
   - ✅ Electron 前端框架
   - ✅ Python 后端服务
   - ✅ 前后端通信
   - 🔄 基础UI界面

2. **M2 MVP** (第5-8周)：最小可行产品
   - 🔄 符号回归算法集成
   - 🔄 蒙特卡罗模拟
   - 🔄 数据可视化
   - 🔄 用户交互功能

3. **M3 最终版本** (第9-11周)：完善功能和优化
   - 🔄 完整功能实现
   - 🔄 性能优化
   - 🔄 多平台打包
   - 🔄 用户文档

## Windows打包

### 打包方式

本项目采用**Windows虚拟机打包**的方式生成Windows安装程序。

### 打包步骤

1. **准备Windows虚拟机**：
   - Windows 10/11 (x64)
   - 安装Python 3.10+、Node.js、Git
   - 确保网络连接稳定

2. **获取项目代码**：
   - 将项目复制到Windows虚拟机中
   - 或从Git仓库克隆

3. **执行打包**：
   - 按照 `docs/Windows虚拟机打包指南.md` 进行操作
   - 生成Windows安装程序

### 打包结果

打包完成后会生成：
- `中药多组分均化分析客户端 Setup.exe` - Windows安装程序
- 支持一键安装和卸载
- 自动创建桌面和开始菜单快捷方式

## 常见问题

### Q: 后端服务启动失败
A: 检查 Python 虚拟环境是否正确激活，确保所有依赖已安装

### Q: 前端应用无法启动
A: 确保 Node.js 版本正确，并已安装所有 npm 依赖

### Q: 端口被占用
A: 使用 `./scripts/stop-dev.sh` 停止所有服务，或修改配置文件中的端口

### Q: 虚拟环境问题
A: 删除 `backend/venv` 目录，重新运行 `./scripts/setup-dev.sh`

### Q: Windows打包失败
A: 参考 `docs/Windows虚拟机打包指南.md` 进行故障排除

## 项目状态

### 当前版本：M1 原型版本

**已完成功能：**
- ✅ 基础架构搭建
- ✅ 前后端通信
- ✅ 用户界面框架
- ✅ 开发工具链
- ✅ Windows虚拟机打包指南

**进行中功能：**
- 🔄 核心算法实现
- 🔄 数据可视化

**计划功能：**
- 📋 符号回归算法集成
- 📋 蒙特卡罗模拟
- 📋 完整用户交互
- 📋 性能优化

---

**注意**：这是一个私有项目，用于参加比赛。请勿对外分享或使用。 