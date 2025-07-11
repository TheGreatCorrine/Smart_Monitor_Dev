"""
backend/app/controllers/__init__.py
------------------------------------
控制器层 - 负责处理用户输入和格式化输出
遵循适配器模式，连接用户界面和业务逻辑
"""
from .AlarmController import AlarmController
from .DataController import DataController
from .MonitorController import MonitorController
from .RuleController import RuleController

__all__ = [
    'AlarmController',
    'DataController', 
    'MonitorController',
    'RuleController'
] 