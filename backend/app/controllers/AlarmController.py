"""
backend/app/controllers/AlarmController.py
------------------------------------
告警控制器 - 处理告警相关的用户请求
负责输入验证、调用服务、格式化输出
"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from ..entities.AlarmEvent import AlarmEvent, AlarmStatus
from ..services.AlarmService import AlarmService, AlarmFilter
from ..services import IAlarmService


class AlarmController:
    """
    告警控制器
    
    职责：
    1. 接收告警相关的用户请求
    2. 验证输入参数
    3. 调用告警服务
    4. 格式化输出结果
    5. 处理异常和错误
    """
    
    def __init__(self, alarm_service: IAlarmService):
        self.alarm_service = alarm_service
        self.logger = logging.getLogger(__name__)
    
    def list_alarms(self, 
                   severity: Optional[str] = None,
                   status: Optional[str] = None,
                   rule_id: Optional[str] = None,
                   run_id: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """
        列出告警事件
        
        Parameters
        ----------
        severity : str, optional
            严重程度过滤
        status : str, optional
            状态过滤
        rule_id : str, optional
            规则ID过滤
        run_id : str, optional
            运行ID过滤
        start_time : datetime, optional
            开始时间
        end_time : datetime, optional
            结束时间
            
        Returns
        -------
        Dict[str, Any]
            格式化的告警列表
        """
        try:
            # 验证输入参数
            self._validate_list_params(severity, status)
            
            # 构建过滤器
            filter_params = AlarmFilter(
                severity=severity,
                status=AlarmStatus(status) if status else None,
                rule_id=rule_id,
                run_id=run_id,
                start_time=start_time,
                end_time=end_time
            )
            
            # 调用服务
            alarms = self.alarm_service.list_alarms(filter_params)
            
            # 格式化输出
            return {
                'success': True,
                'data': {
                    'alarms': [self._format_alarm(alarm) for alarm in alarms],
                    'count': len(alarms)
                }
            }
            
        except Exception as e:
            self.logger.error(f"列出告警失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alarm(self, alarm_id: str) -> Dict[str, Any]:
        """
        获取单个告警事件
        
        Parameters
        ----------
        alarm_id : str
            告警ID
            
        Returns
        -------
        Dict[str, Any]
            格式化的告警信息
        """
        try:
            # 验证输入
            if not alarm_id:
                raise ValueError("告警ID不能为空")
            
            # 调用服务
            alarm = self.alarm_service.get_alarm(alarm_id)
            
            if not alarm:
                return {
                    'success': False,
                    'error': f"告警不存在: {alarm_id}"
                }
            
            # 格式化输出
            return {
                'success': True,
                'data': self._format_alarm(alarm)
            }
            
        except Exception as e:
            self.logger.error(f"获取告警失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def acknowledge_alarm(self, alarm_id: str, user: str) -> Dict[str, Any]:
        """
        确认告警
        
        Parameters
        ----------
        alarm_id : str
            告警ID
        user : str
            确认用户
            
        Returns
        -------
        Dict[str, Any]
            操作结果
        """
        try:
            # 验证输入
            if not alarm_id:
                raise ValueError("告警ID不能为空")
            if not user:
                raise ValueError("用户不能为空")
            
            # 调用服务
            success = self.alarm_service.acknowledge_alarm(alarm_id, user)
            
            if success:
                return {
                    'success': True,
                    'message': f"告警 {alarm_id} 已确认"
                }
            else:
                return {
                    'success': False,
                    'error': f"确认告警失败: {alarm_id}"
                }
                
        except Exception as e:
            self.logger.error(f"确认告警失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def resolve_alarm(self, alarm_id: str, user: str) -> Dict[str, Any]:
        """
        解决告警
        
        Parameters
        ----------
        alarm_id : str
            告警ID
        user : str
            解决用户
            
        Returns
        -------
        Dict[str, Any]
            操作结果
        """
        try:
            # 验证输入
            if not alarm_id:
                raise ValueError("告警ID不能为空")
            if not user:
                raise ValueError("用户不能为空")
            
            # 调用服务
            success = self.alarm_service.resolve_alarm(alarm_id, user)
            
            if success:
                return {
                    'success': True,
                    'message': f"告警 {alarm_id} 已解决"
                }
            else:
                return {
                    'success': False,
                    'error': f"解决告警失败: {alarm_id}"
                }
                
        except Exception as e:
            self.logger.error(f"解决告警失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_alarm_statistics(self) -> Dict[str, Any]:
        """
        获取告警统计信息
        
        Returns
        -------
        Dict[str, Any]
            统计信息
        """
        try:
            stats = self.alarm_service.get_alarm_statistics()
            
            return {
                'success': True,
                'data': stats
            }
            
        except Exception as e:
            self.logger.error(f"获取告警统计失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_list_params(self, severity: Optional[str], status: Optional[str]):
        """验证列表参数"""
        if severity and severity not in ['low', 'medium', 'high', 'critical']:
            raise ValueError(f"无效的严重程度: {severity}")
        
        if status and status not in ['active', 'acknowledged', 'resolved', 'cleared']:
            raise ValueError(f"无效的状态: {status}")
    
    def _format_alarm(self, alarm: AlarmEvent) -> Dict[str, Any]:
        """格式化告警事件"""
        return {
            'id': alarm.id,
            'rule_id': alarm.rule_id,
            'rule_name': alarm.rule_name,
            'severity': alarm.severity.value,
            'status': alarm.status.value,
            'timestamp': alarm.timestamp.isoformat(),
            'description': alarm.description,
            'sensor_values': alarm.sensor_values,
            'run_id': alarm.run_id,
            'acknowledged_by': alarm.acknowledged_by,
            'acknowledged_at': alarm.acknowledged_at.isoformat() if alarm.acknowledged_at else None,
            'resolved_by': alarm.resolved_by,
            'resolved_at': alarm.resolved_at.isoformat() if alarm.resolved_at else None
        } 