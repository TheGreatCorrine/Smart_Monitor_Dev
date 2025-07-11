"""
backend/app/entities/TestSession.py
------------------------------------
纯领域实体：测试会话相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
from datetime import datetime

from .Sensor import SensorChannel


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