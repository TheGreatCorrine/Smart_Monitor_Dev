from ...entities.record import Record
from datetime import datetime, timezone

class RecordFactory:
    @staticmethod
    def from_dict(d: dict, run_id: str, file_pos: int = None) -> Record:
        # 时间戳解析
        try:
            ts = datetime.fromisoformat(str(d.pop("Time_iso"))).astimezone(timezone.utc)
        except KeyError:
            raise ValueError("Expecting key 'Time_iso' in parsed dict")
        # 清理无关字段
        d.pop("Timestamp", None)
        d.pop("Time", None)
        d.pop("run_id", None)
        return Record(run_id=run_id, ts=ts, metrics=d, file_pos=file_pos) 