"""
backend/app/interfaces/IChannelConfigurationService.py
------------------------------------
Channel Configuration Service Interface - Abstract interface for channel configuration
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path


class IChannelConfigurationService(ABC):
    """
    Channel Configuration Service Interface
    
    Abstract interface for channel configuration services
    """
    
    @abstractmethod
    def get_configuration_for_ui(self) -> Dict[str, Any]:
        """
        Get configuration data for UI display
        
        Returns
        -------
        Dict[str, Any]
            Configuration data structured for UI
        """
        pass
    
    @abstractmethod
    def get_default_user_configuration(self) -> Dict[str, Any]:
        """
        Get default user configuration
        
        Returns
        -------
        Dict[str, Any]
            Default configuration for users
        """
        pass
    
    @abstractmethod
    def validate_user_configuration(self, user_config: Dict[str, Any]) -> List[str]:
        """
        Validate user configuration
        
        Parameters
        ----------
        user_config : Dict[str, Any]
            User configuration to validate
            
        Returns
        -------
        List[str]
            List of validation errors, empty if valid
        """
        pass
    
    @abstractmethod
    def save_session_configuration(self, session_config: Dict[str, Any]) -> None:
        """
        Save session configuration
        
        Parameters
        ----------
        session_config : Dict[str, Any]
            Session configuration to save
        """
        pass
    
    @abstractmethod
    def get_channel_label(self, session_id: str, channel_id: str) -> str:
        """
        Get channel label for a session
        
        Parameters
        ----------
        session_id : str
            Session ID
        channel_id : str
            Channel ID
            
        Returns
        -------
        str
            Channel label
        """
        pass 