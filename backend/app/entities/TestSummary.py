"""
backend/app/entities/TestSummary.py
------------------------------------
纯领域实体：测试摘要相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(slots=True)
class TestSummary:
    """
    测试摘要 - 用于统计和报告
    
    Attributes
    ----------
    total_sessions  : int           # 总会话数
    completed_sessions: int         # 完成会话数
    failed_sessions : int           # 失败会话数
    total_duration  : int           # 总时长（分钟）
    total_records   : int           # 总记录数
    total_alarms    : int           # 总告警数
    time_range      : tuple         # 时间范围 (start, end)
    """
    total_sessions: int = 0
    completed_sessions: int = 0
    failed_sessions: int = 0
    total_duration: int = 0
    total_records: int = 0
    total_alarms: int = 0
    time_range: Optional[tuple[datetime, datetime]] = None 