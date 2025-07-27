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
├── backend/           # Python 后端算法
├── docs/             # 项目文档
├── scripts/          # 自动化脚本
├── 项目背景与目标.md
├── 中药配比客户端软件开发计划文档.md
└── README.md
```

## 开发环境要求

- Node.js 18.20.8+ (LTS/Hydrogen)
- Python 3.10+
- Git
- Cursor IDE (推荐)

## 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd tcm-homogenizer
```

### 2. 初始化前端

```bash
cd frontend
npm install
npm start
```

### 3. 初始化后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

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

## 开发计划

项目采用敏捷开发模式，分为以下阶段：

1. **M1 原型** (第2-4周)：核心框架搭建
2. **M2 MVP** (第5-8周)：最小可行产品
3. **M3 最终版本** (第9-11周)：完善功能和优化

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过 GitHub Issues 联系我们。 