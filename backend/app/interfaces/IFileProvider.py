"""
backend/app/interfaces/IFileProvider.py
------------------------------------
File Provider Interface - Abstract interface for file providers
"""
from abc import ABC, abstractmethod
from typing import Callable, Optional
from pathlib import Path


class IFileProvider(ABC):
    """
    File Provider Interface
    
    Abstract interface for file providers that can monitor and provide data files
    """
    
    @abstractmethod
    def set_callback(self, callback: Callable[[Path], None]) -> None:
        """
        Set callback function for file updates
        
        Parameters
        ----------
        callback : Callable[[Path], None]
            Function to call when file is updated
        """
        pass
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the file provider
        
        Returns
        -------
        bool
            True if started successfully
        """
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """
        Stop the file provider
        """
        pass
    
    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the file provider is running
        
        Returns
        -------
        bool
            True if running
        """
        pass
    
    @abstractmethod
    def get_status(self) -> dict:
        """
        Get current status of the file provider
        
        Returns
        -------
        dict
            Status information
        """
        pass 