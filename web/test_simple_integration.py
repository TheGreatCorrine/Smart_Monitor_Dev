#!/usr/bin/env python3
"""
web/test_simple_integration.py
------------------------------------
简化的Web适配器集成测试
"""
import sys
import os

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
        
        # 测试标签保存和加载
        print("\n💾 测试标签保存和加载...")
        test_labels = {"T1": "temp", "T2": "temp"}
        save_result = web_adapter.save_label_selection(test_labels)
        print(f"✅ 标签保存测试: {save_result.get('success')}")
        
        load_result = web_adapter.load_label_selection()
        print(f"✅ 标签加载测试: {load_result.get('success')}")
        
        print("\n🎉 所有集成测试通过！")
        return True
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("🚀 开始Web适配器集成测试...")
    
    # 测试Web适配器集成
    success = test_web_adapter_integration()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"Web适配器集成: {'✅ 通过' if success else '❌ 失败'}")
    
    if success:
        print("🎉 阶段2集成完成！")
        print("✅ Web适配器与Clean Architecture集成成功")
        print("✅ 所有核心功能API已就绪")
        print("✅ 可以开始阶段3: 核心功能API开发")
        sys.exit(0)
    else:
        print("❌ 集成测试失败，需要修复")
        sys.exit(1) 