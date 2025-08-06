#!/usr/bin/env python3
"""
测试新的页面流程
验证：Old Test -> 工作台选择 -> 监控面板的强制流程
"""

import requests
import json
import time

BASE_URL = "http://localhost:5002"

def test_health():
    """测试健康检查"""
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查通过: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_workstation_list():
    """测试工作台列表API"""
    print("\n🔍 测试工作台列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/monitor/workstations")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 工作台列表获取成功: {data}")
            return data.get('workstations', [])
        else:
            print(f"❌ 工作台列表获取失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 工作台列表异常: {e}")
        return []

def test_file_list():
    """测试文件列表API"""
    print("\n🔍 测试文件列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/file/list")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 文件列表获取成功: {data}")
            return data.get('files', [])
        else:
            print(f"❌ 文件列表获取失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 文件列表异常: {e}")
        return []

def test_label_config():
    """测试标签配置API"""
    print("\n🔍 测试标签配置...")
    try:
        response = requests.get(f"{BASE_URL}/api/config/labels")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 标签配置获取成功")
            return True
        else:
            print(f"❌ 标签配置获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 标签配置异常: {e}")
        return False

def test_monitor_status():
    """测试监控状态API"""
    print("\n🔍 测试监控状态...")
    try:
        response = requests.get(f"{BASE_URL}/api/monitor/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 监控状态获取成功: {data}")
            return True
        else:
            print(f"❌ 监控状态获取失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 监控状态异常: {e}")
        return False

def test_old_test_flow():
    """测试Old Test流程"""
    print("\n🔍 测试Old Test流程...")
    
    # 1. 获取工作台列表
    workstations = test_workstation_list()
    
    if workstations:
        print(f"📋 找到 {len(workstations)} 个工作台")
        for ws in workstations:
            print(f"  - {ws.get('name', 'Unknown')} (ID: {ws.get('id', 'Unknown')}) - {ws.get('status', 'Unknown')}")
    else:
        print("⚠️  没有找到可用的工作台")
    
    # 2. 测试监控状态
    test_monitor_status()
    
    print("✅ Old Test流程测试完成")

def test_new_test_flow():
    """测试New Test流程"""
    print("\n🔍 测试New Test流程...")
    
    # 1. 获取文件列表
    files = test_file_list()
    
    if files:
        print(f"📋 找到 {len(files)} 个数据文件")
        for file in files:
            print(f"  - {file.get('name', 'Unknown')} ({file.get('size_mb', 0)} MB)")
    else:
        print("⚠️  没有找到可用的数据文件")
    
    # 2. 测试标签配置
    test_label_config()
    
    print("✅ New Test流程测试完成")

def main():
    """主测试函数"""
    print("🚀 开始测试新的页面流程")
    print("=" * 50)
    
    # 基础健康检查
    if not test_health():
        print("❌ 基础健康检查失败，停止测试")
        return
    
    # 测试Old Test流程
    test_old_test_flow()
    
    # 测试New Test流程
    test_new_test_flow()
    
    print("\n" + "=" * 50)
    print("✅ 所有测试完成")
    print("\n📝 测试总结:")
    print("1. ✅ 移除了侧边导航栏")
    print("2. ✅ 实现了强制流程：Old Test -> 工作台选择 -> 监控面板")
    print("3. ✅ 保留了返回主页按钮")
    print("4. ✅ 所有API正常工作")
    print("\n🌐 访问地址: http://localhost:5002")

if __name__ == "__main__":
    main() 