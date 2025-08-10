# 本草智配

一个基于 Web 技术的中药多组分均化分析系统（项目代号 tcm-homogenizer），采用前后端分离架构，支持用户管理、符号回归分析、蒙特卡洛采样等功能。

## 功能特性

- 🔐 **用户管理**: 完整的用户注册、登录、编辑功能
- 🧬 **符号回归**: 智能中药成分关系分析
- 🎲 **蒙特卡洛采样**: 中药成分配比优化推荐
- 📊 **数据管理**: 完整的数据模型管理系统
- 🎨 **现代化UI**: 响应式设计，流畅的页面切换动画
- 📱 **多平台支持**: Web版本和Electron桌面客户端

## 技术栈

- **前端**: HTML5 + CSS3 + JavaScript (原生)
- **后端**: Python Flask
- **客户端**: Electron
- **测试**: Playwright + Puppeteer

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 或 yarn

### 安装依赖

```bash
# 安装前端依赖
cd frontend && npm install

# 安装后端依赖
cd backend && pip install -r requirements.txt
```

### 启动应用

```bash
# 启动后端服务
cd backend && python main.py

# 启动前端服务
cd frontend && python -m http.server 3000

# 启动 Electron 客户端 (可选)
./scripts/start-dev.sh
```

### 访问应用

- Web版本: http://localhost:3000
- API接口: http://localhost:5000

## 项目结构

```
tcm-homogenizer/
├── frontend/                      # 前端代码
│   ├── index.html                # 主页面
│   ├── assets/                   # 静态资源
│   │   ├── diagrams/            # 流程/结构图
│   │   ├── icons/               # 图标
│   │   │   ├── app/            # 应用与品牌图标（logo/icon）
│   │   │   └── feature/        # 功能图标（数据管理、回归、蒙特卡洛等）
│   │   ├── libs/               # 前端第三方库（MathJax、polyfill等）
│   │   └── tech/               # 技术栈徽标
│   ├── styles/                   # 样式文件
│   ├── scripts/                  # 前端脚本
│   └── data/                     # 前端数据
├── backend/                       # 后端代码
│   ├── main.py                   # Flask 应用入口
│   ├── api/                      # API 接口
│   │   ├── app.py               # Flask 应用配置
│   │   ├── auth.py              # 认证模块
│   │   └── routes.py            # 路由定义
│   ├── algorithms/               # 算法模块
│   │   ├── monte_carlo.py       # 蒙特卡洛算法（占位/桩）
│   │   └── symbolic_regression.py # 符号回归算法（占位/桩）
│   ├── data_models/              # 数据模型元数据（运行期生成）
│   ├── csv_data/                 # CSV 数据文件（运行期生成）
│   ├── models/                   # 回归模型文件（运行期生成）
│   ├── results/                  # 分析结果文件（运行期生成）
│   ├── uploads/                  # 上传文件目录（运行期生成）
│   └── utils/                    # 工具模块与示例数据
├── scripts/                       # 启动脚本
│   ├── start-dev.sh             # 开发环境启动（Electron）
│   ├── stop-dev.sh              # 停止开发环境
│   └── status.sh                # 服务状态检查
├── docs/                          # 项目文档
│   ├── summaries/                # 功能实现总结
│   ├── 开发指南.md               # 开发指南
│   ├── 开发进度总结.md           # 开发进度
│   ├── Windows虚拟机打包指南.md   # Windows 打包指南
│   ├── 项目初始化总结.md         # 项目初始化
│   ├── 首页设计总结.md           # 首页设计
│   └── 开发日志.md               # 开发记录
├── .gitignore                     # Git 忽略文件
├── package.json                   # Node.js 配置
└── README.md                      # 项目说明
```

## 开发指南

详细的开发指南请参考 [docs/开发指南.md](docs/开发指南.md)

## 开发日志

项目开发历程和技术难点请参考 [docs/开发日志.md](docs/开发日志.md)

## 功能实现总结

项目功能实现总结文档位于 [docs/summaries/](docs/summaries/) 目录：

- [滚动条修复总结](docs/summaries/滚动条修复总结.md)
- [完整数据显示功能实现总结](docs/summaries/完整数据显示功能实现总结.md)
- [CSV功能实现总结](docs/summaries/CSV功能实现总结.md)
- [模型显示改进总结](docs/summaries/模型显示改进总结.md)
- [数据管理系统规范总结](docs/summaries/数据管理系统规范总结.md)
- [数据管理功能实现总结](docs/summaries/数据管理功能实现总结.md)

## 测试

```bash
# 运行端到端测试
npm test

# 运行前端测试
python -m pytest tests/
```

## 部署

### 开发环境
按照上述快速开始步骤即可启动开发环境。

### 生产环境
使用Electron打包为桌面应用：

```bash
# 打包Electron应用
npm run build
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。 