"""
backend/app/controllers/DataController.py
------------------------------------
数据控制器 - 处理数据相关的用户请求
负责数据解析、查询、统计等功能
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
from pathlib import Path
import logging

from ..entities.Record import Record
from ..infra.datastore.DatParser import iter_new_records


class DataController:
    """
    数据控制器
    
    职责：
    1. 处理数据文件解析请求
    2. 处理数据查询请求
    3. 提供数据统计功能
    4. 格式化数据输出
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_data_file(self, file_path: str, run_id: str, 
                       start_record: Optional[int] = None,
                       end_record: Optional[int] = None) -> Dict[str, Any]:
        """
        解析数据文件
        
        Parameters
        ----------
        file_path : str
            数据文件路径
        run_id : str
            运行ID
        start_record : int, optional
            开始记录索引
        end_record : int, optional
            结束记录索引
            
        Returns
        -------
        Dict[str, Any]
            解析结果
        """
        try:
            # 验证文件路径
            if not self._validate_file_path(file_path):
                return {
                    'success': False,
                    'error': f"文件不存在或格式错误: {file_path}"
                }
            
            # 解析数据
            records = list(iter_new_records(Path(file_path), run_id))
            
            # 应用范围过滤
            if start_record is not None or end_record is not None:
                start = start_record or 0
                end = end_record or len(records)
                records = records[start:end]
            
            # 格式化结果
            return {
                'success': True,
                'data': {
                    'file_path': file_path,
                    'run_id': run_id,
                    'total_records': len(records),
                    'records': [self._format_record(record) for record in records]
                }
            }
            
        except Exception as e:
            self.logger.error(f"解析数据文件失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        获取文件信息
        
        Parameters
        ----------
        file_path : str
            文件路径
            
        Returns
        -------
        Dict[str, Any]
            文件信息
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return {
                    'success': False,
                    'error': f"文件不存在: {file_path}"
                }
            
            # 获取文件信息
            stat = path.stat()
            
            return {
                'success': True,
                'data': {
                    'file_path': str(path),
                    'file_name': path.name,
                    'file_size': stat.st_size,
                    'file_size_mb': round(stat.st_size / (1024 * 1024), 2),
                    'modified_time': stat.st_mtime,
                    'is_dat_file': path.suffix.lower() == '.dat'
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取文件信息失败: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_data_statistics(self, file_path: str, run_id: str) -> Dict[str, Any]:
        """
        获取数据统计信息
        
        Parameters
        ----------
        file_path : str
            数据文件路径
        run_id : str
            运行ID
            
        Returns
        -------
        Dict[str, Any]
            统计信息
        """
        try:
            # 解析数据
            records = list(iter_new_records(Path(file_path), run_id))
            
            if not records:
                return {
                    'success': True,
                    'data': {
                        'total_records': 0,
                        'time_range': None,
                        'sensors': {},
                        'statistics': {}
                    }
                }
            
            # 计算统计信息
            time_range = (records[0].ts, records[-1].ts)
            sensors = self._analyze_sensors(records)
            
            return {
                'success': True,
                'data': {
                    'total_records': len(records),
                    'time_range': {
                        'start': time_range[0].isoformat(),
                        'end': time_range[1].isoformat(),
                        'duration_minutes': (time_range[1] - time_range[0]).total_seconds() / 60
                    },
                    'sensors': sensors,
                    'statistics': {
                        'avg_records_per_minute': len(records) / max(1, (time_range[1] - time_range[0]).total_seconds() / 60)
                    }
                }
            }
            
        except Exception as e:
            self.logger.error(f"获取数据统计失败: {e}")
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
    
    def _format_record(self, record: Record) -> Dict[str, Any]:
        """格式化记录"""
        return {
            'run_id': record.run_id,
            'timestamp': record.ts.isoformat(),
            'metrics': record.metrics,
            'file_pos': record.file_pos
        }
    
    def _analyze_sensors(self, records: List[Record]) -> Dict[str, Any]:
        """分析传感器数据"""
        if not records:
            return {}
        
        sensors = {}
        
        # 获取所有传感器
        all_sensors = set()
        for record in records:
            all_sensors.update(record.metrics.keys())
        
        # 分析每个传感器
        for sensor in all_sensors:
            values = [record.metrics.get(sensor) for record in records if sensor in record.metrics]
            if values:
                sensors[sensor] = {
                    'count': len(values),
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values)
                }
        
        return sensors 