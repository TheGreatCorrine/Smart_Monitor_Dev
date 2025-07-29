"""
backend/app/infra/fileprovider/FileProvider.py
------------------------------------
File Provider Abstract Base Class - Defines standard interface for file acquisition
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable, Any, Dict
from pathlib import Path
import logging

from ...interfaces.IFileProvider import IFileProvider


class FileProvider(IFileProvider):
    """
    File Provider Abstract Base Class
    
    Defines standard interface for file acquisition and management, supporting different file acquisition strategies:
    - Local files
    - Simulated file push
    - Network file acquisition (future extension)
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._is_active = False
        self._callback: Optional[Callable[[Path], Any]] = None
    
    @abstractmethod
    def get_file_path(self) -> Optional[Path]:
        """
        Get current available file path
        
        Returns
        -------
        Optional[Path]
            File path, returns None if not available
        """
        pass
    
    @abstractmethod
    def is_file_available(self) -> bool:
        """
        Check if file is available
        
        Returns
        -------
        bool
            Whether file is available
        """
        pass
    
    def start(self) -> bool:
        """
        Start file provider
        
        Returns
        -------
        bool
            True if started successfully
        """
        self._is_active = True
        return True
    
    def stop(self) -> None:
        """
        Stop file provider
        """
        self._is_active = False
    
    def is_running(self) -> bool:
        """
        Check if file provider is running
        
        Returns
        -------
        bool
            True if running
        """
        return self._is_active
    
    def set_callback(self, callback: Callable[[Path], None]) -> None:
        """
        Set callback function for file updates
        
        Parameters
        ----------
        callback : Callable[[Path], None]
            Function to call when file is updated
        """
        self._callback = callback
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current status of file provider
        
        Returns
        -------
        Dict[str, Any]
            Status information
        """
        return {
            'is_active': self._is_active,
            'file_available': self.is_file_available(),
            'file_path': str(self.get_file_path()) if self.get_file_path() else None
        }
    
    def _notify_file_update(self, file_path: Path) -> None:
        """
        Notify file update (internal method)
        
        Parameters
        ----------
        file_path : Path
            Updated file path
        """
        if self._callback and self._is_active:
            try:
                self._callback(file_path)
            except Exception as e:
                self.logger.error(f"Error in file update callback: {e}")
    
    def is_active(self) -> bool:
        """
        Check if provider is active (deprecated, use is_running)
        
        Returns
        -------
        bool
            Whether provider is active
        """
        return self._is_active 