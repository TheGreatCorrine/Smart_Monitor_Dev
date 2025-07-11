"""
backend/app/services/__init__.py
------------------------------------
服务层接口定义
"""
from abc import ABC, abstractmethod
from typing import List, Protocol
from ..entities.Rule import Rule
from ..entities.Record import Record
from ..entities.AlarmEvent import AlarmEvent


class IRuleEngine(Protocol):
    """规则引擎接口"""
    
    def load_rules(self, rules: List[Rule]) -> None:
        """加载规则"""
        ...
    
    def evaluate_record(self, record: Record, run_id: str) -> List[AlarmEvent]:
        """评估记录并返回告警事件"""
        ...


class IAlarmService(Protocol):
    """告警服务接口"""
    
    def create_alarm(self, rule: Rule, record: Record, run_id: str) -> AlarmEvent:
        """创建告警事件"""
        ...
    
    def acknowledge_alarm(self, alarm_id: str, user: str) -> bool:
        """确认告警"""
        ...
    
    def resolve_alarm(self, alarm_id: str, user: str) -> bool:
        """解决告警"""
        ...


class IDataAnalysisService(Protocol):
    """数据分析服务接口"""
    
    def analyze_trends(self, sensor_data: List[Record]) -> dict:
        """分析数据趋势"""
        ...
    
    def detect_anomalies(self, sensor_data: List[Record]) -> List[dict]:
        """检测异常模式"""
        ... 