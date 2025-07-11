"""
backend/app/entities/AlarmSummary.py
------------------------------------
纯领域实体：告警摘要相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


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