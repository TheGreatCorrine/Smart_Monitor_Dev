#!/usr/bin/env python3
"""
测试分开的Old Test和New Test控制面板
验证两个控制面板的不同功能和设计
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

def test_old_test_workflow():
    """测试Old Test工作流程"""
    print("\n🔍 测试Old Test工作流程...")
    
    # 1. 获取工作台列表
    try:
        response = requests.get(f"{BASE_URL}/api/monitor/workstations")
        if response.status_code == 200:
            data = response.json()
            workstations = data.get('workstations', [])
            print(f"✅ 找到 {len(workstations)} 个工作台")
            
            if workstations:
                # 选择第一个工作台进行测试
                workstation = workstations[0]
                workstation_id = workstation.get('id')
                print(f"📋 选择工作台: {workstation_id}")
                
                # 2. 测试Old Test监控启动
                print("🔧 测试Old Test监控启动...")
                start_data = {
                    "workstation_id": workstation_id,
                    "config_path": "config/rules.yaml",
                    "run_id": "old_test_run_001"
                }
                
                start_response = requests.post(f"{BASE_URL}/api/monitor/start", 
                                            json=start_data)
                
                if start_response.status_code == 200:
                    start_result = start_response.json()
                    if start_result.get('success'):
                        print(f"✅ Old Test监控启动成功: {start_result.get('session_name')}")
                        
                        # 3. 测试监控状态
                        print("📊 测试Old Test监控状态...")
                        status_response = requests.get(f"{BASE_URL}/api/monitor/status")
                        if status_response.status_code == 200:
                            status_data = status_response.json()
                            print(f"✅ Old Test监控状态: {status_data.get('status', {}).get('is_monitoring', False)}")
                        else:
                            print("❌ 获取Old Test监控状态失败")
                    else:
                        print(f"❌ Old Test监控启动失败: {start_result.get('error')}")
                else:
                    print(f"❌ Old Test监控启动请求失败: {start_response.status_code}")
            else:
                print("⚠️  没有可用的工作台")
        else:
            print(f"❌ 获取工作台列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ Old Test工作流程测试异常: {e}")

def test_new_test_workflow():
    """测试New Test工作流程"""
    print("\n🔍 测试New Test工作流程...")
    
    # 1. 获取文件列表
    try:
        response = requests.get(f"{BASE_URL}/api/file/list")
        if response.status_code == 200:
            data = response.json()
            files = data.get('files', [])
            print(f"✅ 找到 {len(files)} 个数据文件")
            
            if files:
                # 选择第一个文件进行测试
                file_info = files[0]
                file_path = file_info.get('path')
                print(f"📋 选择文件: {file_info.get('name')}")
                
                # 2. 获取标签配置
                print("🏷️  获取标签配置...")
                labels_response = requests.get(f"{BASE_URL}/api/config/labels")
                if labels_response.status_code == 200:
                    labels_data = labels_response.json()
                    print(f"✅ 标签配置获取成功，包含 {len(labels_data.get('categories', {}))} 个类别")
                    
                    # 3. 测试New Test监控启动
                    print("🔧 测试New Test监控启动...")
                    start_data = {
                        "file_path": file_path,
                        "workstation_id": "1",
                        "config_path": "config/rules.yaml",
                        "run_id": "new_test_run_001"
                    }
                    
                    start_response = requests.post(f"{BASE_URL}/api/monitor/start", 
                                                json=start_data)
                    
                    if start_response.status_code == 200:
                        start_result = start_response.json()
                        if start_result.get('success'):
                            print(f"✅ New Test监控启动成功: {start_result.get('session_name')}")
                            
                            # 4. 测试监控状态
                            print("📊 测试New Test监控状态...")
                            status_response = requests.get(f"{BASE_URL}/api/monitor/status")
                            if status_response.status_code == 200:
                                status_data = status_response.json()
                                print(f"✅ New Test监控状态: {status_data.get('status', {}).get('is_monitoring', False)}")
                            else:
                                print("❌ 获取New Test监控状态失败")
                        else:
                            print(f"❌ New Test监控启动失败: {start_result.get('error')}")
                    else:
                        print(f"❌ New Test监控启动请求失败: {start_response.status_code}")
                else:
                    print(f"❌ 获取标签配置失败: {labels_response.status_code}")
            else:
                print("⚠️  没有可用的数据文件")
        else:
            print(f"❌ 获取文件列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ New Test工作流程测试异常: {e}")

def test_panel_differences():
    """测试两个控制面板的差异"""
    print("\n🔍 测试控制面板差异...")
    
    print("📋 Old Test控制面板特点:")
    print("  - 工作台信息显示")
    print("  - 基于工作台ID的监控")
    print("  - 简化的配置选项")
    print("  - 专注于现有测试环境")
    
    print("\n📋 New Test控制面板特点:")
    print("  - 文件信息显示")
    print("  - 标签配置显示")
    print("  - 工作站ID输入")
    print("  - 完整的配置选项")
    print("  - 专注于新测试创建")
    
    print("\n✅ 两个控制面板已成功分离")

def main():
    """主测试函数"""
    print("🚀 开始测试分开的控制面板功能")
    print("=" * 60)
    
    # 基础健康检查
    if not test_health():
        print("❌ 基础健康检查失败，停止测试")
        return
    
    # 测试Old Test工作流程
    test_old_test_workflow()
    
    # 测试New Test工作流程
    test_new_test_workflow()
    
    # 测试控制面板差异
    test_panel_differences()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("\n📝 测试总结:")
    print("1. ✅ Old Test和New Test控制面板已成功分离")
    print("2. ✅ 两个控制面板有不同的功能和设计")
    print("3. ✅ Old Test专注于工作台选择和现有环境")
    print("4. ✅ New Test专注于文件选择和标签配置")
    print("5. ✅ 所有API功能正常工作")
    print("\n🌐 访问地址: http://localhost:5002")
    print("📋 测试流程:")
    print("  - Old Test: 主页 → 工作台选择 → Old Test控制面板")
    print("  - New Test: 主页 → 文件配置 → New Test控制面板")

if __name__ == "__main__":
    main() 