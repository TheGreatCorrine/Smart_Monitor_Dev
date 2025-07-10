"""
backend/app/usecases/Monitor.py
------------------------------------
监控用例 - 负责监控数据流和触发告警
"""
import sys
import os
import logging
from pathlib import Path
from typing import List, Callable, Optional
from datetime import datetime, timedelta

# 添加backend目录到Python路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from app.entities.Record import Record
from app.entities.Rule import Rule, AlarmEvent
from app.services.RuleEngineService import RuleEngine
from app.infra.datastore.DatParser import iter_new_records
from app.infra.config.RuleLoader import RuleLoader


class MonitorService:
    """
    监控服务
    
    协调数据解析、规则评估和告警处理
    遵循Clean Architecture的用例层职责
    """
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.rule_loader = RuleLoader()
        self.logger = logging.getLogger(__name__)
        self.alarm_handlers: List[Callable[[AlarmEvent], None]] = []
    
    def initialize(self, config_path: str = "config/rules.yaml"):
        """
        初始化监控服务
        
        Parameters
        ----------
        config_path : str
            规则配置文件路径
        """
        try:
            # 加载规则
            rules = self.rule_loader.load_rules()
            self.rule_engine.load_rules(rules)
            self.logger.info(f"监控服务初始化完成，加载了 {len(rules)} 条规则")
        except Exception as e:
            self.logger.error(f"初始化监控服务失败: {e}")
            raise
    
    def add_alarm_handler(self, handler: Callable[[AlarmEvent], None]):
        """
        添加告警处理器
        
        Parameters
        ----------
        handler : Callable[[AlarmEvent], None]
            告警处理函数
        """
        self.alarm_handlers.append(handler)
    
    def process_data_file(self, file_path: str, run_id: str) -> tuple[List[AlarmEvent], int]:
        """
        处理数据文件，返回所有告警事件和记录数
        
        Parameters
        ----------
        file_path : str
            数据文件路径
        run_id : str
            测试会话ID
            
        Returns
        -------
        tuple[List[AlarmEvent], int]
            告警事件列表和记录数
        """
        all_alarms = []
        
        try:
            # 解析数据文件
            records = list(iter_new_records(Path(file_path), run_id))
            self.logger.info(f"解析了 {len(records)} 条记录")
            
            # 逐条评估记录
            for record in records:
                alarms = self.rule_engine.evaluate_record(record, run_id)
                all_alarms.extend(alarms)
                
                # 触发告警处理器
                for alarm in alarms:
                    self._handle_alarm(alarm)
            
            self.logger.info(f"处理完成，生成了 {len(all_alarms)} 个告警事件")
            return all_alarms, len(records)
            
        except Exception as e:
            self.logger.error(f"处理数据文件失败: {e}")
            raise
    
    def process_record(self, record: Record, run_id: str) -> List[AlarmEvent]:
        """
        处理单条记录
        
        Parameters
        ----------
        record : Record
            传感器记录
        run_id : str
            测试会话ID
            
        Returns
        -------
        List[AlarmEvent]
            告警事件列表
        """
        try:
            alarms = self.rule_engine.evaluate_record(record, run_id)
            
            # 触发告警处理器
            for alarm in alarms:
                self._handle_alarm(alarm)
            
            return alarms
            
        except Exception as e:
            self.logger.error(f"处理记录失败: {e}")
            return []
    
    def get_rule_summary(self) -> dict:
        """
        获取规则摘要信息
        
        Returns
        -------
        dict
            规则摘要
        """
        return {
            'total_rules': len(self.rule_engine.rules),
            'enabled_rules': len([r for r in self.rule_engine.rules if r.enabled]),
            'rule_ids': [r.id for r in self.rule_engine.rules]
        }
    
    def _handle_alarm(self, alarm: AlarmEvent):
        """处理告警事件"""
        try:
            for handler in self.alarm_handlers:
                handler(alarm)
        except Exception as e:
            self.logger.error(f"处理告警事件失败: {e}")


# 默认告警处理器
def default_alarm_handler(alarm: AlarmEvent):
    """默认告警处理器"""
    print(f"[{alarm.severity.value.upper()}] {alarm.timestamp}: {alarm.description}")
    print(f"  传感器值: {alarm.sensor_values}")
    print(f"  规则ID: {alarm.rule_id}")
    print("-" * 50) 