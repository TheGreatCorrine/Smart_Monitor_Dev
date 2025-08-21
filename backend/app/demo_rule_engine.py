#!/usr/bin/env python3
"""
backend/app/demo_rule_engine.py
------------------------------------
规则引擎演示脚本
演示如何使用规则引擎进行数据监控
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径，确保能找到所有模块
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timedelta
import logging

from backend.app.entities.record import Record
from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity
from backend.app.services.RuleEngineService import RuleEngine
from backend.app.usecases.Monitor import MonitorService, default_alarm_handler


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def create_test_data():
    """创建测试数据"""
    base_time = datetime.now()
    
    # 模拟冰箱测试数据
    test_records = [
        # 正常状态
        Record(
            run_id="demo_session_001",
            ts=base_time,
            metrics={"Temperature": 4.5, "Pressure": 0.9, "Humidity": 65.0}
        ),
        # 温度开始升高
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=1),
            metrics={"Temperature": 6.2, "Pressure": 0.8, "Humidity": 68.0}
        ),
        # 温度继续升高，压力下降
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=2),
            metrics={"Temperature": 7.8, "Pressure": 0.6, "Humidity": 72.0}
        ),
        # 温度过高，压力过低
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=3),
            metrics={"Temperature": 9.5, "Pressure": 0.4, "Humidity": 75.0}
        ),
        # 温度持续过高
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=4),
            metrics={"Temperature": 9.8, "Pressure": 0.3, "Humidity": 78.0}
        ),
        # 温度持续过高，湿度也异常
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=5),
            metrics={"Temperature": 10.2, "Pressure": 0.2, "Humidity": 85.0}
        ),
    ]
    
    return test_records


def custom_alarm_handler(alarm):
    """自定义告警处理器"""
    print(f"\n🚨 告警触发!")
    print(f"   规则: {alarm.rule_name}")
    print(f"   严重程度: {alarm.severity.value.upper()}")
    print(f"   时间: {alarm.timestamp}")
    print(f"   描述: {alarm.description}")
    print(f"   传感器值: {alarm.sensor_values}")
    print("=" * 60)


def main():
    """主函数"""
    print("🧪 冰箱测试异常状态智能监测系统演示")
    print("=" * 60)
    
    # 设置日志
    setup_logging()
    
    # 创建监控服务
    monitor_service = MonitorService()
    monitor_service.add_alarm_handler(custom_alarm_handler)
    
    # 初始化服务
    try:
        # 使用相对于项目根目录的配置文件路径
        config_path = Path(__file__).parent.parent.parent / "config" / "rules.yaml"
        monitor_service.initialize(str(config_path))
        print("✓ 监控服务初始化成功")
        
        # 显示规则摘要
        print(f"✓ 规则引擎初始化成功")
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return
    
    print("\n📊 开始处理测试数据...")
    print("-" * 60)
    
    # 创建测试数据
    test_records = create_test_data()
    
    # 处理每条记录
    total_alarms = 0
    for i, record in enumerate(test_records, 1):
        print(f"\n📝 处理第 {i} 条记录:")
        print(f"   时间: {record.ts}")
        print(f"   传感器值: {record.metrics}")
        
        # 评估记录
        alarms = monitor_service.process_record(record, "demo_session_001")
        
        if alarms:
            total_alarms += len(alarms)
            print(f"   ⚠️  触发了 {len(alarms)} 个告警")
        else:
            print(f"   ✅ 无异常")
    
    print("\n" + "=" * 60)
    print(f"📈 演示完成!")
    print(f"   处理记录数: {len(test_records)}")
    print(f"   总告警数: {total_alarms}")
    print("=" * 60)


if __name__ == "__main__":
    main() 