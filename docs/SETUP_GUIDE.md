# Python 3.11 兼容性指南

## 🎯 兼容性状态

✅ **完全兼容 Python 3.11+**

所有代码已经过测试，确保在Python 3.11中正常运行。

## 🚀 安装指南

### 方法1: 使用conda (推荐)
```bash
# 创建Python 3.11环境
conda create -n smart_monitor_py311 python=3.11

# 激活环境
conda activate smart_monitor_py311

# 安装依赖
pip install -r requirements.txt
```

### 方法2: 使用pyenv
```bash
# 安装Python 3.11
pyenv install 3.11.9

# 设置本地版本
pyenv local 3.11.9

# 创建虚拟环境
python -m venv venv_py311
source venv_py311/bin/activate  # Linux/Mac
# 或
venv_py311\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 方法3: 使用官方Python
```bash
# 下载并安装Python 3.11
# https://www.python.org/downloads/release/python-3119/

# 创建虚拟环境
python3.11 -m venv venv_py311
source venv_py311/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 🧪 兼容性测试

### 运行测试脚本
```bash
# 运行兼容性测试
python test_python311_compatibility.py

# 运行单元测试
python -m pytest tests/unit/ -v

# 运行集成测试
python -m pytest tests/integration/ -v
```

### 测试GUI和CLI
```bash
# 测试GUI
python -m backend.app --gui

# 测试CLI
python -m backend.app --cli --interactive

# 测试演示脚本
python demo_rule_engine.py
```

## 📦 依赖包说明

### 核心依赖
| 包名 | 版本 | 说明 | Python 3.11兼容性 |
|------|------|------|-------------------|
| PyYAML | >=6.0,<7.0 | YAML配置文件解析 | ✅ 完全兼容 |
| pytest | >=7.0,<9.0 | 测试框架 | ✅ 完全兼容 |
| tkinter | 内置 | GUI框架 | ✅ 完全兼容 |

## 🔧 故障排除

### 常见问题

1. **tkinter导入错误**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install python3-tk
   
   # CentOS/RHEL
   sudo yum install tkinter
   
   # macOS (通常已预装)
   brew install python-tk
   ```

2. **PyYAML安装失败**
   ```bash
   # 升级pip
   pip install --upgrade pip
   
   # 重新安装
   pip install PyYAML
   ```

3. **模块导入错误**
   ```bash
   # 确保在项目根目录
   cd /path/to/Smart_Monitor_Dev
   
   # 检查Python路径
   python -c "import sys; print(sys.path)"
   ```

### 版本检查
```bash
# 检查Python版本
python --version

# 检查关键包版本
python -c "import yaml; print('PyYAML:', yaml.__version__)"
python -c "import tkinter; print('tkinter:', tkinter.TkVersion)"
```

## ✅ 总结

- **完全兼容Python 3.11+**
- **所有功能正常**
- **性能良好**
- **易于部署**

可以放心在Python 3.11环境中使用！ 