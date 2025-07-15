"""
backend/app/entities/Record.py
--------------------------------
纯领域实体：不依赖任何框架，只描述"冰箱测试采样点"数据本身
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Union, Optional


@dataclass(slots=True, frozen=True)
class Record:
    """
    一条采样记录（原始点或 1-min 聚合点）

    Attributes
    ----------
    run_id   : str        # 本次试验唯一 ID（上层生成并注入）
    ts       : datetime   # 采样时间；统一使用 **UTC aware** datetime
    metrics  : dict       # 所有模拟 / 数字量键值
    file_pos : Optional[int] # （可选）该记录在源 .dat 中的字节偏移
    """
    run_id: str
    ts: datetime
    metrics: Dict[str, Union[float, int]] = field(default_factory=dict)
    file_pos: Optional[int] = None      # 方便做增量解析；不用可删

    # ---------- 序列化 ------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        便于写 JSON / CSV / 返回 API。
        - ts 转成 ISO-8601 字符串
        - metrics 展平到顶层（可选：也可保留嵌套）
        """
        base = {
            "run_id": self.run_id,
            "ts": self.ts.isoformat(),
            **self.metrics,
        }
        if self.file_pos is not None:
            base["file_pos"] = self.file_pos
        return base

    # ---------- 便捷查询 ----------------------------------------------------

    def get(self, key: str, default: Optional[Union[float, int]] = None):
        """快捷访问某通道值；等价 metrics.get()"""
        return self.metrics.get(key, default)
