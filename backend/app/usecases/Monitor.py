"""
backend/app/usecases/Monitor.py
------------------------------------
监控用例 - 负责监控数据流和触发告警
"""
import sys
import os
import logging
import threading
from pathlib import Path
from typing import List, Callable, Optional, Dict, Any
from datetime import datetime, timedelta

# 添加backend目录到Python路径
backend_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_path))

from backend.app.entities.record import Record
from backend.app.entities.rule import Rule
from backend.app.entities.AlarmEvent import AlarmEvent
from backend.app.services.RuleEngineService import RuleEngine
from backend.app.infra.datastore.DatParser import iter_new_records
from backend.app.infra.config.RuleLoader import RuleLoader
from backend.app.infra.fileprovider import FileProvider


class MonitorService:
    """
    监控服务
    
    协调数据解析、规则评估和告警处理
    支持FileProvider的持续监控功能
    """
    
    def __init__(self):
        self.rule_engine = RuleEngine()
        self.rule_loader = RuleLoader()
        self.logger = logging.getLogger(__name__)
        self.alarm_handlers: List[Callable[[AlarmEvent], None]] = []
        
        # FileProvider相关
        self.file_provider: Optional[FileProvider] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.stop_monitoring_event = threading.Event()
        self.is_monitoring = False
        
        # 监控状态
        self.monitoring_stats = {
            'total_records_processed': 0,
            'total_alarms_generated': 0,
            'last_processed_time': None,
            'current_file_path': None
        }
    
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
    
    def set_file_provider(self, file_provider: FileProvider):
        """
        设置文件提供者
        
        Parameters
        ----------
        file_provider : FileProvider
            文件提供者实例
        """
        self.file_provider = file_provider
        # 设置文件更新回调
        file_provider.set_callback(self._on_file_update)
        self.logger.info("文件提供者已设置")
    
    def start_continuous_monitoring(self, run_id: str) -> bool:
        """
        开始持续监控
        
        Parameters
        ----------
        run_id : str
            测试会话ID
            
        Returns
        -------
        bool
            是否成功启动监控
        """
        if self.is_monitoring:
            self.logger.warning("监控已在运行中")
            return True
        
        if not self.file_provider:
            self.logger.error("未设置文件提供者")
            return False
        
        # 启动文件提供者
        if not self.file_provider.start():
            self.logger.error("启动文件提供者失败")
            return False
        
        # 启动监控线程
        self.stop_monitoring_event.clear()
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            args=(run_id,),
            daemon=True
        )
        self.monitoring_thread.start()
        
        self.is_monitoring = True
        self.logger.info(f"持续监控已启动，运行ID: {run_id}")
        
        return True
    
    def stop_continuous_monitoring(self) -> bool:
        """
        停止持续监控
        
        Returns
        -------
        bool
            是否成功停止监控
        """
        if not self.is_monitoring:
            return True
        
        # 停止监控线程
        self.stop_monitoring_event.set()
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        # 停止文件提供者
        if self.file_provider:
            self.file_provider.stop()
        
        self.is_monitoring = False
        self.logger.info("持续监控已停止")
        
        return True
    
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
            
            # 打印每条记录的详细信息
            for i, record in enumerate(records):
                record_dict = record.to_dict()
                self.logger.info(f"记录 {i+1}: T1={record_dict.get('T1', 'N/A')}, U={record_dict.get('U', 'N/A')}, P={record_dict.get('P', 'N/A')}, 时间={record_dict.get('ts', 'N/A')}")
            
            # 逐条评估记录
            for record in records:
                alarms = self.rule_engine.evaluate_record(record, run_id)
                all_alarms.extend(alarms)
                
                # 触发告警处理器
                for alarm in alarms:
                    self._handle_alarm(alarm)
            
            # 只在有记录或告警时才输出日志
            if len(records) > 0 or len(all_alarms) > 0:
                self.logger.info(f"处理了 {len(records)} 条记录，生成了 {len(all_alarms)} 个告警事件")
            
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
    
    def get_monitoring_status(self) -> dict:
        """
        获取监控状态信息
        
        Returns
        -------
        dict
            监控状态
        """
        status = {
            'is_monitoring': self.is_monitoring,
            'stats': self.monitoring_stats.copy()
        }
        
        if self.file_provider:
            status['file_provider'] = self.file_provider.get_status()
            
            # 添加持续时间信息
            if hasattr(self.file_provider, '_start_time') and self.file_provider._start_time:
                duration = (datetime.now() - self.file_provider._start_time).total_seconds()
                status['file_provider']['simulation_duration'] = duration
        
        return status
    
    def _on_file_update(self, file_path: Path):
        """
        文件更新回调处理
        
        Parameters
        ----------
        file_path : Path
            更新的文件路径
        """
        try:
            self.logger.info(f"检测到文件更新: {file_path}")
            
            # 更新监控状态
            self.monitoring_stats['current_file_path'] = str(file_path)
            self.monitoring_stats['last_processed_time'] = datetime.now()
            
            # 处理文件中的新记录
            # 注意：这里需要实现增量处理逻辑
            # 暂时使用完整处理方式
            if self.monitoring_stats.get('run_id'):
                alarms, record_count = self.process_data_file(str(file_path), self.monitoring_stats['run_id'])
                if record_count > 0:  # 只在有实际处理记录时才更新统计
                    self.monitoring_stats['total_records_processed'] += record_count
                    self.monitoring_stats['total_alarms_generated'] += len(alarms)
                    
                    # 更新处理时间统计
                    if self.file_provider and hasattr(self.file_provider, '_start_time') and self.file_provider._start_time:
                        duration = (datetime.now() - self.file_provider._start_time).total_seconds()
                        self.monitoring_stats['total_duration'] = duration
                
        except Exception as e:
            self.logger.error(f"处理文件更新失败: {e}")
    
    def _monitoring_worker(self, run_id: str):
        """
        监控工作线程
        
        Parameters
        ----------
        run_id : str
            测试会话ID
        """
        self.monitoring_stats['run_id'] = run_id
        
        while not self.stop_monitoring_event.is_set():
            try:
                # 检查文件提供者状态
                if self.file_provider and self.file_provider.is_file_available():
                    file_path = self.file_provider.get_file_path()
                    if file_path:
                        # 处理文件
                        alarms, record_count = self.process_data_file(str(file_path), run_id)
                        if record_count > 0:  # 只在有实际处理记录时才更新统计
                            self.monitoring_stats['total_records_processed'] += record_count
                            self.monitoring_stats['total_alarms_generated'] += len(alarms)
                
                # 等待一段时间再检查
                self.stop_monitoring_event.wait(5)  # 每5秒检查一次
                
            except Exception as e:
                self.logger.error(f"监控工作线程出错: {e}")
                self.stop_monitoring_event.wait(10)  # 出错后等待更长时间
    
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