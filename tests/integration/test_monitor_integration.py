"""
tests/integration/test_monitor_integration.py
------------------------------------
监控服务集成测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import tempfile
import yaml
from datetime import datetime

from backend.app.usecases.monitor_service import MonitorService, default_alarm_handler


class TestMonitorIntegration:
    """监控服务集成测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.monitor_service = MonitorService()
        self.monitor_service.add_alarm_handler(default_alarm_handler)
    
    def test_end_to_end_monitoring(self):
        """端到端监控测试"""
        # 创建临时规则配置文件
        rules_config = {
            'rules': [
                {
                    'id': 'temp_high',
                    'name': '温度过高告警',
                    'description': '冰箱温度超过设定阈值',
                    'severity': 'high',
                    'enabled': True,
                    'conditions': [
                        {
                            'type': 'threshold',
                            'sensor': '温度',
                            'operator': '>',
                            'value': 8.0
                        }
                    ]
                },
                {
                    'id': 'pressure_low',
                    'name': '压力过低告警',
                    'description': '系统压力低于安全值',
                    'severity': 'critical',
                    'enabled': True,
                    'conditions': [
                        {
                            'type': 'threshold',
                            'sensor': '压力',
                            'operator': '<',
                            'value': 0.5
                        }
                    ]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(rules_config, f)
            config_path = f.name
        
        try:
            # 初始化监控服务
            from pathlib import Path
            self.monitor_service.rule_loader.config_path = Path(config_path)
            self.monitor_service.initialize()
            
            # 验证规则加载
            summary = self.monitor_service.get_rule_summary()
            assert summary['total_rules'] == 2
            assert summary['enabled_rules'] == 2
            assert 'temp_high' in summary['rule_ids']
            assert 'pressure_low' in summary['rule_ids']
            
            print("✓ 规则加载测试通过")
            
        finally:
            # 清理临时文件
            os.unlink(config_path)
    
    def test_alarm_handling(self):
        """告警处理测试"""
        # 创建简单的规则
        from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity
        
        rule = Rule(
            id="test_alarm",
            name="测试告警",
            description="测试告警处理",
            conditions=[
                Condition(
                    type=ConditionType.THRESHOLD,
                    sensor="温度",
                    operator=Operator.GT,
                    value=5.0
                )
            ],
            severity=Severity.HIGH
        )
        
        # 手动加载规则
        self.monitor_service.rule_engine.load_rules([rule])
        
        # 创建测试记录
        from backend.app.entities.record import Record
        
        # 正常记录 - 不触发告警
        normal_record = Record(
            run_id="test_run_001",
            ts=datetime.now(),
            metrics={"温度": 3.0}
        )
        
        alarms1 = self.monitor_service.process_record(normal_record, "test_run_001")
        assert len(alarms1) == 0
        
        # 异常记录 - 触发告警
        abnormal_record = Record(
            run_id="test_run_001",
            ts=datetime.now(),
            metrics={"温度": 7.0}
        )
        
        alarms2 = self.monitor_service.process_record(abnormal_record, "test_run_001")
        assert len(alarms2) == 1
        assert alarms2[0].rule_id == "test_alarm"
        assert alarms2[0].severity == Severity.HIGH
        assert "温度" in alarms2[0].sensor_values
        
        print("✓ 告警处理测试通过")
    
    def test_multiple_conditions(self):
        """多条件测试"""
        from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity
        from backend.app.entities.record import Record
        
        # 创建复杂规则：温度 > 6.0 AND 压力 < 0.8
        rule = Rule(
            id="complex_alarm",
            name="复杂告警",
            description="温度过高且压力异常",
            conditions=[
                Condition(
                    type=ConditionType.LOGIC_AND,
                    sensor="",
                    operator=Operator.EQ,
                    conditions=[
                        Condition(
                            type=ConditionType.THRESHOLD,
                            sensor="温度",
                            operator=Operator.GT,
                            value=6.0
                        ),
                        Condition(
                            type=ConditionType.THRESHOLD,
                            sensor="压力",
                            operator=Operator.LT,
                            value=0.8
                        )
                    ]
                )
            ],
            severity=Severity.CRITICAL
        )
        
        self.monitor_service.rule_engine.load_rules([rule])
        
        # 测试各种情况
        test_cases = [
            # (温度, 压力, 期望告警数)
            (5.0, 0.9, 0),  # 都不满足
            (7.0, 0.9, 0),  # 只有温度满足
            (5.0, 0.7, 0),  # 只有压力满足
            (7.0, 0.7, 1),  # 都满足
        ]
        
        for temp, pressure, expected_alarms in test_cases:
            record = Record(
                run_id="test_run_002",
                ts=datetime.now(),
                metrics={"温度": temp, "压力": pressure}
            )
            
            alarms = self.monitor_service.process_record(record, "test_run_002")
            assert len(alarms) == expected_alarms, f"温度={temp}, 压力={pressure}, 期望告警={expected_alarms}, 实际告警={len(alarms)}"
        
        print("✓ 多条件测试通过")


if __name__ == "__main__":
    # 运行集成测试
    test = TestMonitorIntegration()
    
    print("开始集成测试...")
    
    test.setup_method()
    test.test_end_to_end_monitoring()
    
    test.setup_method()
    test.test_alarm_handling()
    
    test.setup_method()
    test.test_multiple_conditions()
    
    print("所有集成测试通过！") 