"""
backend/app/services/AlarmService.py
------------------------------------
告警服务 - 负责告警事件的创建、管理和状态更新
"""
from __future__ import annotations

import uuid
import logging
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass

from ..entities.Rule import Rule
from ..entities.Record import Record
from ..entities.AlarmEvent import AlarmEvent, AlarmStatus
from . import IAlarmService


@dataclass
class AlarmFilter:
    """告警过滤器"""
    severity: Optional[str] = None
    status: Optional[AlarmStatus] = None
    rule_id: Optional[str] = None
    run_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AlarmService(IAlarmService):
    """
    告警服务
    
    负责告警事件的创建、查询、状态管理
    遵循单一职责原则
    """
    
    def __init__(self):
        self.alarms: Dict[str, AlarmEvent] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_alarm(self, rule: Rule, record: Record, run_id: str) -> AlarmEvent:
        """
        创建告警事件
        
        Parameters
        ----------
        rule : Rule
            触发的规则
        record : Record
            传感器记录
        run_id : str
            测试会话ID
            
        Returns
        -------
        AlarmEvent
            创建的告警事件
        """
        try:
            # 生成唯一ID
            alarm_id = f"ALARM_{rule.id}_{uuid.uuid4().hex[:8]}"
            
            alarm = AlarmEvent(
                id=alarm_id,
                rule_id=rule.id,
                rule_name=rule.name,
                severity=rule.severity,
                timestamp=record.ts,
                description=f"规则 '{rule.name}' 触发: {rule.description}",
                sensor_values=record.metrics.copy(),
                run_id=run_id,
                file_pos=record.file_pos
            )
            
            # 存储告警
            self.alarms[alarm_id] = alarm
            self.logger.info(f"创建告警事件: {alarm_id}")
            
            return alarm
            
        except Exception as e:
            self.logger.error(f"创建告警事件失败: {e}")
            raise
    
    def acknowledge_alarm(self, alarm_id: str, user: str) -> bool:
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
        bool
            是否成功确认
        """
        try:
            if alarm_id not in self.alarms:
                self.logger.warning(f"告警不存在: {alarm_id}")
                return False
            
            alarm = self.alarms[alarm_id]
            alarm.status = AlarmStatus.ACKNOWLEDGED
            alarm.acknowledged_by = user
            alarm.acknowledged_at = datetime.now()
            
            self.logger.info(f"告警已确认: {alarm_id} by {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"确认告警失败: {e}")
            return False
    
    def resolve_alarm(self, alarm_id: str, user: str) -> bool:
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
        bool
            是否成功解决
        """
        try:
            if alarm_id not in self.alarms:
                self.logger.warning(f"告警不存在: {alarm_id}")
                return False
            
            alarm = self.alarms[alarm_id]
            alarm.status = AlarmStatus.RESOLVED
            alarm.resolved_by = user
            alarm.resolved_at = datetime.now()
            
            self.logger.info(f"告警已解决: {alarm_id} by {user}")
            return True
            
        except Exception as e:
            self.logger.error(f"解决告警失败: {e}")
            return False
    
    def get_alarm(self, alarm_id: str) -> Optional[AlarmEvent]:
        """获取告警事件"""
        return self.alarms.get(alarm_id)
    
    def list_alarms(self, filter_params: Optional[AlarmFilter] = None) -> List[AlarmEvent]:
        """
        列出告警事件
        
        Parameters
        ----------
        filter_params : AlarmFilter, optional
            过滤条件
            
        Returns
        -------
        List[AlarmEvent]
            告警事件列表
        """
        alarms = list(self.alarms.values())
        
        if filter_params:
            alarms = self._filter_alarms(alarms, filter_params)
        
        return sorted(alarms, key=lambda x: x.timestamp, reverse=True)
    
    def _filter_alarms(self, alarms: List[AlarmEvent], filter_params: AlarmFilter) -> List[AlarmEvent]:
        """过滤告警事件"""
        filtered = []
        
        for alarm in alarms:
            # 严重程度过滤
            if filter_params.severity and alarm.severity.value != filter_params.severity:
                continue
            
            # 状态过滤
            if filter_params.status and alarm.status != filter_params.status:
                continue
            
            # 规则ID过滤
            if filter_params.rule_id and alarm.rule_id != filter_params.rule_id:
                continue
            
            # 运行ID过滤
            if filter_params.run_id and alarm.run_id != filter_params.run_id:
                continue
            
            # 时间范围过滤
            if filter_params.start_time and alarm.timestamp < filter_params.start_time:
                continue
            
            if filter_params.end_time and alarm.timestamp > filter_params.end_time:
                continue
            
            filtered.append(alarm)
        
        return filtered
    
    def get_alarm_statistics(self) -> Dict:
        """获取告警统计信息"""
        total = len(self.alarms)
        by_severity = {}
        by_status = {}
        
        for alarm in self.alarms.values():
            # 按严重程度统计
            severity = alarm.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1
            
            # 按状态统计
            status = alarm.status.value
            by_status[status] = by_status.get(status, 0) + 1
        
        return {
            'total': total,
            'by_severity': by_severity,
            'by_status': by_status
        } 