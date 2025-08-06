# 中药配比客户端

一个基于Web技术的中药配比客户端软件，采用前后端分离架构，支持用户管理、中药配比计算等功能。

## 功能特性

- 🔐 **用户管理**: 完整的用户注册、登录、编辑功能
- 🏥 **中药配比**: 智能中药配方计算和优化
- 🎨 **现代化UI**: 响应式设计，流畅的页面切换动画
- 📱 **多平台支持**: Web版本和Electron桌面客户端
- 🧪 **测试完善**: 端到端测试和自动化测试流程

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
cd backend && python app.py

# 启动前端服务
cd frontend && python -m http.server 3000

# 启动Electron客户端 (可选)
./scripts/dev-start.sh
```

### 访问应用

- Web版本: http://localhost:3000
- API接口: http://localhost:5000

## 项目结构

```
tcm-homogenizer/
├── frontend/          # 前端代码
│   ├── index.html     # 主页面
│   ├── assets/        # 静态资源
│   └── styles/        # 样式文件
├── backend/           # 后端代码
│   ├── app.py         # Flask应用
│   └── models/        # 数据模型
├── scripts/           # 启动脚本
├── docs/              # 项目文档
│   ├── 开发日志.md    # 开发记录
│   └── 开发指南.md    # 开发指南
└── README.md          # 项目说明
```

## 开发指南

详细的开发指南请参考 [docs/开发指南.md](docs/开发指南.md)

## 开发日志

项目开发历程和技术难点请参考 [docs/开发日志.md](docs/开发日志.md)

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
cd frontend && npm run build
```

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至项目维护者

---

*最后更新: 2024年* 