#!/usr/bin/env python3
"""
demo_rule_engine.py
------------------------------------
规则引擎演示脚本
演示如何使用规则引擎进行数据监控
"""
import sys
import os
from pathlib import Path

# 添加backend目录到Python路径
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from datetime import datetime, timedelta
import logging

from app.entities.Record import Record
from app.entities.Rule import Rule, Condition, ConditionType, Operator, Severity
from app.services.RuleEngineService import RuleEngine
from app.usecases.Monitor import MonitorService, default_alarm_handler


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
            metrics={"温度": 4.5, "压力": 0.9, "湿度": 65.0}
        ),
        # 温度开始升高
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=1),
            metrics={"温度": 6.2, "压力": 0.8, "湿度": 68.0}
        ),
        # 温度继续升高，压力下降
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=2),
            metrics={"温度": 7.8, "压力": 0.6, "湿度": 72.0}
        ),
        # 温度过高，压力过低
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=3),
            metrics={"温度": 9.5, "压力": 0.4, "湿度": 75.0}
        ),
        # 温度持续过高
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=4),
            metrics={"温度": 9.8, "压力": 0.3, "湿度": 78.0}
        ),
        # 温度持续过高，湿度也异常
        Record(
            run_id="demo_session_001",
            ts=base_time + timedelta(minutes=5),
            metrics={"温度": 10.2, "压力": 0.2, "湿度": 85.0}
        ),
    ]
    
    return test_records


def custom_alarm_handler(alarm):
    """自定义告警处理器"""
    print(f"\n🚨 告警触发!")
    print(f"   规则: {alarm.rule_name}")
    print(f"   严重程度: {alarm.severity.upper()}")
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
        monitor_service.initialize("config/rules.yaml")
        print("✓ 监控服务初始化成功")
        
        # 显示规则摘要
        summary = monitor_service.get_rule_summary()
        print(f"✓ 加载了 {summary['enabled_rules']} 条规则")
        print(f"   规则ID: {', '.join(summary['rule_ids'])}")
        
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