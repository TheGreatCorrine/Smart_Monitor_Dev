"""
backend/app/infra/fileprovider/__init__.py
------------------------------------
文件提供者模块 - 负责文件获取和管理的抽象层
"""
from .FileProvider import FileProvider
from .SimulatedFileProvider import SimulatedFileProvider
from .LocalFileProvider import LocalFileProvider

__all__ = ['FileProvider', 'SimulatedFileProvider', 'LocalFileProvider'] 