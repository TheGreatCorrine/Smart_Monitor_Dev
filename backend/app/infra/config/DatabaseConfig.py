"""
backend/app/infra/config/DatabaseConfig.py
------------------------------------
基础设施层：数据库配置，属于基础设施配置
"""
from __future__ import annotations

from dataclasses import dataclass


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