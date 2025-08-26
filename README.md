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
│   └── requirements.txt      # 依赖要求
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
- **[用户使用指南](docs/USER_GUIDE.md)** - Web界面的使用说明和功能介绍
- **[环境配置指南](docs/SETUP_GUIDE.md)** - Python环境配置和兼容性说明

### 🏗️ 技术文档
- **[系统功能说明](docs/FEATURES.md)** - 系统功能特性和使用场景详解
- **[系统架构说明](docs/ARCHITECTURE.md)** - Clean Architecture架构重构的详细说明
- **[系统部署指南](docs/DEPLOYMENT.md)** - Web系统的部署和配置说明
- **[测试指南](docs/TESTING.md)** - 测试框架和运行指南
- **[系统配置指南](docs/CONFIGURATION.md)** - 通道配置和系统设置的详细说明

### 📋 配置和参数文件
- **[SigmaData数据解析对照表](docs/SigmaData_DatParser.xlsx)** - xlsx file, SigmaData提供的数据管道文件，定义了二进制.dat文件的解析规则和数据结构
- **[标签配置](docs/labels.xlsx)** - xlsx file，系统标签配置表，用于配置传感器通道channel与业务标签label的对应关系，帮助测试工程师理解数据含义
- **[SigmaData参数](docs/Parameter_file.xlsx)** - xlsx file, SigmaData系统参数配置文件，用于设定检测规则（异常检测逻辑中，规则里部分阀值不是固定的，跟随参数大小改变）
- **[通道标签匹配配置](config/label_channel_match.yaml)** - yaml file, 系统核心配置文件，定义了P、T、T1-T22、TE1-TE14、DE1-DE14等硬件通道与业务标签的映射关系
- **[告警规则配置](config/rules.yaml)** - yaml file, 智能告警系统规则配置文件，定义了温度、压力、湿度等异常检测的阈值和逻辑条件



## 🚀 开发计划

### 最高优先级（必须立即开发）

#### 1. **概念重构：Session → Task** (3-5天)
- **现状**: 代码中混用session概念，但业务是task monitoring，不需要区分用户，没有用户登陆的概念，需要重构。其中，old test和new test只做前端界面的区分，本质上都是test；当前的实现把他们区分成了两种类型的测试，重构成一个，统称为test，属性type只用于前端页面区分，后端公用所有其他属性和方法。
- **问题**: 概念不清晰，容易混淆
- **开发内容**:
  - 重命名所有session相关变量和函数
  - 统一使用task、workstation、monitoring概念
  - 更新所有相关文档

#### 2. **Clean Architecture边界情况处理** (1周)
- **现状**: 架构框架有了，但很多corner cases没考虑
- **问题**: 生产环境可能遇到未处理的情况
- **开发内容**:
  - 完善异常处理机制
  - 添加输入验证和边界检查
  - 实现错误恢复和重试机制

### 高优先级（1-2周内完成）

#### 3. **测试覆盖完善** (1周)
- **现状**: 基础测试有了，但边界情况测试不足
- **问题**: 生产环境稳定性风险
- **测试内容**:
  - 异常数据格式处理测试
  - 网络中断恢复测试
  - 大文件处理测试
  - 并发访问测试

#### 4. **测试规则完善** (1-2周)
- **现状**: 目前测试规则rules.yaml里面都是假规则，用于演示；真正的业务逻辑在docs/Rules.docx，未来会不断的完善，如果有不理解的，可以咨询
- **问题**: 无法进行真正的业务规则检测
- **开发内容**:
  - 根据rules.docx实现真正的业务规则
  - 重构规则引擎以支持真实业务逻辑
  - 更新规则配置和验证机制

#### 5. **Web界面重构** (2-3周)
- **现状**: 主要用于demo展示，代码草率
- **问题**: 用户体验差，维护困难
- **开发内容**:
  - 分离前后端架构
  - 使用React等现代框架重构
  - 重新设计UI/UX
  - 实现响应式设计


### 中优先级（2-4周内完成）

#### 6. **数据传输打通** (2-3周)
- **现状**: start simulation只能模拟，无法真正接收数据，目前的实现逻辑是：**一次性上传一个`.dat`文件，用`.offset.json`记录上次读取位置，每10秒读取一条，模拟真实的数据推送过程。但这不是真正的实时数据传输，只是本地文件的模拟读取。**
- **问题**: 需要与Central PC打通数据传输
- **开发内容**:
  - 实现文件推送接收机制
  - 建立与Central PC的数据传输通道，之前向别的事业部借了一个linux server
  - 完善实时数据处理流程
  - 优化数据传输性能

#### 7. **告警系统完善** (1-2周)
- **现状**: 基础告警功能有了，但通知方式有限
- **问题**: 告警通知不够及时和多样化
- **开发内容**:
  - 实现邮箱、企业微信、短信推送
  - 完善告警确认和处理流程
  - 添加告警历史查询和导出

#### 8. **代码英语化** (2-3周)
- **现状**: 代码中有很多中文注释、变量名、字符串等
- **问题**: 影响代码可读性和国际化标准
- **开发内容**:
  - 将所有中文代码翻译成英文
  - 确保imports和函数调用关系正确
  - 更新注释和文档为英文

### 低优先级（长期规划）

#### 9. **数据持久化** (2-3周)
- **现状**: 数据主要存储在内存中
- **问题**: 重启后数据丢失
- **开发内容**:
  - 实现数据库存储
  - 添加数据备份和恢复
  - 实现历史数据查询

#### 10. **性能优化** (1-2周)
- **现状**: 基础功能实现，但性能可能不够优化
- **问题**: 大数据量处理可能慢
- **开发内容**:
  - 优化数据处理算法
  - 实现数据缓存机制
  - 添加性能监控

---

**项目版本**: 1.0.0  
**最后更新**: 2025-08-26  
**文档状态**: ✅ 完整 
**所有作者**: Xiang, Yining (GDE-CLBP)