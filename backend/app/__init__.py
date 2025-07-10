"""
Smart Monitor Dev - 冰箱测试异常状态智能监测系统
===================================================

Clean Architecture 设计，支持 .dat 文件解析和智能告警
"""

__version__ = "1.0.0"
__author__ = "Yining Xiang"

from .cli import main
from .usecases.Monitor import MonitorService

__all__ = ["main", "MonitorService"] 