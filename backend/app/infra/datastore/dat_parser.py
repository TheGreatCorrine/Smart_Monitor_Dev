#!/usr/bin/env python3
"""
Incremental SigmaData .dat parser → Record objects
作者: Xiang, Yining (GDE-CLBP)
版本: 2025-07-07
"""
import argparse, json, struct, datetime as dt
from pathlib import Path
from typing import Dict, List
from collections import namedtuple

from ...entities.record import Record
from .record_factory import RecordFactory

# ── 常量 & 解析布局（沿用你原稿） ─────────────────────────────────────────
BYTE_ORDER    = ">"
RECORD_BYTES  = 232
DAT_EPOCH     = dt.datetime(1899, 12, 30, 0, 0, 0)
OFFSET_DB     = Path(".offsets.json")

# ---- 布局表（与你原脚本一致，省略重复） -------------------------------
# ── 布局表 ───────────────────────────────────────────────────────────
RECORD_LAYOUT = [
    # 温度、模拟量
    ("T1",0,"f"),("T2",4,"f"),("T3",8,"f"),("T4",12,"f"),("T5",16,"f"),
    ("T6",20,"f"),("T7",24,"f"),("T8",28,"f"),("T9",32,"f"),("T10",36,"f"),
    ("T11",40,"f"),("V1",44,"f"),("V2",48,"f"),("U",52,"f"),("P",56,"f"),
    ("I",60,"f"),("X1",64,"f"),("AT",68,"f"),("AH",72,"f"),

    # 数字量（四个字节，后面拆位）
    ("DIG0",76,"B"),        # DI1..DO4
    ("DIG1",77,"B"),        # DO5..unused1
    # Digital Temperature
    ("TE1",78,"f"),("TE2",82,"f"),("TE3",86,"f"),("TE4",90,"f"),
    ("TE5",94,"f"),("TE6",98,"f"),("TE7",102,"f"),

    ("PH1",106,"f"),("PH2",110,"f"),("PH3",114,"f"),("PH4",118,"f"),

    # 第三段数字量（byte 122）
    ("DEB1",122,"B"),

    # Time started：秒数 (uint32, big-endian) since 1899-12-30
    ("Time",123,"I"),

    # TE8-14
    ("TE8",127,"f"),("TE9",131,"f"),("TE10",135,"f"),("TE11",139,"f"),
    ("TE12",143,"f"),("TE13",147,"f"),("TE14",151,"f"),

    # 第四段数字量（byte 155）
    ("DEB2",155,"B"),

    # 额外温度
    ("T12",156,"f"),("T13",160,"f"),("T14",164,"f"),("T15",168,"f"),
    ("T16",172,"f"),("T17",176,"f"),("T18",180,"f"),("T19",184,"f"),
    ("T20",188,"f"),("T21",192,"f"),("T22",196,"f"),

    # 能耗、频率、FILETIME-64
    ("Energy",200,"d"),("Frequency",208,"f"),
    ("Res1",212,"f"),("Res2",216,"f"),("Res3",220,"f"),
    ("Timestamp",224,"Q"),
]
Field  = namedtuple("Field","name offset fmt")
FIELDS : List[Field] = [Field(n,o,BYTE_ORDER+f) for n,o,f in RECORD_LAYOUT]
RECORD_SIZE = RECORD_BYTES

# ── 数字量位映射 ────────────────────────────────────────────────────
DIGITAL_MAP = {
    76: ["DI1","DI2","DI3","DI4","DO1","DO2","DO3","DO4"],
    77: ["DO5","DO6","DO7","DO8","DO9","DO10","DO11","unused1"],
    122:["DE1","DE2","DE3","DE4","DE5","DE6","DE7","DE8"],
    155:["DE9","DE10","DE11","DE12","DE13","DE14","DE15","unused2"],
}
DIGITAL_NAMES = sum(DIGITAL_MAP.values(), [])

# === 简易偏移持久化 ================================================
def _load_offsets() -> Dict[str, int]:
    if OFFSET_DB.exists():
        return json.loads(OFFSET_DB.read_text())
    return {}

def _save_offsets(tbl: Dict[str, int]):
    OFFSET_DB.write_text(json.dumps(tbl))

def get_offset(path: Path) -> int:
    return _load_offsets().get(str(path), 0)

def save_offset(path: Path, pos: int):
    tbl = _load_offsets()
    tbl[str(path)] = pos
    _save_offsets(tbl)

# === 解析单条记录 → dict  ==========================================
def _parse_record(buf: bytes) -> Dict[str, float]:
    rec: Dict[str, float] = {}
    for f in FIELDS:
        if f.name in ("DIG0", "DIG1", "DEB1", "DEB2"):
            continue
        rec[f.name] = struct.unpack_from(f.fmt, buf, f.offset)[0]

    for off, names in DIGITAL_MAP.items():
        val = struct.unpack_from(">B", buf, off)[0]
        for bit, name in enumerate(names):
            rec[name] = (val >> bit) & 1

    secs = rec["Time"]
    rec["Time_iso"] = (DAT_EPOCH + dt.timedelta(seconds=secs)).isoformat(sep=" ")
    return rec

# === 增量迭代器 → Record ===========================================
def iter_new_records(path: Path, run_id: str):
    start = get_offset(path)
    with path.open("rb") as fd:
        fd.seek(start)
        pos = start
        while chunk := fd.read(RECORD_BYTES):
            if len(chunk) == RECORD_BYTES:
                rdict = _parse_record(chunk)
                yield RecordFactory.from_dict(rdict, run_id=run_id, file_pos=pos)
                pos += RECORD_BYTES
        # 解析完毕，保存最新偏移
        save_offset(path, pos)

# === CLI ===========================================================
def main():
    pa = argparse.ArgumentParser(description="Incremental .dat parser demo")
    pa.add_argument("-f", "--file", required=True)
    pa.add_argument("-r", "--run-id", help="custom run_id (default: file stem)")
    pa.add_argument("-n", "--rows", type=int, default=5,
                    help="preview last N new records")
    args = pa.parse_args()

    path = Path(args.file)
    run_id = args.run_id or path.stem

    new_records: List[Record] = list(iter_new_records(path, run_id))
    if not new_records:
        print("No new data.")
        return

    # 只预览最后 N 行
    for rec in new_records[-args.rows:]:
        d = rec.to_dict()
        print(f"[{d['ts']}] T1={d.get('T1'):.2f}  U={d.get('U'):.2f}  "
              f"P={d.get('P'):.2f}  run={rec.run_id}")

if __name__ == "__main__":
    main()
