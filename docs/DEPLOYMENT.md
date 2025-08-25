# Smart Monitor Web 内网部署指南

## 🎯 部署方案概述

本项目采用Flask轻量级框架，确保内网环境部署简单可靠。

**注意**: 当前 `web/` 目录主要用于demo演示，未来上线时将重构为独立的 `frontend/` 模块。

### 依赖最小化
- 只需要Flask核心包
- 无需数据库
- 无需复杂配置

## 📦 方案1: 预下载部署 (推荐)

### 在有网环境准备
```bash
# 1. 下载Flask包
pip download flask werkzeug -d ./packages/

# 2. 复制项目文件
cp -r web/ /path/to/internal/network/
cp -r packages/ /path/to/internal/network/
```

### 在内网环境安装
```bash
# 1. 安装Flask
pip install --no-index --find-links ./packages/ flask

# 2. 运行应用
cd web/
python app.py
```

## 🚀 方案2: 打包部署

### 在有网环境打包
```bash
# 1. 安装PyInstaller
pip install pyinstaller

# 2. 打包应用
cd web/
pyinstaller --onefile app.py

# 3. 复制到内网
cp dist/app /path/to/internal/network/
```

### 在内网环境运行
```bash
# 直接运行exe文件
./app
```

## 🔧 快速测试

### 启动应用
```bash
cd web/
python app.py
```

### 访问应用
- 主页面: http://localhost:5000
- 健康检查: http://localhost:5000/api/health
- 测试API: http://localhost:5000/api/test

### 测试脚本
```bash
python test_app.py
```

## 📋 部署检查清单

### 环境检查
- [ ] Python 3.8+ 已安装
- [ ] 网络连接正常 (仅首次安装需要)
- [ ] 端口5000未被占用

### 应用检查
- [ ] Flask应用能正常启动
- [ ] 主页面能正常访问
- [ ] API能正常响应
- [ ] 静态文件能正常加载

### 功能检查
- [ ] 健康检查API正常
- [ ] 基础测试API正常
- [ ] 页面交互正常

## 🛠️ 故障排除

### 常见问题

#### 1. 端口被占用
```bash
# 检查端口占用
lsof -i :5000

# 修改端口
python app.py --port 5001
```

#### 2. 模块导入错误
```bash
# 检查Python路径
python -c "import sys; print(sys.path)"

# 添加路径
export PYTHONPATH=$PYTHONPATH:/path/to/project
```

#### 3. 权限问题
```bash
# 检查文件权限
ls -la web/

# 修改权限
chmod +x web/app.py
```

## 📊 性能指标

### 启动时间
- 冷启动: < 3秒
- 热启动: < 1秒

### 内存占用
- 基础运行: ~50MB
- 监控运行: ~100MB

### 响应时间
- API响应: < 100ms
- 页面加载: < 500ms

## 🔒 安全考虑

### 内网安全
- 应用仅在内网运行
- 不暴露到外网
- 使用内网IP访问

### 访问控制
- 当前版本无用户认证
- 后续版本可添加简单认证

## 📈 扩展计划

### 当前版本
- ✅ 基础Flask框架
- ✅ 健康检查API
- ✅ 基础测试页面
- ✅ 集成现有Clean Architecture
- ✅ 监控功能API
- ✅ 文件管理功能

### 下一版本
- ⏳ 重构Web模块为独立frontend
- ⏳ 优化用户界面和交互
- ⏳ 增强实时数据展示

### 后续版本
- ⏳ 用户认证和权限管理
- ⏳ 高级配置功能
- ⏳ 移动端适配

## 📞 技术支持

如遇到部署问题，请检查：
1. Python版本是否兼容
2. 网络连接是否正常
3. 端口是否被占用
4. 文件权限是否正确

---

**版本**: 1.0.0  
**最后更新**: 2025-08-25  
**兼容性**: Python 3.11+, Flask 3.0+ 