"""
tests/unit/test_record.py
------------------------------------
Record实体测试
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import dataclasses
from datetime import datetime, timezone

from backend.app.entities.Record import Record

# ---------- helpers -------------------------------------------------
RAW_SAMPLE = {
    "T1": -2.13,
    "U":  220.03,
    "P":  19.46,
    "Time_iso": "2025-06-20 08:49:25",   # local(?), will be coerced to UTC
    "Timestamp": 123456789,              # 将被丢弃
    "Time":       0                      # 将被丢弃
}

RUN_ID = "RUN_XYZ"
FILE_POS = 456


# ---------- tests ----------------------------------------------------

def test_record_creation():
    """测试Record创建"""
    ts = datetime.fromisoformat("2025-06-20 08:49:25").astimezone(timezone.utc)
    rec = Record(
        run_id=RUN_ID,
        ts=ts,
        metrics={"T1": -2.13, "U": 220.03, "P": 19.46},
        file_pos=FILE_POS
    )

    # ts 是否已变为 UTC aware datetime
    assert isinstance(rec.ts, datetime)
    assert rec.ts.tzinfo == timezone.utc

    # run_id / file_pos 是否写入
    assert rec.run_id == RUN_ID
    assert rec.file_pos == FILE_POS

    # metrics 里应包含 T1/U/P
    assert rec.metrics["T1"] == -2.13
    assert rec.metrics["U"] == 220.03
    assert rec.metrics["P"] == 19.46


def test_to_dict_roundtrip():
    """测试to_dict方法"""
    ts = datetime.fromisoformat("2025-06-20 08:49:25").astimezone(timezone.utc)
    rec = Record(
        run_id=RUN_ID,
        ts=ts,
        metrics={"T1": -2.13, "U": 220.03, "P": 19.46}
    )
    d = rec.to_dict()

    # 展平后应包含 run_id、ts(字符串)、以及全部 metrics 键
    assert d["run_id"] == RUN_ID
    assert isinstance(d["ts"], str)
    for k in ("T1", "U", "P"):
        assert d[k] == RAW_SAMPLE[k]


def test_frozen_immutable():
    """测试不可变性"""
    ts = datetime.fromisoformat("2025-06-20 08:49:25").astimezone(timezone.utc)
    rec = Record(
        run_id=RUN_ID,
        ts=ts,
        metrics={"T1": -2.13}
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.run_id = "NEW"


def test_get_helper():
    """测试get方法"""
    ts = datetime.fromisoformat("2025-06-20 08:49:25").astimezone(timezone.utc)
    rec = Record(
        run_id=RUN_ID,
        ts=ts,
        metrics={"T1": -2.13, "U": 220.03}
    )
    assert rec.get("T1") == -2.13
    assert rec.get("NON_EXIST", default=999) == 999


def test_record_without_file_pos():
    """测试不带file_pos的Record"""
    ts = datetime.fromisoformat("2025-06-20 08:49:25").astimezone(timezone.utc)
    rec = Record(
        run_id=RUN_ID,
        ts=ts,
        metrics={"T1": -2.13}
    )
    
    assert rec.file_pos is None
    d = rec.to_dict()
    assert "file_pos" not in d
