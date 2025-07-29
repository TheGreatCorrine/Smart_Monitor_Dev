"""
backend/app/adapters/GUIAdapter.py
------------------------------------
GUI Adapter - Interface adapter for GUI operations
"""
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import json
from datetime import datetime

from ..interfaces.IMonitorService import IMonitorService
from ..interfaces.IChannelConfigurationService import IChannelConfigurationService
from ..interfaces.IFileProvider import IFileProvider
from ..entities.AlarmEvent import AlarmEvent


class GUIAdapter:
    """
    GUI Adapter
    
    Provides a clean interface for GUI operations, abstracting business logic
    and following Clean Architecture principles.
    """
    
    def __init__(self, 
                 monitor_service: IMonitorService,
                 channel_service: IChannelConfigurationService):
        self.monitor_service = monitor_service
        self.channel_service = channel_service
        self.label_selection_path = Path("label_selection.json")
    
    def load_label_configuration(self) -> Dict[str, Any]:
        """
        Load label configuration for UI display
        
        Returns
        -------
        Dict[str, Any]
            Configuration data for UI
        """
        try:
            return self.channel_service.get_configuration_for_ui()
        except Exception as e:
            # Return empty config on error
            return {'categories': {}}
    
    def save_label_selection(self, selected_labels: Dict[str, str]) -> bool:
        """
        Save label selection to file
        
        Parameters
        ----------
        selected_labels : Dict[str, str]
            Selected labels mapping
            
        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            with open(self.label_selection_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'labels': selected_labels
                }, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def load_label_selection(self) -> Optional[Dict[str, str]]:
        """
        Load previous label selection
        
        Returns
        -------
        Optional[Dict[str, str]]
            Previous label selection or None if not found
        """
        try:
            if not self.label_selection_path.exists():
                return None
            
            with open(self.label_selection_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('labels', {})
        except Exception:
            return None
    
    def start_monitoring(self, file_path: str, config_path: str, run_id: str) -> Dict[str, Any]:
        """
        Start monitoring process
        
        Parameters
        ----------
        file_path : str
            Path to data file
        config_path : str
            Path to config file
        run_id : str
            Run ID
            
        Returns
        -------
        Dict[str, Any]
            Monitoring result
        """
        try:
            # Initialize monitor service
            self.monitor_service.initialize(config_path)
            
            # Process data file
            alarms, records_count = self.monitor_service.process_data_file(file_path, run_id)
            
            return {
                'success': True,
                'records_count': records_count,
                'alarms_count': len(alarms),
                'alarms': alarms
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def start_simulation(self, file_path: str, config_path: str, run_id: str, 
                        workstation_id: str, file_provider: IFileProvider) -> Dict[str, Any]:
        """
        Start simulation monitoring
        
        Parameters
        ----------
        file_path : str
            Path to data file
        config_path : str
            Path to config file
        run_id : str
            Run ID
        workstation_id : str
            Workstation ID
        file_provider : IFileProvider
            File provider instance
            
        Returns
        -------
        Dict[str, Any]
            Simulation result
        """
        try:
            # Initialize monitor service
            self.monitor_service.initialize(config_path)
            
            # Set file provider
            self.monitor_service.set_file_provider(file_provider)
            
            # Start continuous monitoring
            success = self.monitor_service.start_continuous_monitoring(run_id)
            
            if success:
                return {
                    'success': True,
                    'workstation_id': workstation_id
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to start simulation'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_monitoring(self) -> bool:
        """
        Stop monitoring
        
        Returns
        -------
        bool
            True if stopped successfully
        """
        try:
            return self.monitor_service.stop_continuous_monitoring()
        except Exception:
            return False
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """
        Get current monitoring status
        
        Returns
        -------
        Dict[str, Any]
            Current monitoring status
        """
        try:
            return self.monitor_service.get_monitoring_status()
        except Exception:
            return {}
    
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]) -> None:
        """
        Add alarm handler
        
        Parameters
        ----------
        handler : Callable[[AlarmEvent], None]
            Alarm handler function
        """
        self.monitor_service.add_alarm_handler(handler)
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """
        Validate file path
        
        Parameters
        ----------
        file_path : str
            File path to validate
            
        Returns
        -------
        Dict[str, Any]
            Validation result
        """
        path = Path(file_path)
        
        if not path.exists():
            return {
                'valid': False,
                'error': 'File does not exist'
            }
        
        if not path.is_file():
            return {
                'valid': False,
                'error': 'Path is not a file'
            }
        
        if path.suffix.lower() != '.dat':
            return {
                'valid': False,
                'error': 'File must be a .dat file'
            }
        
        return {
            'valid': True,
            'file_path': str(path)
        }
    
    def auto_infer_workstation_id(self, file_path: str) -> Optional[str]:
        """
        Auto infer workstation ID from filename
        
        Parameters
        ----------
        file_path : str
            File path
            
        Returns
        -------
        Optional[str]
            Inferred workstation ID or None
        """
        try:
            import re
            path = Path(file_path)
            stem = path.stem
            
            if stem.startswith('mpl') or stem.startswith('MPL'):
                match = re.search(r'mpl(\d+)', stem.lower())
                if match:
                    return match.group(1)
        except Exception:
            pass
        
        return None 