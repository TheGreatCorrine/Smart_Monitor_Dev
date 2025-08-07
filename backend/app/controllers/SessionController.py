"""
backend/app/controllers/SessionController.py
------------------------------------
会话控制器 - 处理会话管理相关的Web请求
将前端的业务逻辑移到后端，符合Clean Architecture
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
import logging

from ..services.SessionService import SessionService, TestType, SessionStatus
from ..usecases.Monitor import MonitorService


class SessionController:
    """
    会话控制器
    
    职责：
    1. 处理测试类型选择和会话创建
    2. 管理Old Test和New Test的配置流程
    3. 控制监控启动和停止
    4. 提供会话状态查询接口
    """
    
    def __init__(self, session_service: SessionService, monitor_service: MonitorService):
        self.session_service = session_service
        self.monitor_service = monitor_service
        self.logger = logging.getLogger(__name__)
    
    # ==================== 测试选择和会话创建 ====================
    
    def select_test_type(self, test_type: str) -> Dict[str, Any]:
        """
        选择测试类型并创建会话
        
        Parameters
        ----------
        test_type : str
            测试类型 ("old" 或 "new")
            
        Returns
        -------
        Dict[str, Any]
            操作结果
        """
        try:
            if test_type not in ["old", "new"]:
                return {
                    'success': False,
                    'error': f"不支持的测试类型: {test_type}"
                }
            
            # 创建会话
            test_type_enum = TestType.OLD if test_type == "old" else TestType.NEW
            session_id = self.session_service.create_session(test_type_enum)
            
            return {
                'success': True,
                'session_id': session_id,
                'test_type': test_type,
                'message': f"已创建{test_type.upper()}测试会话",
                'next_step': 'workstation_selection' if test_type == 'old' else 'file_configuration'
            }
            
        except Exception as e:
            self.logger.error(f"Failed to select test type: {e}")
            return {
                'success': False,
                'error': f"选择测试类型失败: {str(e)}"
            }
    
    # ==================== Old Test 工作流 ====================
    
    def configure_old_test_session(self, session_id: str, workstation_id: str, 
                                 config_path: str = "config/rules.yaml") -> Dict[str, Any]:
        """
        配置Old Test会话
        
        Parameters
        ----------
        session_id : str
            会话ID
        workstation_id : str
            工作台ID
        config_path : str
            配置文件路径
            
        Returns
        -------
        Dict[str, Any]
            配置结果
        """
        try:
            # 配置会话
            success, error_msg = self.session_service.configure_session(
                session_id,
                selected_workstation=workstation_id,
                config_path=config_path
            )
            
            if success:
                return {
                    'success': True,
                    'session_id': session_id,
                    'workstation_id': workstation_id,
                    'message': 'Old Test会话配置成功',
                    'ready_to_start': True
                }
            else:
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Failed to configure Old Test session: {e}")
            return {
                'success': False,
                'error': f"配置Old Test会话失败: {str(e)}"
            }
    
    def start_old_test_monitoring(self, session_id: str) -> Dict[str, Any]:
        """
        启动Old Test监控
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': f"会话不存在: {session_id}"
                }
            
            # 启动会话
            success, message, run_id = self.session_service.start_session(session_id)
            if not success:
                return {
                    'success': False,
                    'error': message
                }
            
            # 启动监控服务
            monitor_success = self.monitor_service.start_continuous_monitoring(run_id)
            if not monitor_success:
                # 如果监控启动失败，回滚会话状态
                self.session_service.stop_session(session_id)
                return {
                    'success': False,
                    'error': '监控服务启动失败'
                }
            
            return {
                'success': True,
                'session_id': session_id,
                'session_name': f"Old Test - {session.configuration.selected_workstation}",
                'run_id': run_id,
                'message': message,
                'workstation_id': session.configuration.selected_workstation
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start Old Test monitoring: {e}")
            return {
                'success': False,
                'error': f"启动Old Test监控失败: {str(e)}"
            }
    
    def start_old_test_simulation(self, session_id: str) -> Dict[str, Any]:
        """
        启动Old Test模拟
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': f"会话不存在: {session_id}"
                }
            
            # 启动会话
            success, message, run_id = self.session_service.start_session(session_id)
            if not success:
                return {
                    'success': False,
                    'error': message
                }
            
            # TODO: 这里需要设置模拟文件提供者
            # 暂时使用基本的监控启动
            monitor_success = self.monitor_service.start_continuous_monitoring(run_id)
            if not monitor_success:
                self.session_service.stop_session(session_id)
                return {
                    'success': False,
                    'error': '模拟启动失败'
                }
            
            return {
                'success': True,
                'session_id': session_id,
                'session_name': f"Old Test Simulation - {session.configuration.selected_workstation}",
                'run_id': run_id,
                'message': f"模拟启动成功 - {run_id}",
                'workstation_id': session.configuration.selected_workstation
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start Old Test simulation: {e}")
            return {
                'success': False,
                'error': f"启动Old Test模拟失败: {str(e)}"
            }
    
    # ==================== New Test 工作流 ====================
    
    def configure_new_test_session(self, session_id: str, file_path: str, 
                                 selected_labels: Dict[str, str], workstation_id: str = "1",
                                 config_path: str = "config/rules.yaml") -> Dict[str, Any]:
        """
        配置New Test会话
        
        Parameters
        ----------
        session_id : str
            会话ID
        file_path : str
            数据文件路径
        selected_labels : Dict[str, str]
            标签配置
        workstation_id : str
            工作站ID
        config_path : str
            配置文件路径
            
        Returns
        -------
        Dict[str, Any]
            配置结果
        """
        try:
            # 先保存标签配置
            save_success, save_message = self.session_service.save_label_configuration(selected_labels)
            if not save_success:
                return {
                    'success': False,
                    'error': f"保存标签配置失败: {save_message}"
                }
            
            # 配置会话
            success, error_msg = self.session_service.configure_session(
                session_id,
                selected_file=file_path,
                selected_labels=selected_labels,
                workstation_id=workstation_id,
                config_path=config_path
            )
            
            if success:
                return {
                    'success': True,
                    'session_id': session_id,
                    'file_path': file_path,
                    'selected_labels': selected_labels,
                    'workstation_id': workstation_id,
                    'message': 'New Test会话配置成功',
                    'ready_to_start': True
                }
            else:
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            self.logger.error(f"Failed to configure New Test session: {e}")
            return {
                'success': False,
                'error': f"配置New Test会话失败: {str(e)}"
            }
    
    def start_new_test_monitoring(self, session_id: str) -> Dict[str, Any]:
        """
        启动New Test监控
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': f"会话不存在: {session_id}"
                }
            
            # 验证会话配置
            if session.test_type.value != 'new':
                return {
                    'success': False,
                    'error': f"会话类型错误: {session.test_type.value}，期望: new"
                }
            
            # 检查是否已配置文件和标签
            if not session.configuration.selected_file:
                return {
                    'success': False,
                    'error': '请先选择数据文件'
                }
            
            if not session.configuration.selected_labels:
                return {
                    'success': False,
                    'error': '请先配置标签匹配'
                }
            
            # 验证文件路径
            if not session.configuration.validate_file_path(session.configuration.selected_file):
                return {
                    'success': False,
                    'error': f'文件不存在或格式错误: {session.configuration.selected_file}'
                }
            
            # 启动会话
            success, message, run_id = self.session_service.start_session(session_id)
            if not success:
                return {
                    'success': False,
                    'error': message
                }
            
            # 启动监控服务
            monitor_success = self.monitor_service.start_continuous_monitoring(run_id)
            if not monitor_success:
                self.session_service.stop_session(session_id)
                return {
                    'success': False,
                    'error': '监控服务启动失败'
                }
            
            file_name = session.configuration.selected_file.split('/')[-1] if session.configuration.selected_file else "未知文件"
            
            return {
                'success': True,
                'session_id': session_id,
                'session_name': f"New Test - {file_name}",
                'run_id': run_id,
                'message': message,
                'file_path': session.configuration.selected_file,
                'workstation_id': session.configuration.workstation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start New Test monitoring: {e}")
            return {
                'success': False,
                'error': f"启动New Test监控失败: {str(e)}"
            }
    
    def start_new_test_simulation(self, session_id: str) -> Dict[str, Any]:
        """
        启动New Test模拟
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Dict[str, Any]
            启动结果
        """
        try:
            session = self.session_service.get_session(session_id)
            if not session:
                return {
                    'success': False,
                    'error': f"会话不存在: {session_id}"
                }
            
            # 验证会话配置
            if session.test_type.value != 'new':
                return {
                    'success': False,
                    'error': f"会话类型错误: {session.test_type.value}，期望: new"
                }
            
            # 检查是否已配置文件和标签
            if not session.configuration.selected_file:
                return {
                    'success': False,
                    'error': '请先选择数据文件'
                }
            
            if not session.configuration.selected_labels:
                return {
                    'success': False,
                    'error': '请先配置标签匹配'
                }
            
            # 验证文件路径
            if not session.configuration.validate_file_path(session.configuration.selected_file):
                return {
                    'success': False,
                    'error': f'文件不存在或格式错误: {session.configuration.selected_file}'
                }
            
            # 启动会话
            success, message, run_id = self.session_service.start_session(session_id)
            if not success:
                return {
                    'success': False,
                    'error': message
                }
            
            # TODO: 这里需要设置文件提供者进行模拟
            # 暂时使用基本的监控启动
            monitor_success = self.monitor_service.start_continuous_monitoring(run_id)
            if not monitor_success:
                self.session_service.stop_session(session_id)
                return {
                    'success': False,
                    'error': '模拟启动失败'
                }
            
            file_name = session.configuration.selected_file.split('/')[-1] if session.configuration.selected_file else "未知文件"
            
            return {
                'success': True,
                'session_id': session_id,
                'session_name': f"New Test Simulation - {file_name}",
                'run_id': run_id,
                'message': f"模拟启动成功 - {run_id}",
                'file_path': session.configuration.selected_file,
                'workstation_id': session.configuration.workstation_id
            }
            
        except Exception as e:
            self.logger.error(f"Failed to start New Test simulation: {e}")
            return {
                'success': False,
                'error': f"启动New Test模拟失败: {str(e)}"
            }
    
    # ==================== 通用会话管理 ====================
    
    def stop_session_monitoring(self, session_id: str) -> Dict[str, Any]:
        """
        停止会话监控
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Dict[str, Any]
            停止结果
        """
        try:
            # 停止监控服务
            monitor_success = self.monitor_service.stop_continuous_monitoring()
            
            # 停止会话
            success, message = self.session_service.stop_session(session_id)
            
            return {
                'success': success and monitor_success,
                'session_id': session_id,
                'message': message if success else f"停止会话失败: {message}",
                'monitor_stopped': monitor_success
            }
            
        except Exception as e:
            self.logger.error(f"Failed to stop session monitoring: {e}")
            return {
                'success': False,
                'error': f"停止监控失败: {str(e)}"
            }
    
    def get_session_status(self, session_id: str = None) -> Dict[str, Any]:
        """
        获取会话状态
        
        Parameters
        ----------
        session_id : str, optional
            会话ID，如果为None则返回当前活动会话
            
        Returns
        -------
        Dict[str, Any]
            会话状态信息
        """
        try:
            if session_id:
                session = self.session_service.get_session(session_id)
            else:
                session = self.session_service.get_current_session()
                session_id = self.session_service.current_session_id
            
            if not session:
                return {
                    'success': False,
                    'error': '会话不存在'
                }
            
            # 获取监控状态
            monitor_status = self.monitor_service.get_monitoring_status()
            
            # 更新会话统计信息
            if monitor_status.get('stats'):
                stats = monitor_status['stats']
                self.session_service.update_session_statistics(
                    session_id,
                    stats.get('total_records_processed', 0),
                    stats.get('total_alarms_generated', 0)
                )
            
            # 合并会话和监控状态
            session_data = session.to_dict()
            session_data.update({
                'monitoring_status': monitor_status,
                'is_monitoring': monitor_status.get('is_monitoring', False)
            })
            
            return {
                'success': True,
                'session': session_data
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get session status: {e}")
            return {
                'success': False,
                'error': f"获取会话状态失败: {str(e)}"
            }
    
    def list_all_sessions(self, test_type: str = None) -> Dict[str, Any]:
        """
        列出所有会话
        
        Parameters
        ----------
        test_type : str, optional
            测试类型过滤器 ("old" 或 "new")
            
        Returns
        -------
        Dict[str, Any]
            会话列表
        """
        try:
            test_type_enum = None
            if test_type:
                test_type_enum = TestType.OLD if test_type == "old" else TestType.NEW
            
            sessions = self.session_service.list_sessions(test_type_enum)
            
            return {
                'success': True,
                'sessions': [session.to_dict() for session in sessions],
                'current_session_id': self.session_service.current_session_id,
                'total_count': len(sessions)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to list sessions: {e}")
            return {
                'success': False,
                'error': f"获取会话列表失败: {str(e)}"
            }
    
    def switch_to_session(self, session_id: str) -> Dict[str, Any]:
        """
        切换到指定会话
        
        Parameters
        ----------
        session_id : str
            目标会话ID
            
        Returns
        -------
        Dict[str, Any]
            切换结果
        """
        try:
            success, message = self.session_service.switch_session(session_id)
            
            if success:
                session = self.session_service.get_session(session_id)
                return {
                    'success': True,
                    'session_id': session_id,
                    'test_type': session.test_type.value,
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': message
                }
                
        except Exception as e:
            self.logger.error(f"Failed to switch session: {e}")
            return {
                'success': False,
                'error': f"切换会话失败: {str(e)}"
            } 