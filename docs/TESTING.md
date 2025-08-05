# 测试结构说明

## 目录结构

```
tests/
├── unit/                    # 单元测试
│   ├── test_record.py      # Record实体测试
│   ├── test_sensor_config.py # 传感器配置测试
│   └── test_rule_engine.py # 规则引擎测试
├── integration/             # 集成测试
│   ├── test_monitor_integration.py # 监控服务集成测试
│   └── test_parse_dat.py   # 数据解析集成测试
└── README.md               # 本文件
```

## 测试分类

### 单元测试 (unit/)
- **test_record.py**: 测试Record实体的基本功能
- **test_sensor_config.py**: 测试传感器配置相关实体
- **test_rule_engine.py**: 测试规则引擎的核心业务逻辑

### 集成测试 (integration/)
- **test_monitor_integration.py**: 测试监控服务的完整流程
- **test_parse_dat.py**: 测试数据文件解析功能

## 运行测试

### 运行所有测试
```bash
python run_tests.py
```

### 只运行单元测试
```bash
python run_tests.py unit
```

### 只运行集成测试
```bash
python run_tests.py integration
```

### 运行单个测试文件
```bash
python tests/unit/test_record.py
python tests/integration/test_monitor_integration.py
```

## 测试原则

- **单元测试**: 测试单个组件或函数，不依赖外部系统
- **集成测试**: 测试多个组件之间的协作，可能依赖外部文件或服务
- **测试覆盖率**: 确保核心业务逻辑有充分的测试覆盖 