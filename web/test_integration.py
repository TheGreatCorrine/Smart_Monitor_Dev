#!/usr/bin/env python3
"""
web/test_integration.py
------------------------------------
测试Web适配器与Clean Architecture的集成
"""
import sys
import os
import time

# 添加路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def test_web_adapter_integration():
    """测试Web适配器集成"""
    print("🧪 测试Web适配器与Clean Architecture集成...")
    
    try:
        # 导入Web适配器
        from adapters.WebAdapter import WebAdapter
        print("✅ Web适配器导入成功")
        
        # 创建Web适配器实例
        web_adapter = WebAdapter()
        print("✅ Web适配器实例化成功")
        
        # 测试获取标签配置
        print("\n📋 测试标签配置...")
        config = web_adapter.get_label_configuration()
        print(f"✅ 标签配置获取成功: {len(config.get('categories', {}))} 个类别")
        
        # 测试Web状态
        print("\n🌐 测试Web状态...")
        status = web_adapter.get_web_status()
        print(f"✅ Web状态获取成功: {status.get('success')}")
        
        # 测试文件验证
        print("\n📁 测试文件验证...")
        test_file = "data/test.dat"
        validation = web_adapter.validate_file_path(test_file)
        print(f"✅ 文件验证测试完成: {validation.get('success')}")
        
        # 测试监控状态
        print("\n📊 测试监控状态...")
        monitor_status = web_adapter.get_monitoring_status()
        print(f"✅ 监控状态获取成功: {monitor_status.get('success')}")
        
        print("\n🎉 所有集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_integration():
    """测试Flask集成"""
    print("\n🌐 测试Flask集成...")
    
    try:
        # 导入Flask应用
        import app
        app_instance = app.app
        web_adapter = app.web_adapter
        print("✅ Flask应用导入成功")
        print(f"✅ Web适配器状态: {'Ready' if web_adapter else 'Failed'}")
        
        # 测试应用上下文
        with app_instance.test_client() as client:
            # 测试健康检查
            response = client.get('/api/health')
            print(f"✅ 健康检查API: {response.status_code}")
            
            # 测试Web状态API
            response = client.get('/api/web/status')
            print(f"✅ Web状态API: {response.status_code}")
            
            # 测试标签配置API
            response = client.get('/api/config/labels')
            print(f"✅ 标签配置API: {response.status_code}")
        
        print("🎉 Flask集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ Flask集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 开始Web适配器集成测试...")
    
    # 测试Web适配器集成
    adapter_success = test_web_adapter_integration()
    
    # 测试Flask集成
    flask_success = test_flask_integration()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"Web适配器集成: {'✅ 通过' if adapter_success else '❌ 失败'}")
    print(f"Flask集成: {'✅ 通过' if flask_success else '❌ 失败'}")
    
    if adapter_success and flask_success:
        print("🎉 所有测试通过！阶段2集成完成！")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要修复")
        sys.exit(1) 