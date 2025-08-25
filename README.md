# Smart Monitor and Alert System 智能监测报警系统

## 🎯 项目简介

Smart Monitor and Alert System 是一个基于Python的智能监测报警系统，支持CLI, GUI, 以及Web三种界面，采用Clean Architecture架构设计。

## 🚀 快速开始

### 1. 环境准备
```bash
# 查看环境配置指南
docs/SETUP_GUIDE.md
```

### 2. 启动应用
```bash
# CLI模式，仅测试开发使用
python -m backend.app --cli data/MPL6.dat

# GUI模式，仅测试开发使用
python -m backend.app --gui

# Web 模式（推荐），未来重点开发方向
cd web
python app.py

# 规则引擎演示(仅用于demo演示，不用于实际开发)
python -m backend.app.demo_rule_engine

```


## 📁 项目结构
`web/`主要用于demo演示，快速开发出来的，将来应当移除，只使用`backend/`和`frontend/`去进行部署。

```
Smart_Monitor_Dev/
├── backend/                   # 后端核心代码
│   ├── app/                  # 主应用模块
│   │   ├── entities/         # 业务实体
│   │   ├── usecases/         # 用例层
│   │   ├── controllers/      # 控制器
│   │   ├── adapters/         # 适配器
│   │   ├── services/         # 服务层
│   │   ├── interfaces/       # 接口定义
│   │   ├── di/               # 依赖注入
│   │   ├── infra/            # 基础设施
│   │   ├── cli.py            # 命令行界面（仅用于辅助开发）
│   │   ├── gui.py            # 图形界面（仅用于辅助开发）
│   │   ├── __main__.py       # 主程序入口
│   │   └── demo_rule_engine.py # 规则引擎演示（仅用于演示）
│   ├── __init__.py           # 包初始化
│   └── requirement.txt       # 依赖要求
├── web/                      # Web应用（主要用于demo演示）
│   ├── app.py                # Flask应用主文件
│   ├── templates/            # HTML模板
│   ├── static/               # 静态资源
│   └── adapters/             # Web适配器
├── docs/                     # 项目文档
├── config/                   # 配置文件
├── data/                     # 数据文件
├── tests/                    # 测试代码
│   ├── unit/                 # 单元测试
│   └── integration/          # 集成测试
├── frontend/                 # 前端代码（预留）
└── README.md                # 项目说明
```

## 🎯 核心功能

- **智能监测**: 实时数据监控和告警
- **双界面支持**: GUI图形界面 + Web浏览器界面
- **Clean Architecture**: 清晰的分层架构设计
- **依赖注入**: 松耦合的服务管理
- **测试覆盖**: 完整的单元测试和集成测试

## 📊 技术栈

- **后端**: Python 3.11+, Clean Architecture
- **GUI**: Tkinter (仅用于辅助开发)
- **Web**: Flask (主要界面)
- **测试**: pytest
- **配置**: YAML (PyYAML)
- **架构**: 依赖注入 (DI Container)
- **数据格式**: 二进制 .dat 文件解析

## 📚 详细文档

### 🎯 用户指南
- **[用户使用指南](docs/USER_GUIDE.md)** - GUI界面的使用说明和功能介绍
- **[环境配置指南](docs/SETUP_GUIDE.md)** - Python环境配置和兼容性说明

### 🏗️ 技术文档
- **[系统功能说明](docs/FEATURES.md)** - 系统功能特性和使用场景详解
- **[系统架构说明](docs/ARCHITECTURE.md)** - Clean Architecture架构重构的详细说明
- **[系统部署指南](docs/DEPLOYMENT.md)** - Web系统的部署和配置说明
- **[测试指南](docs/TESTING.md)** - 测试框架和运行指南
- **[系统配置指南](docs/CONFIGURATION.md)** - 通道配置和系统设置的详细说明

## 开发计划
- 重新构一下web

---

**项目版本**: 1.0.0  
**最后更新**: 2025-08-20  
**文档状态**: ✅ 完整 