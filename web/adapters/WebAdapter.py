"""
web/adapters/WebAdapter.py
------------------------------------
Web Adapter - Completely independent from GUI version
Directly uses Clean Architecture core services
"""
import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
from queue import Queue
import threading

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from backend.app.di.config import get_monitor_service, get_channel_service
from backend.app.entities.AlarmEvent import AlarmEvent
from backend.app.entities.record import Record
from backend.app.entities.ChannelConfiguration import ChannelCategory, ChannelSubtype
from backend.app.entities.AlarmEvent import Severity


class WebLogHandler(logging.Handler):
    """Custom log handler to capture logs for web interface"""
    
    def __init__(self, log_queue: Queue):
        super().__init__()
        self.log_queue = log_queue
    
    def emit(self, record):
        """Send log message to queue"""
        msg = self.format(record)
        self.log_queue.put(msg)


class WebAdapter:
    """Web adapter for clean architecture"""
    
    def __init__(self):
        # Change to project root for correct path resolution
        project_root = os.path.join(os.path.dirname(__file__), '../..')
        os.chdir(project_root)
        
        # Verify we're in the correct directory
        if not os.path.exists('config/label_channel_match.yaml'):
            raise RuntimeError(f"Configuration file not found. Current directory: {os.getcwd()}")
        
        # Initialize services
        self.monitor_service = get_monitor_service()
        self.channel_service = get_channel_service()
        
        # Web-specific configuration
        self.web_config = {
            'current_file': None,
            'monitoring_active': False,
            'session_id': None
        }
        
        # Setup logging capture
        self.log_queue = Queue()
        self.log_handler = WebLogHandler(self.log_queue)
        logging.getLogger().addHandler(self.log_handler)
        logging.getLogger().setLevel(logging.INFO)
        
        # Add alarm handler for web
        self.monitor_service.add_alarm_handler(self._web_alarm_handler)
    
    def _web_alarm_handler(self, alarm: AlarmEvent):
        """Web alarm handler"""
        # Log alarm for web interface
        logging.info(f"ALARM: {alarm.severity.value} - {alarm.description}")
    
    def get_logs(self) -> Dict[str, Any]:
        """Get captured logs for web interface"""
        try:
            logs = []
            # Get all available logs from queue without clearing it
            temp_logs = []
            while not self.log_queue.empty():
                try:
                    log_msg = self.log_queue.get_nowait()
                    temp_logs.append(log_msg)
                except:
                    break
            
            # Put logs back to queue to maintain history
            for log_msg in temp_logs:
                self.log_queue.put(log_msg)
            
            # Return all logs (including the ones we just put back)
            logs = temp_logs
            
            return {
                'success': True,
                'logs': logs
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get logs: {str(e)}'
            }
    
    # ==================== Configuration Management ====================
    
    def get_label_configuration(self) -> Dict[str, Any]:
        """Get label configuration - directly use channel service"""
        try:
            return self.channel_service.get_configuration_for_ui()
        except Exception as e:
            return {
                'categories': {},
                'error': f'Failed to load configuration: {str(e)}'
            }
    
    def save_label_selection(self, selected_labels: Dict[str, str]) -> Dict[str, Any]:
        """Save label selection - directly save to file"""
        try:
            label_selection_path = Path("label_selection.json")
            
            # Save to file
            with open(label_selection_path, 'w', encoding='utf-8') as f:
                json.dump(selected_labels, f, ensure_ascii=False, indent=2)
            
            return {
                'success': True,
                'message': 'Label selection saved successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save labels: {str(e)}'
            }
    
    def load_label_selection(self) -> Dict[str, Any]:
        """Load label selection - directly load from file"""
        try:
            label_selection_path = Path("label_selection.json")
            
            if not label_selection_path.exists():
                return {
                    'success': True,
                    'labels': {}
                }
            
            with open(label_selection_path, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            
            return {
                'success': True,
                'labels': labels
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to load labels: {str(e)}'
            }
    
    # ==================== File Management ====================
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """Validate file path - direct validation"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': True,
                    'valid': False,
                    'message': 'File does not exist'
                }
            
            if not path.suffix.lower() == '.dat':
                return {
                    'success': True,
                    'valid': False,
                    'message': 'File is not a .dat file'
                }
            
            # Check file size
            file_size = path.stat().st_size
            if file_size == 0:
                return {
                    'success': True,
                    'valid': False,
                    'message': 'File is empty'
                }
            
            return {
                'success': True,
                'valid': True,
                'message': 'File is valid',
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'File validation failed: {str(e)}'
            }
    
    def auto_infer_workstation_id(self, file_path: str) -> Dict[str, Any]:
        """Automatically infer workstation ID - infer from filename"""
        try:
            import re
            
            path = Path(file_path)
            filename = path.stem
            
            # Try to infer workstation ID from filename
            # Match patterns: MPL number or filename containing numbers
            patterns = [
                r'MPL(\d+)',  # MPL6, MPL12, etc.
                r'(\d+)',      # Any number
            ]
            
            for pattern in patterns:
                match = re.search(pattern, filename)
                if match:
                    workstation_id = match.group(1)
                    return {
                        'success': True,
                        'workstation_id': workstation_id,
                        'inferred': True,
                        'pattern': pattern
                    }
            
            return {
                'success': True,
                'workstation_id': None,
                'inferred': False
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Workstation ID inference failed: {str(e)}'
            }
    
    # ==================== Monitoring Management ====================
    
    def start_monitoring(self, file_path: str = None, config_path: str = "config/rules.yaml", run_id: str = None, workstation_id: str = None) -> Dict[str, Any]:
        """Start monitoring - directly use monitoring service"""
        try:
            if not run_id:
                run_id = f"web_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # If file path exists, validate file
            if file_path:
                validation = self.validate_file_path(file_path)
                if not validation.get('valid', False):
                    return {
                        'success': False,
                        'error': validation.get('message', 'File validation failed')
                    }
            
            # Start monitoring
            success = self.monitor_service.start_continuous_monitoring(run_id)
            
            if success:
                self.web_config['current_file'] = file_path
                self.web_config['monitoring_active'] = True
                self.web_config['session_id'] = run_id
            
            return {
                'success': success,
                'message': 'Monitoring started successfully' if success else 'Failed to start monitoring',
                'run_id': run_id,
                'file_path': file_path,
                'workstation_id': workstation_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start monitoring: {str(e)}'
            }
    
    def start_simulation(self, file_path: str, config_path: str = "config/rules.yaml", 
                        run_id: str = None, workstation_id: str = "1") -> Dict[str, Any]:
        """Start simulation - directly use monitoring service"""
        try:
            if not run_id:
                run_id = f"web_sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Validate file only if file_path is provided (for New Test)
            if file_path:
                validation = self.validate_file_path(file_path)
                if not validation.get('valid', False):
                    return {
                        'success': False,
                        'error': validation.get('message', 'File validation failed')
                    }
            
            # Stop old monitoring first (if running)
            if self.monitor_service.is_monitoring:
                self.monitor_service.stop_continuous_monitoring()
            
            # Initialize monitoring service
            self.monitor_service.initialize(config_path)
            
            # Create file provider
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
            from backend.app.di.config import create_file_provider
            file_provider = create_file_provider("simulated", file_path)
            
            # Set file provider
            self.monitor_service.set_file_provider(file_provider)
            
            # Start monitoring
            success = self.monitor_service.start_continuous_monitoring(run_id)
            
            if success:
                self.web_config['current_file'] = file_path
                self.web_config['monitoring_active'] = True
                self.web_config['session_id'] = run_id
            
            return {
                'success': success,
                'message': 'Simulation started successfully' if success else 'Failed to start simulation',
                'run_id': run_id,
                'file_path': file_path,
                'workstation_id': workstation_id
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start simulation: {str(e)}'
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring - directly use monitoring service"""
        try:
            success = self.monitor_service.stop_continuous_monitoring()
            
            if success:
                self.web_config['monitoring_active'] = False
                self.web_config['session_id'] = None
            
            return {
                'success': success,
                'message': 'Monitoring stopped successfully' if success else 'Failed to stop monitoring'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to stop monitoring: {str(e)}'
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring status - directly use monitoring service"""
        try:
            status = self.monitor_service.get_monitoring_status()
            
            # Add Web-specific status information
            status.update({
                'web_session_id': self.web_config['session_id'],
                'web_current_file': self.web_config['current_file'],
                'web_monitoring_active': self.web_config['monitoring_active']
            })
            
            return {
                'success': True,
                'status': status
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get monitoring status: {str(e)}'
            }
    
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]) -> Dict[str, Any]:
        """Add alarm handler - directly use monitoring service"""
        try:
            self.monitor_service.add_alarm_handler(handler)
            return {
                'success': True,
                'message': 'Alarm handler added successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add alarm handler: {str(e)}'
            }
    
    # ==================== Web-specific Features ====================
    
    def get_web_status(self) -> Dict[str, Any]:
        """Get Web application status"""
        return {
            'success': True,
            'web_config': self.web_config,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    def reset_web_session(self) -> Dict[str, Any]:
        """Reset Web session"""
        try:
            # Stop monitoring
            if self.web_config['monitoring_active']:
                self.stop_monitoring()
            
            # Reset configuration
            self.web_config = {
                'session_id': None,
                'current_file': None,
                'monitoring_active': False
            }
            
            return {
                'success': True,
                'message': 'Web session reset successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to reset web session: {str(e)}'
            } 