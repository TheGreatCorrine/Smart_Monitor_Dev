"""
backend/app/entities/TestResult.py
------------------------------------
纯领域实体：测试结果相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass(slots=True)
class TestResult:
    """
    测试结果 - 用于记录测试结果
    
    Attributes
    ----------
    session_id      : str           # 关联的会话ID
    result_type     : str           # 结果类型 (pass/fail/warning)
    timestamp       : datetime      # 结果时间
    description     : str           # 结果描述
    data_file       : str|None      # 数据文件路径
    record_count    : int           # 记录数量
    alarm_count     : int           # 告警数量
    performance_metrics: Dict[str, float] # 性能指标
    """
    session_id: str
    result_type: str
    timestamp: datetime = field(default_factory=datetime.now)
    description: str = ""
    data_file: Optional[str] = None
    record_count: int = 0
    alarm_count: int = 0
    performance_metrics: Dict[str, float] = field(default_factory=dict) 