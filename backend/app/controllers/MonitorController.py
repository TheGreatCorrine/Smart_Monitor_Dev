"""
backend/app/controllers/MonitorController.py
------------------------------------
监控控制器 - 处理监控相关的用户请求
负责数据文件处理、实时监控、状态查询
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..usecases.Monitor import MonitorService
from ..entities.record import Record
from ..entities.AlarmEvent import AlarmEvent


class MonitorController:
    """
    监控控制器
    
    职责：
    1. 处理数据文件监控请求
    2. 处理实时监控请求
    3. 查询监控状态
    4. 格式化监控结果
    """
    
    def __init__(self, monitor_service: MonitorService):
        self.monitor_service = monitor_service
        self.logger = logging.getLogger(__name__)
    
    def process_data_file(self, file_path: str, run_id: str) -> Dict[str, Any]:
        """
        处理数据文件
        
        Parameters
        ----------
        file_path : str
            数据文件路径
        run_id : str
            运行ID
            
        Returns
        -------
        Dict[str, Any]
            处理结果
        """
        try:
            # 验证文件路径
            if not self._validate_file_path(file_path):
                return {
                    'success': False,
                    'error': f"文件不存在或格式错误: {file_path}"
                }
            
            # 调用监控服务
            alarms, records_count = self.monitor_service.process_data_file(file_path, run_id)
            
            # 格式化结果
            return {
                'success': True,
                'data': {
                    'file_path': file_path,
                    'run_id': run_id,
                    'records_count': records_count,
                    'alarms_count': len(alarms),
                    'alarms': [self._format_alarm(alarm) for alarm in alarms]
                }
            }
            
        except Exception as e:
            self.logger.error(f"处理数据文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_record(self, record: Record, run_id: str) -> Dict[str, Any]:
        """
        处理单条记录
        
        Parameters
        ----------
        record : Record
            传感器记录
        run_id : str
            运行ID
            
        Returns
        -------
        Dict[str, Any]
            处理结果
        """
        try:
            # 调用监控服务
            alarms = self.monitor_service.process_record(record, run_id)
            
            # 格式化结果
            return {
                'success': True,
                'data': {
                    'run_id': run_id,
                    'timestamp': record.ts.isoformat(),
                    'alarms_count': len(alarms),
                    'alarms': [self._format_alarm(alarm) for alarm in alarms]
                }
            }
            
        except Exception as e:
            self.logger.error(f"处理记录失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_monitor_status(self) -> Dict[str, Any]:
        """
        获取监控状态
        
        Returns
        -------
        Dict[str, Any]
            监控状态信息
        """
        try:
            # 获取规则摘要
            rule_summary = self.monitor_service.get_rule_summary()
            
            return {
                'success': True,
                'data': {
                    'status': 'active',
                    'rules': rule_summary,
                    'alarm_handlers_count': len(self.monitor_service.alarm_handlers)
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取监控状态失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_alarm_handler(self, handler_name: str, handler_func) -> Dict[str, Any]:
        """
        添加告警处理器
        
        Parameters
        ----------
        handler_name : str
            处理器名称
        handler_func : Callable
            处理函数
            
        Returns
        -------
        Dict[str, Any]
            操作结果
        """
        try:
            # 验证输入
            if not handler_name:
                raise ValueError("处理器名称不能为空")
            if not callable(handler_func):
                raise ValueError("处理器必须是可调用对象")
            
            # 添加处理器
            self.monitor_service.add_alarm_handler(handler_func)
            
            return {
                'success': True,
                'message': f"告警处理器 '{handler_name}' 添加成功"
            }
            
        except Exception as e:
            self.logger.error(f"添加告警处理器失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_file_path(self, file_path: str) -> bool:
        """验证文件路径"""
        try:
            path = Path(file_path)
            return path.exists() and path.suffix.lower() == '.dat'
        except Exception:
            return False
    
    def _format_alarm(self, alarm: AlarmEvent) -> Dict[str, Any]:
        """格式化告警事件"""
        return {
            'id': alarm.id,
            'rule_id': alarm.rule_id,
            'rule_name': alarm.rule_name,
            'severity': alarm.severity.value,
            'timestamp': alarm.timestamp.isoformat(),
            'description': alarm.description,
            'sensor_values': alarm.sensor_values
        } 