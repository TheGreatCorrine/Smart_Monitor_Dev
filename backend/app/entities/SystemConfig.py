"""
backend/app/entities/SystemConfig.py
------------------------------------
纯领域实体：系统配置相关的核心实体，不依赖任何框架
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional
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


@dataclass(slots=True)
class DatabaseConfig:
    """
    数据库配置
    
    Attributes
    ----------
    host            : str           # 数据库主机
    port            : int           # 数据库端口
    database        : str           # 数据库名
    username        : str           # 用户名
    password        : str           # 密码
    connection_pool : int           # 连接池大小
    timeout         : int           # 超时时间（秒）
    """
    host: str = "localhost"
    port: int = 5432
    database: str = "smart_monitor"
    username: str = ""
    password: str = ""
    connection_pool: int = 10
    timeout: int = 30


@dataclass(slots=True)
class NotificationConfig:
    """
    通知配置
    
    Attributes
    ----------
    email_enabled   : bool          # 邮件启用
    sms_enabled     : bool          # 短信启用
    webhook_enabled : bool          # Webhook启用
    email_server    : str           # 邮件服务器
    email_port      : int           # 邮件端口
    email_username  : str           # 邮件用户名
    email_password  : str           # 邮件密码
    sms_provider    : str           # 短信提供商
    sms_api_key     : str           # 短信API密钥
    webhook_url     : str           # Webhook URL
    """
    email_enabled: bool = False
    sms_enabled: bool = False
    webhook_enabled: bool = False
    email_server: str = ""
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""
    sms_provider: str = ""
    sms_api_key: str = ""
    webhook_url: str = ""


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