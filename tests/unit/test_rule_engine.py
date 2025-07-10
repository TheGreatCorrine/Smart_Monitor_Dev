"""
tests/unit/test_rule_engine.py
------------------------------------
规则引擎单元测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from datetime import datetime, timedelta

from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity
from backend.app.entities.record import Record
from backend.app.services.rule_engine import RuleEngine


class TestRuleEngine:
    """规则引擎测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.rule_engine = RuleEngine()
        self.run_id = "test_session_001"
    
    def test_threshold_condition(self):
        """测试阈值条件"""
        # 创建规则：温度 > 8.0
        rule = Rule(
            id="temp_test",
            name="温度测试",
            description="温度超过8度告警",
            conditions=[
                Condition(
                    type=ConditionType.THRESHOLD,
                    sensor="温度",
                    operator=Operator.GT,
                    value=8.0
                )
            ],
            severity=Severity.HIGH
        )
        
        self.rule_engine.load_rules([rule])
        
        # 测试正常温度
        record1 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 5.0}
        )
        alarms1 = self.rule_engine.evaluate_record(record1, self.run_id)
        assert len(alarms1) == 0
        
        # 测试异常温度
        record2 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 9.0}
        )
        alarms2 = self.rule_engine.evaluate_record(record2, self.run_id)
        assert len(alarms2) == 1
        assert alarms2[0].rule_id == "temp_test"
    
    def test_state_duration_condition(self):
        """测试状态持续时间条件"""
        # 创建规则：温度 > 6.0 持续2分钟
        rule = Rule(
            id="temp_duration_test",
            name="温度持续时间测试",
            description="温度持续过高",
            conditions=[
                Condition(
                    type=ConditionType.STATE_DURATION,
                    sensor="温度",
                    operator=Operator.GT,
                    value=6.0,
                    duration_minutes=2
                )
            ],
            severity=Severity.MEDIUM
        )
        
        self.rule_engine.load_rules([rule])
        
        # 第一次记录 - 应该不触发
        record1 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 7.0}
        )
        alarms1 = self.rule_engine.evaluate_record(record1, self.run_id)
        assert len(alarms1) == 0
        
        # 模拟时间过去1分钟 - 应该不触发
        record2 = Record(
            run_id=self.run_id,
            ts=record1.ts + timedelta(minutes=1),
            metrics={"温度": 7.0}
        )
        alarms2 = self.rule_engine.evaluate_record(record2, self.run_id)
        assert len(alarms2) == 0
        
        # 模拟时间过去3分钟 - 应该触发
        record3 = Record(
            run_id=self.run_id,
            ts=record1.ts + timedelta(minutes=3),
            metrics={"温度": 7.0}
        )
        alarms3 = self.rule_engine.evaluate_record(record3, self.run_id)
        assert len(alarms3) == 1
        assert alarms3[0].rule_id == "temp_duration_test"
    
    def test_logic_and_condition(self):
        """测试逻辑AND条件"""
        # 创建规则：温度 > 7.0 AND 压力 < 0.8
        rule = Rule(
            id="logic_and_test",
            name="逻辑AND测试",
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
                            value=7.0
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
        
        self.rule_engine.load_rules([rule])
        
        # 测试：只有温度异常 - 不触发
        record1 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 8.0, "压力": 0.9}
        )
        alarms1 = self.rule_engine.evaluate_record(record1, self.run_id)
        assert len(alarms1) == 0
        
        # 测试：只有压力异常 - 不触发
        record2 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 5.0, "压力": 0.7}
        )
        alarms2 = self.rule_engine.evaluate_record(record2, self.run_id)
        assert len(alarms2) == 0
        
        # 测试：两个条件都满足 - 触发
        record3 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 8.0, "压力": 0.7}
        )
        alarms3 = self.rule_engine.evaluate_record(record3, self.run_id)
        assert len(alarms3) == 1
        assert alarms3[0].rule_id == "logic_and_test"
    
    def test_logic_or_condition(self):
        """测试逻辑OR条件"""
        # 创建规则：温度 > 9.0 OR 压力 < 0.3
        rule = Rule(
            id="logic_or_test",
            name="逻辑OR测试",
            description="温度过高或压力过低",
            conditions=[
                Condition(
                    type=ConditionType.LOGIC_OR,
                    sensor="",
                    operator=Operator.EQ,
                    conditions=[
                        Condition(
                            type=ConditionType.THRESHOLD,
                            sensor="温度",
                            operator=Operator.GT,
                            value=9.0
                        ),
                        Condition(
                            type=ConditionType.THRESHOLD,
                            sensor="压力",
                            operator=Operator.LT,
                            value=0.3
                        )
                    ]
                )
            ],
            severity=Severity.HIGH
        )
        
        self.rule_engine.load_rules([rule])
        
        # 测试：只有温度异常 - 触发
        record1 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 10.0, "压力": 0.5}
        )
        alarms1 = self.rule_engine.evaluate_record(record1, self.run_id)
        assert len(alarms1) == 1
        assert alarms1[0].rule_id == "logic_or_test"
        
        # 测试：只有压力异常 - 触发
        record2 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 5.0, "压力": 0.2}
        )
        alarms2 = self.rule_engine.evaluate_record(record2, self.run_id)
        assert len(alarms2) == 1
        assert alarms2[0].rule_id == "logic_or_test"
        
        # 测试：两个条件都满足 - 触发
        record3 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 10.0, "压力": 0.2}
        )
        alarms3 = self.rule_engine.evaluate_record(record3, self.run_id)
        assert len(alarms3) == 1
        assert alarms3[0].rule_id == "logic_or_test"
        
        # 测试：两个条件都不满足 - 不触发
        record4 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 5.0, "压力": 0.5}
        )
        alarms4 = self.rule_engine.evaluate_record(record4, self.run_id)
        assert len(alarms4) == 0
    
    def test_complex_logic_combination(self):
        """测试复杂逻辑组合"""
        # 创建复杂规则：(温度持续>6.5持续3分钟 AND 压力<0.6) OR (温度>8.5 AND 湿度>80)
        rule = Rule(
            id="complex_test",
            name="复杂逻辑测试",
            description="复杂异常检测",
            conditions=[
                Condition(
                    type=ConditionType.LOGIC_OR,
                    sensor="",
                    operator=Operator.EQ,
                    conditions=[
                        Condition(
                            type=ConditionType.LOGIC_AND,
                            sensor="",
                            operator=Operator.EQ,
                            conditions=[
                                Condition(
                                    type=ConditionType.STATE_DURATION,
                                    sensor="温度",
                                    operator=Operator.GT,
                                    value=6.5,
                                    duration_minutes=3
                                ),
                                Condition(
                                    type=ConditionType.THRESHOLD,
                                    sensor="压力",
                                    operator=Operator.LT,
                                    value=0.6
                                )
                            ]
                        ),
                        Condition(
                            type=ConditionType.LOGIC_AND,
                            sensor="",
                            operator=Operator.EQ,
                            conditions=[
                                Condition(
                                    type=ConditionType.THRESHOLD,
                                    sensor="温度",
                                    operator=Operator.GT,
                                    value=8.5
                                ),
                                Condition(
                                    type=ConditionType.THRESHOLD,
                                    sensor="湿度",
                                    operator=Operator.GT,
                                    value=80.0
                                )
                            ]
                        )
                    ]
                )
            ],
            severity=Severity.CRITICAL
        )
        
        self.rule_engine.load_rules([rule])
        
        # 测试第一个分支：温度持续过高且压力异常
        base_time = datetime.now()
        record1 = Record(
            run_id=self.run_id,
            ts=base_time,
            metrics={"温度": 7.0, "压力": 0.5, "湿度": 60.0}
        )
        alarms1 = self.rule_engine.evaluate_record(record1, self.run_id)
        assert len(alarms1) == 0  # 第一次不触发
        
        record2 = Record(
            run_id=self.run_id,
            ts=base_time + timedelta(minutes=4),
            metrics={"温度": 7.0, "压力": 0.5, "湿度": 60.0}
        )
        alarms2 = self.rule_engine.evaluate_record(record2, self.run_id)
        assert len(alarms2) == 1  # 持续3分钟后触发
        assert alarms2[0].rule_id == "complex_test"
        
        # 测试第二个分支：温度过高且湿度异常
        record3 = Record(
            run_id=self.run_id,
            ts=datetime.now(),
            metrics={"温度": 9.0, "压力": 0.8, "湿度": 85.0}
        )
        alarms3 = self.rule_engine.evaluate_record(record3, self.run_id)
        assert len(alarms3) == 1
        assert alarms3[0].rule_id == "complex_test"


if __name__ == "__main__":
    # 运行测试
    test = TestRuleEngine()
    
    print("开始测试规则引擎...")
    
    test.setup_method()
    test.test_threshold_condition()
    print("✓ 阈值条件测试通过")
    
    test.setup_method()
    test.test_state_duration_condition()
    print("✓ 状态持续时间条件测试通过")
    
    test.setup_method()
    test.test_logic_and_condition()
    print("✓ 逻辑AND条件测试通过")
    
    test.setup_method()
    test.test_logic_or_condition()
    print("✓ 逻辑OR条件测试通过")
    
    test.setup_method()
    test.test_complex_logic_combination()
    print("✓ 复杂逻辑组合测试通过")
    
    print("所有测试通过！") 