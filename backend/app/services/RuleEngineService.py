"""
backend/app/services/RuleEngineService.py
------------------------------------
应用服务层：规则引擎，实现规则评估和告警生成的核心业务逻辑
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
import logging

from ..entities.Rule import Rule, Condition, ConditionType, Operator, Severity
from ..entities.AlarmEvent import AlarmEvent
from ..entities.Record import Record


class RuleEngine:
    """
    规则引擎
    
    负责评估规则条件，生成告警事件
    支持阈值判断、状态持续时间判断和逻辑组合
    """
    
    def __init__(self):
        self.rules: List[Rule] = []
        self.sensor_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.state_duration: Dict[str, Dict[str, datetime]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
    
    def load_rules(self, rules: List[Rule]):
        """加载规则"""
        self.rules = [rule for rule in rules if rule.enabled]
        self.logger.info(f"加载了 {len(self.rules)} 条规则")
    
    def evaluate_record(self, record: Record, run_id: str) -> List[AlarmEvent]:
        """
        评估单条记录，返回触发的告警事件
        
        Parameters
        ----------
        record : Record
            传感器记录
        run_id : str
            测试会话ID
            
        Returns
        -------
        List[AlarmEvent]
            触发的告警事件列表
        """
        # 更新传感器历史数据
        self._update_sensor_history(record)
        
        # 评估所有规则
        alarms = []
        for rule in self.rules:
            if self._evaluate_rule(rule, record):
                alarm = self._create_alarm_event(rule, record, run_id)
                if alarm:
                    alarms.append(alarm)
        
        return alarms
    
    def _update_sensor_history(self, record: Record):
        """更新传感器历史数据"""
        for sensor, value in record.metrics.items():
            self.sensor_history[sensor].append({
                'value': value,
                'timestamp': record.ts
            })
    
    def _evaluate_rule(self, rule: Rule, record: Record) -> bool:
        """评估单个规则"""
        try:
            # 所有条件都必须满足（AND逻辑）
            for condition in rule.conditions:
                if not self._evaluate_condition(condition, record):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"评估规则 {rule.id} 时出错: {e}")
            return False
    
    def _evaluate_condition(self, condition: Condition, record: Record) -> bool:
        """评估单个条件"""
        try:
            if condition.type == ConditionType.THRESHOLD:
                return self._evaluate_threshold(condition, record)
            elif condition.type == ConditionType.STATE_DURATION:
                return self._evaluate_state_duration(condition, record)
            elif condition.type == ConditionType.FREQUENCY:
                return self._evaluate_frequency(condition, record)
            elif condition.type == ConditionType.LOGIC_AND:
                return self._evaluate_logic_and(condition, record)
            elif condition.type == ConditionType.LOGIC_OR:
                return self._evaluate_logic_or(condition, record)
            else:
                self.logger.warning(f"未知条件类型: {condition.type}")
                return False
        except Exception as e:
            self.logger.error(f"评估条件时出错: {e}")
            return False
    
    def _evaluate_threshold(self, condition: Condition, record: Record) -> bool:
        """评估阈值条件"""
        if condition.sensor not in record.metrics:
            return False
        
        current_value = record.metrics[condition.sensor]
        threshold_value = condition.value
        
        if threshold_value is None:
            return False
        
        if condition.operator == Operator.GT:
            return current_value > threshold_value
        elif condition.operator == Operator.LT:
            return current_value < threshold_value
        elif condition.operator == Operator.GTE:
            return current_value >= threshold_value
        elif condition.operator == Operator.LTE:
            return current_value <= threshold_value
        elif condition.operator == Operator.EQ:
            return abs(current_value - threshold_value) < 0.001
        elif condition.operator == Operator.NE:
            return abs(current_value - threshold_value) >= 0.001
        else:
            return False
    
    def _evaluate_state_duration(self, condition: Condition, record: Record) -> bool:
        """评估状态持续时间条件"""
        if condition.sensor not in record.metrics:
            return False
        
        current_value = record.metrics[condition.sensor]
        duration_minutes = condition.duration_minutes
        
        if duration_minutes is None:
            return False
        
        # 检查状态是否持续指定时间
        sensor_key = f"{condition.sensor}_{current_value}"
        now = record.ts
        
        if sensor_key not in self.state_duration[condition.sensor]:
            self.state_duration[condition.sensor][sensor_key] = now
            return False
        
        start_time = self.state_duration[condition.sensor][sensor_key]
        duration = now - start_time
        
        return duration >= timedelta(minutes=duration_minutes)
    
    def _evaluate_frequency(self, condition: Condition, record: Record) -> bool:
        """评估频率条件（简化实现）"""
        # TODO: 实现频率检测逻辑
        return False
    
    def _evaluate_logic_and(self, condition: Condition, record: Record) -> bool:
        """评估逻辑AND条件"""
        if not condition.conditions:
            return False
        
        for sub_condition in condition.conditions:
            if not self._evaluate_condition(sub_condition, record):
                return False
        return True
    
    def _evaluate_logic_or(self, condition: Condition, record: Record) -> bool:
        """评估逻辑OR条件"""
        if not condition.conditions:
            return False
        
        for sub_condition in condition.conditions:
            if self._evaluate_condition(sub_condition, record):
                return True
        return False
    
    def _create_alarm_event(self, rule: Rule, record: Record, run_id: str) -> Optional[AlarmEvent]:
        """创建告警事件"""
        try:
            # 生成唯一ID
            alarm_id = f"ALARM_{rule.id}_{record.ts.strftime('%Y%m%d_%H%M%S')}_{hash(record.ts) % 10000:04d}"
            
            return AlarmEvent(
                id=alarm_id,
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity.value,  # 转换为字符串
                timestamp=record.ts,
                description=f"规则 '{rule.name}' 触发: {rule.description}",
                sensor_values=record.metrics.copy(),
                run_id=run_id
            )
        except Exception as e:
            self.logger.error(f"创建告警事件时出错: {e}")
            return None 