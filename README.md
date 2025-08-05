# Smart Monitor 智能监测系统

## 🎯 项目简介

Smart Monitor 是一个基于Python的智能监测系统，支持GUI和Web两种界面，采用Clean Architecture架构设计。

## 🚀 快速开始

### 1. 环境准备
```bash
# 查看环境配置指南
docs/SETUP_GUIDE.md
```

### 2. 启动应用
```bash
# GUI模式 (推荐)
python -m backend.app --gui

# CLI模式
python -m backend.app --cli data/MPL6.dat
```

### 3. Web部署
```bash
# 查看部署指南
docs/DEPLOYMENT.md
```

## 📚 详细文档

### 🎯 用户指南
- **[用户使用指南](docs/USER_GUIDE.md)** - GUI界面的使用说明和功能介绍
- **[环境配置指南](docs/SETUP_GUIDE.md)** - Python环境配置和兼容性说明

### 🏗️ 技术文档
- **[系统架构说明](docs/ARCHITECTURE.md)** - Clean Architecture架构重构的详细说明
- **[系统部署指南](docs/DEPLOYMENT.md)** - Web系统的部署和配置说明
- **[测试指南](docs/TESTING.md)** - 测试框架和运行指南
- **[系统配置指南](docs/CONFIGURATION.md)** - 通道配置和系统设置的详细说明

## 📁 项目结构

```
Smart_Monitor_Dev/
├── backend/                   # 后端核心代码
│   ├── app/                  # 主应用模块
│   ├── entities/             # 业务实体
│   ├── usecases/             # 用例层
│   ├── controllers/          # 控制器
│   ├── adapters/             # 适配器
│   ├── services/             # 服务层
│   ├── interfaces/           # 接口定义
│   ├── di/                   # 依赖注入
│   └── infra/               # 基础设施
├── web/                      # Web应用
├── docs/                     # 项目文档
├── config/                   # 配置文件
├── data/                     # 数据文件
├── tests/                    # 测试代码
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
- **GUI**: Tkinter
- **Web**: Flask
- **测试**: pytest
- **配置**: YAML

## 📞 技术支持

如有问题或建议，请：
1. 查看相关文档
2. 检查配置文件
3. 确认环境设置
4. 提交Issue反馈

---

**项目版本**: 1.0.0  
**最后更新**: 2024-01-01  
**文档状态**: ✅ 完整 