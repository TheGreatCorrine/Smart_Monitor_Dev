"""
backend/app/infra/fileprovider/FileProvider.py
------------------------------------
文件提供者抽象基类 - 定义文件获取的标准接口
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any
from pathlib import Path
import logging


class FileProvider(ABC):
    """
    文件提供者抽象基类
    
    定义了文件获取和管理的标准接口，支持不同的文件获取策略：
    - 本地文件
    - 模拟文件推送
    - 网络文件获取（未来扩展）
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_active = False
        self._callback: Optional[Callable[[Path], Any]] = None
    
    @abstractmethod
    def get_file_path(self) -> Optional[Path]:
        """
        获取当前可用的文件路径
        
        Returns
        -------
        Optional[Path]
            文件路径，如果不可用则返回None
        """
        pass
    
    @abstractmethod
    def is_file_available(self) -> bool:
        """
        检查文件是否可用
        
        Returns
        -------
        bool
            文件是否可用
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """
        启动文件提供者
        
        Returns
        -------
        bool
            是否成功启动
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        停止文件提供者
        
        Returns
        -------
        bool
            是否成功停止
        """
        pass
    
    def set_callback(self, callback: Callable[[Path], Any]) -> None:
        """
        设置文件更新回调函数
        
        Parameters
        ----------
        callback : Callable[[Path], Any]
            当文件更新时调用的回调函数
        """
        self._callback = callback
    
    def is_active(self) -> bool:
        """
        检查提供者是否处于活动状态
        
        Returns
        -------
        bool
            是否处于活动状态
        """
        return self._is_active
    
    def _notify_file_update(self, file_path: Path) -> None:
        """
        通知文件更新（内部方法）
        
        Parameters
        ----------
        file_path : Path
            更新的文件路径
        """
        if self._callback and file_path.exists():
            try:
                self._callback(file_path)
                self.logger.info(f"文件更新通知: {file_path}")
            except Exception as e:
                self.logger.error(f"文件更新回调执行失败: {e}")
    
    def get_status(self) -> dict:
        """
        获取提供者状态信息
        
        Returns
        -------
        dict
            状态信息字典
        """
        return {
            'active': self._is_active,
            'file_available': self.is_file_available(),
            'file_path': str(self.get_file_path()) if self.get_file_path() else None
        } 