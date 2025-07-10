"""
backend/app/entities/AlarmEvent.py
------------------------------------
纯领域实体：告警事件相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class AlarmStatus(Enum):
    """告警状态"""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    CLEARED = "cleared"


class AlarmCategory(Enum):
    """告警分类"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    POWER = "power"
    SYSTEM = "system"
    CUSTOM = "custom"


@dataclass(slots=True)
class AlarmEvent:
    """
    告警事件 - 核心告警实体
    
    Attributes
    ----------
    id              : str           # 告警事件唯一ID
    rule_id         : str           # 触发规则ID
    rule_name       : str           # 规则名称
    severity        : str           # 严重程度 (low/medium/high/critical)
    status          : AlarmStatus   # 告警状态
    category        : AlarmCategory # 告警分类
    timestamp       : datetime      # 触发时间
    description     : str           # 告警描述
    sensor_values   : Dict[str, float] # 传感器值
    run_id          : str           # 测试会话ID
    file_pos        : int|None      # 文件位置
    acknowledged_by : str|None      # 确认人
    acknowledged_at : datetime|None # 确认时间
    resolved_by     : str|None      # 解决人
    resolved_at     : datetime|None # 解决时间
    notes           : str           # 备注
    """
    id: str
    rule_id: str
    rule_name: str
    severity: str
    status: AlarmStatus = AlarmStatus.ACTIVE
    category: AlarmCategory = AlarmCategory.CUSTOM
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    sensor_values: Dict[str, float] = field(default_factory=dict)
    run_id: str = ""
    file_pos: Optional[int] = None
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    notes: str = ""


@dataclass(slots=True)
class AlarmSummary:
    """
    告警摘要 - 用于统计和报告
    
    Attributes
    ----------
    total_alarms    : int           # 总告警数
    active_alarms   : int           # 活跃告警数
    critical_alarms : int           # 严重告警数
    high_alarms     : int           # 高级告警数
    medium_alarms   : int           # 中级告警数
    low_alarms      : int           # 低级告警数
    time_range      : tuple         # 时间范围 (start, end)
    """
    total_alarms: int = 0
    active_alarms: int = 0
    critical_alarms: int = 0
    high_alarms: int = 0
    medium_alarms: int = 0
    low_alarms: int = 0
    time_range: Optional[tuple[datetime, datetime]] = None 