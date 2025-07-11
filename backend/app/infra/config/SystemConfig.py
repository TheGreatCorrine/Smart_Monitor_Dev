"""
backend/app/infra/config/SystemConfig.py
------------------------------------
基础设施层：系统配置，属于基础设施配置
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime


class LogLevel(Enum):
    """日志级别"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class DataFormat(Enum):
    """数据格式"""
    DAT = "dat"
    CSV = "csv"
    JSON = "json"
    XML = "xml"


@dataclass(slots=True)
class SystemConfig:
    """
    系统配置 - 核心系统实体
    
    Attributes
    ----------
    system_id       : str           # 系统唯一ID
    name            : str           # 系统名称
    version         : str           # 系统版本
    description     : str           # 描述
    log_level       : LogLevel      # 日志级别
    data_format     : DataFormat    # 数据格式
    timezone        : str           # 时区
    language        : str           # 语言
    auto_save       : bool          # 自动保存
    backup_enabled  : bool          # 备份启用
    max_file_size   : int           # 最大文件大小 (MB)
    max_records     : int           # 最大记录数
    retention_days  : int           # 保留天数
    email_notifications: bool       # 邮件通知
    sms_notifications: bool         # 短信通知
    webhook_url     : str|None      # Webhook URL
    created_at      : datetime      # 创建时间
    updated_at      : datetime      # 更新时间
    """
    system_id: str
    name: str
    version: str = "1.0.0"
    description: str = ""
    log_level: LogLevel = LogLevel.INFO
    data_format: DataFormat = DataFormat.DAT
    timezone: str = "UTC"
    language: str = "zh_CN"
    auto_save: bool = True
    backup_enabled: bool = True
    max_file_size: int = 100  # MB
    max_records: int = 1000000
    retention_days: int = 30
    email_notifications: bool = False
    sms_notifications: bool = False
    webhook_url: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now) 