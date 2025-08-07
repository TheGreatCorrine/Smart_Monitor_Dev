"""
web/adapters/WebAdapter.py
------------------------------------
Web适配器 - 完全独立于GUI版本
直接使用Clean Architecture的核心服务
集成SessionController处理业务流程
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

from backend.app.di.config import get_monitor_service, get_channel_service, get_session_service
from backend.app.controllers.SessionController import SessionController
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
    """Web adapter for clean architecture with session management"""
    
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
        self.session_service = get_session_service()
        
        # Initialize session controller
        self.session_controller = SessionController(self.session_service, self.monitor_service)
        
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
    
    # ==================== 会话管理 API ====================
    
    def select_test_type(self, test_type: str) -> Dict[str, Any]:
        """
        选择测试类型 - 使用SessionController
        
        Parameters
        ----------
        test_type : str
            测试类型 ("old" 或 "new")
            
        Returns
        -------
        Dict[str, Any]
            选择结果
        """
        return self.session_controller.select_test_type(test_type)
    
    def configure_old_test_session(self, session_id: str, workstation_id: str, 
                                 config_path: str = "config/rules.yaml") -> Dict[str, Any]:
        """配置Old Test会话"""
        return self.session_controller.configure_old_test_session(session_id, workstation_id, config_path)
    
    def start_old_test_monitoring(self, session_id: str) -> Dict[str, Any]:
        """启动Old Test监控"""
        return self.session_controller.start_old_test_monitoring(session_id)
    
    def start_old_test_simulation(self, session_id: str) -> Dict[str, Any]:
        """启动Old Test模拟"""
        return self.session_controller.start_old_test_simulation(session_id)
    
    def configure_new_test_session(self, session_id: str, file_path: str, 
                                 selected_labels: Dict[str, str], workstation_id: str = "1",
                                 config_path: str = "config/rules.yaml") -> Dict[str, Any]:
        """配置New Test会话"""
        return self.session_controller.configure_new_test_session(session_id, file_path, selected_labels, workstation_id, config_path)
    
    def start_new_test_monitoring(self, session_id: str) -> Dict[str, Any]:
        """启动New Test监控"""
        return self.session_controller.start_new_test_monitoring(session_id)
    
    def start_new_test_simulation(self, session_id: str) -> Dict[str, Any]:
        """启动New Test模拟"""
        return self.session_controller.start_new_test_simulation(session_id)
    
    def stop_session_monitoring(self, session_id: str) -> Dict[str, Any]:
        """停止会话监控"""
        return self.session_controller.stop_session_monitoring(session_id)
    
    def get_session_status(self, session_id: str = None) -> Dict[str, Any]:
        """获取会话状态"""
        return self.session_controller.get_session_status(session_id)
    
    def list_all_sessions(self, test_type: str = None) -> Dict[str, Any]:
        """列出所有会话"""
        return self.session_controller.list_all_sessions(test_type)
    
    def switch_to_session(self, session_id: str) -> Dict[str, Any]:
        """切换到指定会话"""
        return self.session_controller.switch_to_session(session_id)
    
    # ==================== 工作台管理 ====================
    
    def get_workstations(self) -> Dict[str, Any]:
        """
        获取工作台列表 - 基于会话状态
        
        Returns
        -------
        Dict[str, Any]
            工作台列表
        """
        try:
            # 获取所有Old Test会话作为工作台
            old_sessions = self.session_service.list_sessions()
            old_sessions = [s for s in old_sessions if s.test_type.value == 'old']
            
            workstations = []
            for session in old_sessions:
                status = 'running' if session.status.value == 'running' else 'stopped'
                workstations.append({
                    'id': session.session_id,
                    'name': f"Old Test - {session.configuration.selected_workstation or 'Unknown'}",
                    'status': status,
                    'start_time': session.started_at.isoformat() if session.started_at else None,
                    'records_processed': session.records_processed,
                    'alarms_generated': session.alarms_generated,
                    'test_type': 'old'
                })
            
            return {
                'success': True,
                'workstations': workstations
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get workstations: {str(e)}'
            }
    
    def select_workstation(self, workstation_id: str) -> Dict[str, Any]:
        """
        选择工作台 - 切换到指定会话
        
        Parameters
        ----------
        workstation_id : str
            工作台ID (实际上是会话ID)
            
        Returns
        -------
        Dict[str, Any]
            选择结果
        """
        return self.switch_to_session(workstation_id)
    
    def stop_workstation(self, workstation_id: str) -> Dict[str, Any]:
        """
        停止工作台 - 停止指定会话
        
        Parameters
        ----------
        workstation_id : str
            工作台ID (实际上是会话ID)
            
        Returns
        -------
        Dict[str, Any]
            停止结果
        """
        return self.stop_session_monitoring(workstation_id)
    
    # ==================== 配置管理 ====================
    
    def get_label_configuration(self) -> Dict[str, Any]:
        """获取标签配置 - 直接使用通道服务"""
        try:
            return self.channel_service.get_configuration_for_ui()
        except Exception as e:
            return {
                'categories': {},
                'error': f'Failed to load configuration: {str(e)}'
            }
    
    def save_label_selection(self, selected_labels: Dict[str, str]) -> Dict[str, Any]:
        """保存标签选择 - 使用SessionService"""
        try:
            success, message = self.session_service.save_label_configuration(selected_labels)
            return {
                'success': success,
                'message': message
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to save labels: {str(e)}'
            }
    
    def load_label_selection(self) -> Dict[str, Any]:
        """加载标签选择 - 使用SessionService"""
        try:
            success, labels, error_msg = self.session_service.load_label_configuration()
            return {
                'success': success,
                'labels': labels,
                'error': error_msg if not success else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to load labels: {str(e)}'
            }
    
    # ==================== 文件管理 ====================
    
    def validate_file_path(self, file_path: str) -> Dict[str, Any]:
        """验证文件路径 - 直接验证"""
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
            
            # 检查文件大小
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
        """自动推断工作站ID - 从文件名推断"""
        try:
            import re
            
            path = Path(file_path)
            filename = path.stem
            
            # 尝试从文件名推断工作站ID
            # 匹配模式: MPL数字 或 包含数字的文件名
            patterns = [
                r'MPL(\d+)',  # MPL6, MPL12 等
                r'(\d+)',      # 任何数字
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
    
    # ==================== 监控管理 ====================
    
    def start_monitoring(self, file_path: str = None, config_path: str = "config/rules.yaml", 
                        run_id: str = None, workstation_id: str = None) -> Dict[str, Any]:
        """
        启动监控 - 使用SessionController
        
        Parameters
        ----------
        file_path : str, optional
            数据文件路径 (New Test)
        config_path : str
            配置文件路径
        run_id : str, optional
            运行ID
        workstation_id : str, optional
            工作站ID (Old Test)
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            # 获取当前会话
            current_session = self.session_service.get_current_session()
            if not current_session:
                return {
                    'success': False,
                    'error': '没有活动会话，请先选择测试类型'
                }
            
            # 根据测试类型启动监控
            if current_session.test_type.value == 'old':
                return self.start_old_test_monitoring(current_session.session_id)
            else:  # New Test
                return self.start_new_test_monitoring(current_session.session_id)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start monitoring: {str(e)}'
            }
    
    def start_simulation(self, file_path: str, config_path: str = "config/rules.yaml", 
                        run_id: str = None, workstation_id: str = "1") -> Dict[str, Any]:
        """
        启动模拟 - 使用SessionController
        
        Parameters
        ----------
        file_path : str
            数据文件路径
        config_path : str
            配置文件路径
        run_id : str, optional
            运行ID
        workstation_id : str
            工作站ID
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            # 获取当前会话
            current_session = self.session_service.get_current_session()
            if not current_session:
                return {
                    'success': False,
                    'error': '没有活动会话，请先选择测试类型'
                }
            
            # 根据测试类型启动模拟
            if current_session.test_type.value == 'old':
                return self.start_old_test_simulation(current_session.session_id)
            else:  # New Test
                return self.start_new_test_simulation(current_session.session_id)
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to start simulation: {str(e)}'
            }
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """停止监控 - 使用SessionController"""
        try:
            current_session = self.session_service.get_current_session()
            if not current_session:
                return {
                    'success': False,
                    'error': '没有活动会话'
                }
            
            return self.stop_session_monitoring(current_session.session_id)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to stop monitoring: {str(e)}'
            }
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """获取监控状态 - 使用SessionController"""
        try:
            current_session = self.session_service.get_current_session()
            if not current_session:
                return {
                    'success': True,
                    'status': {
                        'is_monitoring': False,
                        'web_monitoring_active': False,
                        'web_session_id': None,
                        'web_current_file': None
                    }
                }
            
            return self.get_session_status(current_session.session_id)
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get monitoring status: {str(e)}'
            }
    
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]) -> Dict[str, Any]:
        """添加告警处理器 - 直接使用监控服务"""
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
    
    # ==================== Web特有功能 ====================
    
    def get_web_status(self) -> Dict[str, Any]:
        """获取Web应用状态"""
        current_session = self.session_service.get_current_session()
        return {
            'success': True,
            'web_config': self.web_config,
            'current_session': current_session.to_dict() if current_session else None,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        }
    
    def reset_web_session(self) -> Dict[str, Any]:
        """Reset web session state"""
        try:
            self.web_config = {
                'current_file': None,
                'monitoring_active': False,
                'session_id': None
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