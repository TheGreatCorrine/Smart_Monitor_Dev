"""
backend/app/services/SessionService.py
------------------------------------
会话管理服务 - 管理Web应用的会话状态和业务流程
符合Clean Architecture原则，处理核心业务逻辑
"""
from __future__ import annotations

import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
from enum import Enum
import logging

from ..entities.record import Record
from ..entities.AlarmEvent import AlarmEvent


class TestType(Enum):
    """测试类型枚举"""
    OLD = "old"
    NEW = "new"


class SessionStatus(Enum):
    """会话状态枚举"""
    PENDING = "pending"         # 等待配置
    CONFIGURED = "configured"   # 已配置，等待启动
    RUNNING = "running"         # 运行中
    STOPPED = "stopped"         # 已停止
    ERROR = "error"            # 错误状态


class SessionConfiguration:
    """会话配置"""
    
    def __init__(self):
        self.test_type: Optional[TestType] = None
        self.selected_file: Optional[str] = None
        self.selected_workstation: Optional[str] = None
        self.selected_labels: Dict[str, str] = {}
        self.config_path: str = "config/rules.yaml"
        self.run_id: Optional[str] = None
        self.workstation_id: Optional[str] = None
    
    def is_valid_for_old_test(self) -> Tuple[bool, str]:
        """验证Old Test配置"""
        if not self.selected_workstation:
            return False, "请先选择工作台"
        return True, ""
    
    def is_valid_for_new_test(self) -> Tuple[bool, str]:
        """验证New Test配置"""
        if not self.selected_file:
            return False, "请先选择数据文件"
        if not self.selected_labels:
            return False, "请配置标签匹配"
        if not self._validate_file_path(self.selected_file):
            return False, f"文件不存在或格式错误: {self.selected_file}"
        return True, ""
    
    def validate_file_path(self, file_path: str) -> bool:
        """验证文件路径"""
        try:
            path = Path(file_path)
            return path.exists() and path.suffix.lower() == '.dat'
        except Exception:
            return False


class Session:
    """会话实体"""
    
    def __init__(self, session_id: str, test_type: TestType):
        self.session_id = session_id
        self.test_type = test_type
        self.status = SessionStatus.PENDING
        self.configuration = SessionConfiguration()
        self.configuration.test_type = test_type
        
        # 会话统计
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.stopped_at: Optional[datetime] = None
        self.records_processed = 0
        self.alarms_generated = 0
        self.processing_speed = 0.0
        
        # 运行时数据
        self.current_run_id: Optional[str] = None
        self.error_message: Optional[str] = None
    
    def update_statistics(self, records_processed: int, alarms_generated: int):
        """更新会话统计信息"""
        self.records_processed = records_processed
        self.alarms_generated = alarms_generated
        
        # 计算处理速度
        if self.started_at and records_processed > 0:
            elapsed_seconds = (datetime.now() - self.started_at).total_seconds()
            if elapsed_seconds > 0:
                self.processing_speed = records_processed / elapsed_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'session_id': self.session_id,
            'test_type': self.test_type.value,
            'status': self.status.value,
            'configuration': {
                'selected_file': self.configuration.selected_file,
                'selected_workstation': self.configuration.selected_workstation,
                'selected_labels': self.configuration.selected_labels,
                'config_path': self.configuration.config_path,
                'run_id': self.configuration.run_id,
                'workstation_id': self.configuration.workstation_id
            },
            'statistics': {
                'created_at': self.created_at.isoformat(),
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None,
                'records_processed': self.records_processed,
                'alarms_generated': self.alarms_generated,
                'processing_speed': self.processing_speed
            },
            'current_run_id': self.current_run_id,
            'error_message': self.error_message
        }


