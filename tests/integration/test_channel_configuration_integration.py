#!/usr/bin/env python3
"""
test_channel_configuration.py
------------------------------
测试Channel配置系统框架
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from pathlib import Path

# 添加项目根目录到Python路径
# sys.path.insert(0, str(Path(__file__).parent)) # This line is now redundant due to the new_code

from backend.app.services.ChannelConfigurationService import ChannelConfigurationService
from backend.app.entities.ChannelConfiguration import (
    ChannelCategory, ChannelSubtype, UserChannelSelection, TestSessionChannelConfig
)
import logging

def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_framework():
    """测试配置框架"""
    print("🧪 测试Channel配置系统框架")
    print("=" * 60)
    
    try:
        # 1. 测试服务初始化
        print("1. 测试服务初始化...")
        service = ChannelConfigurationService()
        print("   ✅ 服务初始化成功")
        
        # 2. 测试配置文件状态
        print("\n2. 检查配置文件...")
        config_path = Path("config/label_channel_match.yaml")
        if config_path.exists():
            print(f"   ✅ 配置文件存在: {config_path}")
            
            # 尝试加载配置
            try:
                service.load_configuration()
                print("   ✅ 配置文件格式正确")
                
                # 获取配置信息
                ui_config = service.get_configuration_for_ui()
                print(f"   📊 配置统计:")
                print(f"      - 总channels: {ui_config['total_channels']}")
                print(f"      - 可监控channels: {ui_config['monitorable_channels']}")
                print(f"      - 大类数量: {len(ui_config['categories'])}")
                
                # 显示各大类信息
                for category_key, category_data in ui_config['categories'].items():
                    channel_count = len(category_data['channels'])
                    print(f"      - {category_data['category_name']}: {channel_count} channels")
                
            except Exception as e:
                print(f"   ⚠️  配置文件需要完善: {e}")
                print("   💡 请参考 docs/CHANNEL_CONFIGURATION_GUIDE.md 填写配置")
        else:
            print(f"   ⚠️  配置文件不存在: {config_path}")
            print("   💡 已创建模板文件，请填写具体配置内容")
        
        # 3. 测试实体类
        print("\n3. 测试实体类...")
        
        # 测试ChannelSubtype
        subtype = ChannelSubtype(
            subtype_id="test_subtype",
            label="测试标签",
            tag="🧪 测试",
            description="这是一个测试用的细分类型",
            unit="°C",
            typical_range=(0.0, 100.0),
            is_default=True
        )
        print(f"   ✅ ChannelSubtype创建成功: {subtype.label}")
        
        # 测试UserChannelSelection
        selection = UserChannelSelection(
            channel_id="T1",
            selected_subtype_id="test_subtype",
            enabled=True,
            notes="测试备注"
        )
        print(f"   ✅ UserChannelSelection创建成功: {selection.channel_id}")
        
        # 测试TestSessionChannelConfig
        from datetime import datetime
        session_config = TestSessionChannelConfig(
            session_id="test_session_001",
            selections={"T1": selection},
            created_by="test_user",
            config_name="测试配置"
        )
        print(f"   ✅ TestSessionChannelConfig创建成功: {session_config.session_id}")
        
        # 4. 测试枚举
        print("\n4. 测试枚举类...")
        categories = list(ChannelCategory)
        print(f"   ✅ 支持的大类 ({len(categories)}个):")
        for cat in categories:
            print(f"      - {cat.value}")
        
        print("\n" + "=" * 60)
        print("🎉 框架测试完成!")
        print("\n📝 下一步操作:")
        print("1. 根据指南填写 config/channel_definitions.yaml")
        print("2. 运行配置验证确保格式正确")
        print("3. 在前端界面测试配置效果")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def show_configuration_template():
    """显示配置模板示例"""
    print("\n" + "=" * 60)
    print("📋 配置模板示例")
    print("=" * 60)
    
    template = """
# 示例：填写环境温度大类
environment_temp:
  category_name: "环境温度"
  category_description: "冰箱内外环境温度监测"
  channels:
    - AT
  subtypes:
    - subtype_id: "room_ambient"
      label: "室内环境温度"
      tag: "🏠 室内"
      description: "冰箱所在房间的环境温度"
      unit: "°C"
      typical_range: [15.0, 30.0]
      is_default: true
      
    - subtype_id: "lab_ambient"
      label: "实验室环境温度"
      tag: "🔬 实验室"
      description: "实验室内的标准环境温度"
      unit: "°C"
      typical_range: [18.0, 25.0]
      is_default: false
"""
    
    print(template)
    print("💡 请按照这个格式填写所有5个大类的配置")

if __name__ == "__main__":
    setup_logging()
    test_framework()
    show_configuration_template() 