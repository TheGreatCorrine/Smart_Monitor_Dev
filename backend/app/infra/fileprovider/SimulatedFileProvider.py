"""
backend/app/infra/fileprovider/SimulatedFileProvider.py
------------------------------------
模拟文件提供者 - 模拟真实文件推送过程
"""
import threading
import time
from pathlib import Path
from typing import Optional, Callable, Any
import logging
from datetime import datetime

from .FileProvider import FileProvider


class SimulatedFileProvider(FileProvider):
    """
    模拟文件提供者
    
    模拟真实文件推送过程：
    1. 从原始mplX.dat文件读取数据
    2. 每10秒截取一个record写入temp文件
    3. 模拟文件被推送过来的效果
    """
    
    def __init__(self, source_file: str, workstation_id: str = "1"):
        """
        初始化模拟文件提供者
        
        Parameters
        ----------
        source_file : str
            原始mplX.dat文件路径
        workstation_id : str
            工作站ID，用于生成temp文件名
        """
        super().__init__()
        self.source_file = Path(source_file)
        self.workstation_id = workstation_id
        self.temp_file = self._get_temp_file_path()
        
        # 模拟控制
        self._simulation_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_record_index = 0
        self._record_size = 232  # 每个record大小为232字节（与DatParser一致）
        
        # 状态信息
        self._total_records = 0
        self._start_time: Optional[datetime] = None
        self._last_update_time: Optional[datetime] = None
    
    def _get_temp_file_path(self) -> Path:
        """生成temp文件路径"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return data_dir / f"mpl{self.workstation_id}_temp.dat"
    
    def get_file_path(self) -> Optional[Path]:
        """获取当前可用的文件路径"""
        if self.temp_file.exists() and self.temp_file.stat().st_size > 0:
            return self.temp_file
        return None
    
    def is_file_available(self) -> bool:
        """检查文件是否可用"""
        return self.get_file_path() is not None
    
    def start(self) -> bool:
        """启动模拟文件提供者"""
        if self._is_active:
            self.logger.warning("模拟文件提供者已经在运行")
            return True
        
        if not self.source_file.exists():
            self.logger.error(f"源文件不存在: {self.source_file}")
            return False
        
        # 初始化temp文件
        self._initialize_temp_file()
        
        # 启动模拟线程
        self._stop_event.clear()
        self._simulation_thread = threading.Thread(
            target=self._simulation_worker,
            daemon=True
        )
        self._simulation_thread.start()
        
        self._is_active = True
        self._start_time = datetime.now()
        self.logger.info(f"模拟文件提供者已启动，工作站ID: {self.workstation_id}")
        
        return True
    
    def stop(self) -> bool:
        """停止模拟文件提供者"""
        if not self._is_active:
            return True
        
        self._stop_event.set()
        if self._simulation_thread:
            self._simulation_thread.join(timeout=5)
        
        self._is_active = False
        self.logger.info("模拟文件提供者已停止")
        
        return True
    
    def _initialize_temp_file(self) -> None:
        """初始化temp文件"""
        try:
            # 清空temp文件
            self.temp_file.write_bytes(b'')
            self._current_record_index = 0
            self._total_records = 0
            self.logger.info(f"初始化temp文件: {self.temp_file}")
        except Exception as e:
            self.logger.error(f"初始化temp文件失败: {e}")
            raise
    
    def _simulation_worker(self) -> None:
        """模拟工作线程"""
        self.logger.info("开始模拟文件推送...")
        
        while not self._stop_event.is_set():
            try:
                # 从源文件读取下一个record
                if self._read_and_append_record():
                    self._last_update_time = datetime.now()
                    self._total_records += 1
                    
                    # 通知文件更新
                    self._notify_file_update(self.temp_file)
                    
                    self.logger.info(f"已推送第 {self._total_records} 个record")
                else:
                    # 所有records都已推送完毕
                    self.logger.info("所有records已推送完毕")
                    break
                
                # 等待10秒
                self._stop_event.wait(10)
                
            except Exception as e:
                self.logger.error(f"模拟推送过程中出错: {e}")
                break
        
        self.logger.info("模拟推送线程结束")
    
    def _read_and_append_record(self) -> bool:
        """
        从源文件读取一个record并追加到temp文件
        
        Returns
        -------
        bool
            是否成功读取并追加record
        """
        try:
            with open(self.source_file, 'rb') as source:
                # 计算当前record的位置
                record_start = self._current_record_index * self._record_size
                source.seek(record_start)
                
                # 读取一个record
                record_data = source.read(self._record_size)
                
                if not record_data:
                    self.logger.info(f"SimulatedFileProvider: 源文件已读完，当前index={self._current_record_index}")
                    return False  # 没有更多数据
                
                # 追加到temp文件
                with open(self.temp_file, 'ab') as temp:
                    temp.write(record_data)
                
                self.logger.info(f"SimulatedFileProvider: 推送record {self._current_record_index + 1}, 大小={len(record_data)}字节, temp文件大小={self.temp_file.stat().st_size}字节")
                self._current_record_index += 1
                return True
                
        except Exception as e:
            self.logger.error(f"读取record失败: {e}")
            return False
    
    def get_status(self) -> dict:
        """获取详细状态信息"""
        base_status = super().get_status()
        base_status.update({
            'workstation_id': self.workstation_id,
            'source_file': str(self.source_file),
            'temp_file': str(self.temp_file),
            'current_record_index': self._current_record_index,
            'total_records_pushed': self._total_records,
            'start_time': self._start_time.isoformat() if self._start_time else None,
            'last_update_time': self._last_update_time.isoformat() if self._last_update_time else None,
            'simulation_duration': self._get_duration_seconds()
        })
        return base_status
    
    def _get_duration_seconds(self) -> Optional[float]:
        """获取模拟持续时间（秒）"""
        if self._start_time:
            return (datetime.now() - self._start_time).total_seconds()
        return None
    
    def reset_simulation(self) -> bool:
        """重置模拟状态"""
        if self._is_active:
            self.logger.warning("无法在运行状态下重置模拟")
            return False
        
        try:
            self._initialize_temp_file()
            self._start_time = None
            self._last_update_time = None
            self.logger.info("模拟状态已重置")
            return True
        except Exception as e:
            self.logger.error(f"重置模拟状态失败: {e}")
            return False 