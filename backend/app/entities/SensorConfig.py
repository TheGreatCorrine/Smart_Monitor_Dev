"""
backend/app/entities/SensorConfig.py
------------------------------------
纯领域实体：传感器配置相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class SensorType(Enum):
    """传感器类型 - 用于UI显示和数据处理"""
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"
    DIGITAL = "digital"
    ANALOG = "analog"
    POWER = "power"
    CURRENT = "current"
    VOLTAGE = "voltage"
    FREQUENCY = "frequency"
    ENERGY = "energy"


class Unit(Enum):
    """单位枚举 - 用于显示和格式化"""
    CELSIUS = "°C"
    FAHRENHEIT = "°F"
    KELVIN = "K"
    PASCAL = "Pa"
    BAR = "bar"
    PSI = "psi"
    PERCENT = "%"
    VOLT = "V"
    AMPERE = "A"
    WATT = "W"
    HERTZ = "Hz"
    KWH = "kWh"
    BOOLEAN = "bool"
    NONE = ""


@dataclass(slots=True)
class SensorChannel:
    """
    传感器通道配置 - 纯映射关系，不包含业务逻辑
    
    Attributes
    ----------
    label       : str        # 显示标签，如 "TCEC", "TA1", "TRC1"
    channel     : str        # 实际通道，如 "T1", "T2", "DI1"
    sensor_type : SensorType # 传感器类型（用于UI显示）
    unit        : Unit       # 单位（用于显示）
    description : str        # 描述
    enabled     : bool       # 是否启用
    """
    label: str
    channel: str
    sensor_type: SensorType
    unit: Unit
    description: str = ""
    enabled: bool = True


@dataclass(slots=True)
class SensorGroup:
    """
    传感器分组 - 用于UI分组显示
    
    Attributes
    ----------
    name        : str   # 分组名称
    description : str   # 描述
    sensors     : List[str] # 传感器标签列表
    color       : str   # 显示颜色
    enabled     : bool  # 是否启用
    """
    name: str
    description: str = ""
    sensors: List[str] = field(default_factory=list)
    color: str = "#000000"
    enabled: bool = True 