"""
backend/app/infra/fileprovider/LocalFileProvider.py
------------------------------------
本地文件提供者 - 处理本地文件
"""
from pathlib import Path
from typing import Optional
import logging

from .FileProvider import FileProvider


class LocalFileProvider(FileProvider):
    """
    本地文件提供者
    
    处理本地文件，作为现有功能的封装
    """
    
    def __init__(self, file_path: str):
        """
        初始化本地文件提供者
        
        Parameters
        ----------
        file_path : str
            本地文件路径
        """
        super().__init__()
        self.file_path = Path(file_path)
        self.logger.info(f"初始化本地文件提供者: {self.file_path}")
    
    def get_file_path(self) -> Optional[Path]:
        """获取当前可用的文件路径"""
        if self.file_path.exists() and self.file_path.stat().st_size > 0:
            return self.file_path
        return None
    
    def is_file_available(self) -> bool:
        """检查文件是否可用"""
        return self.get_file_path() is not None
    
    def start(self) -> bool:
        """启动本地文件提供者"""
        if self._is_active:
            self.logger.warning("本地文件提供者已经在运行")
            return True
        
        if not self.is_file_available():
            self.logger.error(f"文件不可用: {self.file_path}")
            return False
        
        self._is_active = True
        self.logger.info(f"本地文件提供者已启动: {self.file_path}")
        
        # 立即通知文件可用
        self._notify_file_update(self.file_path)
        
        return True
    
    def stop(self) -> bool:
        """停止本地文件提供者"""
        if not self._is_active:
            return True
        
        self._is_active = False
        self.logger.info("本地文件提供者已停止")
        
        return True
    
    def get_status(self) -> dict:
        """获取详细状态信息"""
        base_status = super().get_status()
        base_status.update({
            'file_size': self.file_path.stat().st_size if self.file_path.exists() else 0,
            'file_modified': self.file_path.stat().st_mtime if self.file_path.exists() else None
        })
        return base_status 