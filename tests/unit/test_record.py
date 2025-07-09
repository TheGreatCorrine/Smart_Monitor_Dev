# tests/test_record.py
from datetime import datetime, timezone
import pytest
import dataclasses

from backend.app.entities.record import Record

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

def test_from_dict_basic():
    rec = Record.from_dict(RAW_SAMPLE.copy(), run_id=RUN_ID, file_pos=FILE_POS)

    # ts 是否已变为 UTC aware datetime
    assert isinstance(rec.ts, datetime)
    assert rec.ts.tzinfo == timezone.utc

    # run_id / file_pos 是否写入
    assert rec.run_id == RUN_ID
    assert rec.file_pos == FILE_POS

    # metrics 里应包含 T1/U/P，且不包含 Time/Timestamp
    assert rec.metrics["T1"] == -2.13
    assert "Timestamp" not in rec.metrics
    assert "Time" not in rec.metrics

def test_to_dict_roundtrip():
    rec = Record.from_dict(RAW_SAMPLE.copy(), run_id=RUN_ID)
    d = rec.to_dict()

    # 展平后应包含 run_id、ts(字符串)、以及全部 metrics 键
    assert d["run_id"] == RUN_ID
    assert isinstance(d["ts"], str)
    for k in ("T1", "U", "P"):
        assert d[k] == RAW_SAMPLE[k]

def test_missing_time_iso_raises():
    bad = {"T1": 1.0}
    with pytest.raises(ValueError):
        Record.from_dict(bad, run_id="ANY")

def test_frozen_immutable():
    rec = Record.from_dict(RAW_SAMPLE.copy(), run_id=RUN_ID)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rec.run_id = "NEW"

def test_get_helper():
    rec = Record.from_dict(RAW_SAMPLE.copy(), run_id=RUN_ID)
    assert rec.get("T1") == -2.13
    assert rec.get("NON_EXIST", default=999) == 999
