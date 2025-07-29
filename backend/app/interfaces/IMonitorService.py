"""
backend/app/interfaces/IMonitorService.py
------------------------------------
Monitor Service Interface - Abstract interface for monitoring services
"""
from abc import ABC, abstractmethod
from typing import List, Callable, Optional, Dict, Any
from pathlib import Path

from ..entities.record import Record
from ..entities.AlarmEvent import AlarmEvent
from .IFileProvider import IFileProvider


class IMonitorService(ABC):
    """
    Monitor Service Interface
    
    Abstract interface for monitoring services
    """
    
    @abstractmethod
    def initialize(self, config_path: str = "config/rules.yaml") -> None:
        """
        Initialize the monitor service
        
        Parameters
        ----------
        config_path : str
            Path to configuration file
        """
        pass
    
    @abstractmethod
    def set_file_provider(self, file_provider: IFileProvider) -> None:
        """
        Set file provider for the monitor service
        
        Parameters
        ----------
        file_provider : IFileProvider
            File provider instance
        """
        pass
    
    @abstractmethod
    def start_continuous_monitoring(self, run_id: str) -> bool:
        """
        Start continuous monitoring
        
        Parameters
        ----------
        run_id : str
            Run ID for the monitoring session
            
        Returns
        -------
        bool
            True if started successfully
        """
        pass
    
    @abstractmethod
    def stop_continuous_monitoring(self) -> bool:
        """
        Stop continuous monitoring
        
        Returns
        -------
        bool
            True if stopped successfully
        """
        pass
    
    @abstractmethod
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]) -> None:
        """
        Add alarm handler
        
        Parameters
        ----------
        handler : Callable[[AlarmEvent], None]
            Alarm handler function
        """
        pass
    
    @abstractmethod
    def process_data_file(self, file_path: str, run_id: str) -> tuple[List[AlarmEvent], int]:
        """
        Process data file
        
        Parameters
        ----------
        file_path : str
            Path to data file
        run_id : str
            Run ID
            
        Returns
        -------
        tuple[List[AlarmEvent], int]
            List of alarms and record count
        """
        pass
    
    @abstractmethod
    def process_record(self, record: Record, run_id: str) -> List[AlarmEvent]:
        """
        Process single record
        
        Parameters
        ----------
        record : Record
            Record to process
        run_id : str
            Run ID
            
        Returns
        -------
        List[AlarmEvent]
            List of generated alarms
        """
        pass
    
    @abstractmethod
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get monitoring status
        
        Returns
        -------
        Dict[str, Any]
            Current monitoring status
        """
        pass
    
    @property
    @abstractmethod
    def is_monitoring(self) -> bool:
        """
        Check if monitoring is active
        
        Returns
        -------
        bool
            True if monitoring is active
        """
        pass 