class SessionService:
    """
    会话管理服务
    
    职责：
    1. 管理测试会话的完整生命周期
    2. 处理业务流程验证和控制
    3. 维护会话状态和统计信息
    4. 提供会话查询和管理接口
    """
    
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
        self.current_session_id: Optional[str] = None
        self.logger = logging.getLogger(__name__)
    
    # ==================== 会话生命周期管理 ====================
    
    def create_session(self, test_type: TestType) -> str:
        """
        创建新会话
        
        Parameters
        ----------
        test_type : TestType
            测试类型 (OLD 或 NEW)
            
        Returns
        -------
        str
            会话ID
        """
        session_id = f"{test_type.value}_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%H%M%S')}"
        session = Session(session_id, test_type)
        
        self.sessions[session_id] = session
        self.current_session_id = session_id
        
        self.logger.info(f"Created {test_type.value} session: {session_id}")
        return session_id
    
    def configure_session(self, session_id: str, **kwargs) -> Tuple[bool, str]:
        """
        配置会话参数
        
        Parameters
        ----------
        session_id : str
            会话ID
        **kwargs
            配置参数 (selected_file, selected_workstation, selected_labels等)
            
        Returns
        -------
        Tuple[bool, str]
            (成功标志, 错误信息)
        """
        session = self.sessions.get(session_id)
        if not session:
            return False, f"会话不存在: {session_id}"
        
        # 更新配置
        config = session.configuration
        if 'selected_file' in kwargs:
            config.selected_file = kwargs['selected_file']
        if 'selected_workstation' in kwargs:
            config.selected_workstation = kwargs['selected_workstation']
        if 'selected_labels' in kwargs:
            config.selected_labels = kwargs['selected_labels']
        if 'config_path' in kwargs:
            config.config_path = kwargs['config_path']
        if 'workstation_id' in kwargs:
            config.workstation_id = kwargs['workstation_id']
        
        # 验证配置
        if session.test_type == TestType.OLD:
            is_valid, error_msg = config.is_valid_for_old_test()
        else:  # TestType.NEW
            is_valid, error_msg = config.is_valid_for_new_test()
        
        if is_valid:
            session.status = SessionStatus.CONFIGURED
            self.logger.info(f"Session {session_id} configured successfully")
            return True, ""
        else:
            session.status = SessionStatus.ERROR
            session.error_message = error_msg
            self.logger.error(f"Session {session_id} configuration failed: {error_msg}")
            return False, error_msg
    
    def start_session(self, session_id: str) -> Tuple[bool, str, Optional[str]]:
        """
        启动会话监控
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Tuple[bool, str, Optional[str]]
            (成功标志, 消息, 运行ID)
        """
        session = self.sessions.get(session_id)
        if not session:
            return False, f"会话不存在: {session_id}", None
        
        if session.status != SessionStatus.CONFIGURED:
            return False, f"会话状态不正确: {session.status.value}", None
        
        # 生成运行ID
        run_id = f"{session.test_type.value}_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        session.configuration.run_id = run_id
        session.current_run_id = run_id
        session.started_at = datetime.now()
        session.status = SessionStatus.RUNNING
        
        self.logger.info(f"Session {session_id} started with run_id: {run_id}")
        return True, f"监控启动成功 - {run_id}", run_id
    
    def stop_session(self, session_id: str) -> Tuple[bool, str]:
        """
        停止会话监控
        
        Parameters
        ----------
        session_id : str
            会话ID
            
        Returns
        -------
        Tuple[bool, str]
            (成功标志, 消息)
        """
        session = self.sessions.get(session_id)
        if not session:
            return False, f"会话不存在: {session_id}"
        
        session.stopped_at = datetime.now()
        session.status = SessionStatus.STOPPED
        
        self.logger.info(f"Session {session_id} stopped")
        return True, "监控已停止"
    
    # ==================== 会话查询和管理 ====================
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话实例"""
        return self.sessions.get(session_id)
    
    def get_current_session(self) -> Optional[Session]:
        """获取当前活动会话"""
        if self.current_session_id:
            return self.sessions.get(self.current_session_id)
        return None
    
    def list_sessions(self, test_type: Optional[TestType] = None) -> List[Session]:
        """
        列出会话
        
        Parameters
        ----------
        test_type : Optional[TestType]
            可选的测试类型过滤器
            
        Returns
        -------
        List[Session]
            会话列表
        """
        sessions = list(self.sessions.values())
        if test_type:
            sessions = [s for s in sessions if s.test_type == test_type]
        
        # 按创建时间倒序排列
        sessions.sort(key=lambda x: x.created_at, reverse=True)
        return sessions
    
    def get_running_sessions(self) -> List[Session]:
        """获取所有运行中的会话"""
        return [s for s in self.sessions.values() if s.status == SessionStatus.RUNNING]
    
    def switch_session(self, session_id: str) -> Tuple[bool, str]:
        """
        切换当前活动会话
        
        Parameters
        ----------
        session_id : str
            目标会话ID
            
        Returns
        -------
        Tuple[bool, str]
            (成功标志, 消息)
        """
        if session_id not in self.sessions:
            return False, f"会话不存在: {session_id}"
        
        self.current_session_id = session_id
        session = self.sessions[session_id]
        
        self.logger.info(f"Switched to session: {session_id}")
        return True, f"已切换到会话: {session_id} ({session.test_type.value})"
    
    # ==================== 业务流程控制 ====================
    
    def create_and_configure_old_test_session(self, selected_workstation: str, 
                                             config_path: str = "config/rules.yaml") -> Tuple[bool, str, Optional[str]]:
        """
        创建并配置Old Test会话的完整流程
        
        Parameters
        ----------
        selected_workstation : str
            选择的工作台ID
        config_path : str
            配置文件路径
            
        Returns
        -------
        Tuple[bool, str, Optional[str]]
            (成功标志, 消息, 会话ID)
        """
        try:
            # 创建会话
            session_id = self.create_session(TestType.OLD)
            
            # 配置会话
            success, error_msg = self.configure_session(
                session_id,
                selected_workstation=selected_workstation,
                config_path=config_path
            )
            
            if success:
                return True, f"Old Test会话创建成功: {session_id}", session_id
            else:
                return False, error_msg, None
                
        except Exception as e:
            self.logger.error(f"Failed to create Old Test session: {e}")
            return False, f"创建Old Test会话失败: {str(e)}", None
    
    def create_and_configure_new_test_session(self, selected_file: str, selected_labels: Dict[str, str],
                                             workstation_id: str = "1", 
                                             config_path: str = "config/rules.yaml") -> Tuple[bool, str, Optional[str]]:
        """
        创建并配置New Test会话的完整流程
        
        Parameters
        ----------
        selected_file : str
            选择的数据文件路径
        selected_labels : Dict[str, str]
            标签配置
        workstation_id : str
            工作站ID
        config_path : str
            配置文件路径
            
        Returns
        -------
        Tuple[bool, str, Optional[str]]
            (成功标志, 消息, 会话ID)
        """
        try:
            # 创建会话
            session_id = self.create_session(TestType.NEW)
            
            # 配置会话
            success, error_msg = self.configure_session(
                session_id,
                selected_file=selected_file,
                selected_labels=selected_labels,
                workstation_id=workstation_id,
                config_path=config_path
            )
            
            if success:
                return True, f"New Test会话创建成功: {session_id}", session_id
            else:
                return False, error_msg, None
                
        except Exception as e:
            self.logger.error(f"Failed to create New Test session: {e}")
            return False, f"创建New Test会话失败: {str(e)}", None
    
    def update_session_statistics(self, session_id: str, records_processed: int, alarms_generated: int):
        """更新会话统计信息"""
        session = self.sessions.get(session_id)
        if session:
            session.update_statistics(records_processed, alarms_generated)
    
    # ==================== 标签配置管理 ====================
    
    def save_label_configuration(self, selected_labels: Dict[str, str]) -> Tuple[bool, str]:
        """
        保存标签配置到文件
        
        Parameters
        ----------
        selected_labels : Dict[str, str]
            标签配置
            
        Returns
        -------
        Tuple[bool, str]
            (成功标志, 消息)
        """
        try:
            label_selection_path = Path("label_selection.json")
            with open(label_selection_path, 'w', encoding='utf-8') as f:
                json.dump(selected_labels, f, ensure_ascii=False, indent=2)
            
            self.logger.info("Label configuration saved successfully")
            return True, "标签配置保存成功"
            
        except Exception as e:
            self.logger.error(f"Failed to save label configuration: {e}")
            return False, f"保存标签配置失败: {str(e)}"
    
    def load_label_configuration(self) -> Tuple[bool, Dict[str, str], str]:
        """
        从文件加载标签配置
        
        Returns
        -------
        Tuple[bool, Dict[str, str], str]
            (成功标志, 标签配置, 错误消息)
        """
        try:
            label_selection_path = Path("label_selection.json")
            
            if not label_selection_path.exists():
                return True, {}, ""
            
            with open(label_selection_path, 'r', encoding='utf-8') as f:
                labels = json.load(f)
            
            self.logger.info("Label configuration loaded successfully")
            return True, labels, ""
            
        except Exception as e:
            self.logger.error(f"Failed to load label configuration: {e}")
            return False, {}, f"加载标签配置失败: {str(e)}" 