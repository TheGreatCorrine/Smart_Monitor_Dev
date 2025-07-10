"""
backend/app/entities/TestSession.py
------------------------------------
纯领域实体：测试会话相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime

from .SensorConfig import SensorChannel


class TestStatus(Enum):
    """测试状态"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TestType(Enum):
    """测试类型"""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    EFFICIENCY = "efficiency"
    SAFETY = "safety"
    CUSTOM = "custom"


@dataclass(slots=True)
class TestSession:
    """
    测试会话 - 核心测试实体
    
    Attributes
    ----------
    session_id      : str           # 会话唯一ID
    name            : str           # 测试名称
    description     : str           # 描述
    status          : TestStatus    # 测试状态
    test_type       : TestType      # 测试类型
    engineer        : str           # 工程师姓名
    start_time      : datetime|None # 开始时间
    end_time        : datetime|None # 结束时间
    duration_minutes: int|None      # 持续时间（分钟）
    sensors         : Dict[str, SensorChannel] # 传感器配置
    metadata        : Dict[str, str] # 元数据
    notes           : str           # 备注
    """
    session_id: str
    name: str
    description: str = ""
    status: TestStatus = TestStatus.PLANNED
    test_type: TestType = TestType.CUSTOM
    engineer: str = ""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    sensors: Dict[str, SensorChannel] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)
    notes: str = ""


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