"""
backend/app/entities/ChannelConfiguration.py
------------------------------------
Channel配置系统实体 - 支持分层配置和用户自定义映射
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
from datetime import datetime


class ChannelCategory(Enum):
    """Channel大类枚举"""
    ENVIRONMENT_TEMP = "environment_temp"      # 环境温度
    TOTAL_POWER = "total_power"               # 整体功率  
    TEMPERATURE_T = "temperature_t"           # T1~T22温度
    TEMPERATURE_TE = "temperature_te"         # TE1~TE14数字温度
    DIGITAL_DE = "digital_de"                 # DE1~DE14数字量


@dataclass(slots=True)
class ChannelSubtype:
    """
    Channel细分类型
    
    每个大类下的具体细分选项，包含标签、描述等属性
    """
    subtype_id: str                          # 细分类型ID，如 "indoor_temp"
    label: str                               # 用户可选择的标签，如 "室内温度"
    tag: str                                 # 细分标签，如 "🌡️ 室内"
    description: str                         # 详细描述，如 "冰箱内部环境温度监测"
    unit: str = "°C"                        # 单位
    typical_range: Optional[tuple[float, float]] = None  # 典型值范围


@dataclass(slots=True)
class ChannelDefinition:
    """
    Channel定义 - 系统中的具体channel与其可选配置
    """
    channel_id: str                          # 原始channel ID，如 "T1"
    category: ChannelCategory                # 所属大类
    available_subtypes: List[ChannelSubtype] # 可选的细分类型
    default_subtype_id: str                  # 默认细分类型ID
    is_monitorable: bool = True              # 是否可监控
    system_description: str = ""             # 系统层面的描述


@dataclass(slots=True)
class UserChannelSelection:
    """
    用户对特定channel的选择配置
    """
    channel_id: str                          # channel ID
    selected_subtype_id: str                 # 用户选择的细分类型ID
    enabled: bool = True                     # 是否启用监控
    custom_label: Optional[str] = None       # 用户自定义标签
    notes: str = ""                          # 用户备注


@dataclass(slots=True) 
class TestSessionChannelConfig:
    """
    测试会话的完整channel配置
    """
    session_id: str                          # 会话ID
    selections: Dict[str, UserChannelSelection]  # channel_id -> 用户选择
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = ""                     # 操作用户
    config_name: str = ""                    # 配置名称（便于复用）
    
    def get_effective_label(self, channel_id: str, channel_definitions: Dict[str, ChannelDefinition]) -> str:
        """
        获取channel的有效标签
        优先级：用户自定义标签 > 选择的细分类型标签 > 默认标签
        """
        if channel_id not in self.selections or channel_id not in channel_definitions:
            return channel_id
            
        selection = self.selections[channel_id]
        definition = channel_definitions[channel_id]
        
        # 优先使用用户自定义标签
        if selection.custom_label:
            return selection.custom_label
            
        # 查找选择的细分类型
        for subtype in definition.available_subtypes:
            if subtype.subtype_id == selection.selected_subtype_id:
                return subtype.label
                
        # 回退到默认标签
        for subtype in definition.available_subtypes:
            if subtype.subtype_id == definition.default_subtype_id:
                return subtype.label
                
        return channel_id 