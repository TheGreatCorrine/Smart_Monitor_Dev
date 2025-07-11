"""
backend/app/entities/SystemSummary.py
------------------------------------
纯领域实体：系统摘要相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SystemSummary:
    """
    系统摘要 - 用于统计和报告
    
    Attributes
    ----------
    total_sessions  : int           # 总会话数
    total_records   : int           # 总记录数
    total_alarms    : int           # 总告警数
    disk_usage      : float         # 磁盘使用率
    memory_usage    : float         # 内存使用率
    cpu_usage       : float         # CPU使用率
    uptime_hours    : int           # 运行时间（小时）
    """
    total_sessions: int = 0
    total_records: int = 0
    total_alarms: int = 0
    disk_usage: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    uptime_hours: int = 0 