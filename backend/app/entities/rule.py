"""
backend/app/entities/Rule.py
------------------------------------
纯领域实体：规则相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum
from datetime import datetime


class ConditionType(Enum):
    """条件类型"""
    THRESHOLD = "threshold"
    STATE_DURATION = "state_duration"
    FREQUENCY = "frequency"
    LOGIC_AND = "logic_and"
    LOGIC_OR = "logic_or"


class Operator(Enum):
    """操作符"""
    GREATER_THAN = ">"
    LESS_THAN = "<"
    GREATER_THAN_OR_EQUAL_TO = ">="
    LESS_THAN_OR_EQUAL_TO = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="
    UNCHANGED = "unchanged"
    CHANGED = "changed"


class Severity(Enum):
    """告警严重程度"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(slots=True)
class Condition:
    """
    规则条件
    
    Attributes
    ----------
    type        : ConditionType # 条件类型
    sensor      : str           # 传感器标签
    operator    : Operator      # 操作符
    value       : Optional[float]    # 比较值
    duration_minutes : Optional[int] # 持续时间（分钟）
    conditions  : Optional[List[Condition]] # 逻辑组合条件
    """
    type: ConditionType
    sensor: str
    operator: Operator
    value: Optional[float] = None
    duration_minutes: Optional[int] = None
    conditions: Optional[List['Condition']] = None


@dataclass(slots=True)
class Rule:
    """
    检测规则
    
    Attributes
    ----------
    id          : str           # 规则ID
    name        : str           # 规则名称
    description : str           # 规则描述
    conditions  : List[Condition] # 条件列表
    severity    : Severity      # 严重程度
    enabled     : bool          # 是否启用
    """
    id: str
    name: str
    description: str
    conditions: List[Condition]
    severity: Severity
    enabled: bool = True 