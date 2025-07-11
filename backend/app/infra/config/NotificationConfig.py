"""
backend/app/infra/config/NotificationConfig.py
------------------------------------
基础设施层：通知配置，属于基础设施配置
"""
from __future__ import annotations

from dataclasses import dataclass


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