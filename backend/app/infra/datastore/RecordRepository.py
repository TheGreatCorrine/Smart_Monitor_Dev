"""
backend/app/infra/datastore/RecordRepository.py
------------------------------------
记录仓储 - 负责Record对象的创建和转换
"""
from ...entities.record import Record
from datetime import datetime, timezone

class RecordFactory:
    @staticmethod
    def from_dict(d: dict, run_id: str, file_pos: int = None) -> Record:
        # 时间戳解析
        try:
            time_iso = d["Time_iso"]  # 不删除，只是获取值
            ts = datetime.fromisoformat(str(time_iso)).astimezone(timezone.utc)
        except KeyError:
            raise ValueError("Expecting key 'Time_iso' in parsed dict")
        
        # 保留时间戳字段在metrics中，不删除
        # d.pop("Timestamp", None)  # 删除这行
        # d.pop("Time", None)       # 删除这行
        d.pop("run_id", None)
        
        return Record(run_id=run_id, ts=ts, metrics=d, file_pos=file_pos) 