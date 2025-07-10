#!/usr/bin/env python3
"""
tests/integration/test_parse_dat.py
------------------------------------
测试 dat_parser.py 的功能
使用 MPL6.dat 文件并结构化打印结果
"""
import sys
from pathlib import Path

# 添加backend目录到Python路径，方便IDE直接运行
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

import json
from datetime import datetime

from app.infra.datastore.DatParser import iter_new_records


def test_parse_mpl6_dat():
    """测试解析 MPL6.dat 文件"""
    dat_file = Path("MPL6.dat")
    
    if not dat_file.exists():
        print(f"❌ 错误: 找不到文件 {dat_file}")
        return
    
    print(f"🔍 开始解析文件: {dat_file}")
    print(f"📊 文件大小: {dat_file.stat().st_size:,} bytes")
    print("-" * 60)
    
    # 解析记录
    records = []
    try:
        for record in iter_new_records(dat_file, run_id="TEST_MPL6"):
            records.append(record)
            
            # 只显示前5条记录用于预览
            if len(records) <= 5:
                print(f"📝 记录 #{len(records)}:")
                print(f"   Run ID: {record.run_id}")
                print(f"   时间戳: {record.ts}")
                print(f"   文件位置: {record.file_pos:,} bytes")
                print(f"   通道数量: {len(record.metrics)}")
                
                # 显示前10个通道的值
                print("   通道数据:")
                for i, (channel, value) in enumerate(record.metrics.items()):
                    if i >= 10:  # 只显示前10个
                        print(f"     ... 还有 {len(record.metrics) - 10} 个通道")
                        break
                    print(f"     {channel}: {value}")
                print()
        
        print("-" * 60)
        print(f"✅ 解析完成!")
        print(f"📈 总记录数: {len(records)}")
        
        if records:
            # 显示统计信息
            first_record = records[0]
            last_record = records[-1]
            
            print(f"⏰ 时间范围:")
            print(f"   开始: {first_record.ts}")
            print(f"   结束: {last_record.ts}")
            
            # 计算时间间隔
            time_diff = last_record.ts - first_record.ts
            print(f"   总时长: {time_diff}")
            
            # 显示所有可用的通道
            print(f"🔧 可用通道 ({len(first_record.metrics)} 个):")
            channels = sorted(first_record.metrics.keys())
            for i, channel in enumerate(channels):
                if i % 8 == 0:  # 每行8个
                    print("   ", end="")
                print(f"{channel:>8}", end="")
                if (i + 1) % 8 == 0 or i == len(channels) - 1:
                    print()
            
            # 显示一些数值统计
            print(f"📊 数值统计 (第一条记录):")
            numeric_channels = [k for k, v in first_record.metrics.items() 
                              if isinstance(v, (int, float)) and not isinstance(v, bool)]
            if numeric_channels:
                print(f"   数值通道: {len(numeric_channels)} 个")
                for channel in numeric_channels[:5]:  # 显示前5个
                    value = first_record.metrics[channel]
                    print(f"   {channel}: {value}")
                if len(numeric_channels) > 5:
                    print(f"   ... 还有 {len(numeric_channels) - 5} 个数值通道")
            
            # 显示布尔通道
            bool_channels = [k for k, v in first_record.metrics.items() 
                           if isinstance(v, bool)]
            if bool_channels:
                print(f"   布尔通道: {len(bool_channels)} 个")
                for channel in bool_channels[:5]:  # 显示前5个
                    value = first_record.metrics[channel]
                    print(f"   {channel}: {value}")
                if len(bool_channels) > 5:
                    print(f"   ... 还有 {len(bool_channels) - 5} 个布尔通道")
        
    except Exception as e:
        print(f"❌ 解析错误: {e}")
        import traceback
        traceback.print_exc()


def test_record_structure():
    """测试Record结构"""
    print("\n" + "=" * 60)
    print("🔬 测试Record结构")
    print("=" * 60)
    
    dat_file = Path("MPL6.dat")
    if not dat_file.exists():
        print(f"❌ 错误: 找不到文件 {dat_file}")
        return
    
    # 获取第一条记录
    for record in iter_new_records(dat_file, run_id="STRUCTURE_TEST"):
        print(f"📋 Record 结构分析:")
        print(f"   类型: {type(record)}")
        print(f"   属性: {list(record.__dataclass_fields__.keys())}")
        print(f"   是否不可变: {hasattr(record, '__hash__')}")
        print(f"   是否使用slots: {hasattr(record, '__slots__')}")
        
        # 测试to_dict方法
        record_dict = record.to_dict()
        print(f"   to_dict() 键: {list(record_dict.keys())[:10]}...")
        
        # 测试get方法
        if record.metrics:
            first_key = list(record.metrics.keys())[0]
            value = record.get(first_key)
            print(f"   get('{first_key}'): {value}")
        
        break  # 只测试第一条记录


if __name__ == "__main__":
    print("🚀 开始测试 dat_parser.py")
    print("=" * 60)
    
    test_parse_mpl6_dat()
    test_record_structure()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成!") 