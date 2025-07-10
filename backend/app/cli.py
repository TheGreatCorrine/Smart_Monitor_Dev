#!/usr/bin/env python3
"""
backend/app/cli.py
------------------------------------
命令行界面 - 智能监测系统入口
"""
import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from .usecases.Monitor import MonitorService, default_alarm_handler


def setup_logging(verbose: bool = False):
    """设置日志"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def custom_alarm_handler(alarm):
    """自定义告警处理器 - 美化输出"""
    severity_icons = {
        "low": "🔵",
        "medium": "🟡", 
        "high": "🟠",
        "critical": "🔴"
    }
    
    icon = severity_icons.get(alarm.severity.value, "⚪")
    
    print(f"\n{icon} [{alarm.severity.value.upper()}] {alarm.timestamp}")
    print(f"   规则: {alarm.rule_name}")
    print(f"   描述: {alarm.description}")
    print(f"   传感器值: {alarm.sensor_values}")
    print(f"   规则ID: {alarm.rule_id}")
    print("-" * 60)


def print_header(file_path: Path):
    """打印文件处理头部信息"""
    print("🔍 冰箱测试异常状态智能监测系统")
    print("=" * 60)
    print(f"📁 处理文件: {file_path}")
    print(f"📊 文件大小: {file_path.stat().st_size:,} bytes")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)


def print_summary(records_count: int, alarms_count: int, processing_time: float):
    """打印处理摘要"""
    print("\n" + "=" * 60)
    print("📊 处理摘要")
    print("=" * 60)
    print(f"📈 总记录数: {records_count:,}")
    print(f"🚨 告警事件: {alarms_count}")
    print(f"⏱️  处理时间: {processing_time:.2f} 秒")
    print(f"📊 处理速度: {records_count/processing_time:.0f} 记录/秒")
    
    if alarms_count > 0:
        print(f"⚠️  告警率: {alarms_count/records_count*100:.2f}%")
    else:
        print("✅ 无异常告警")
    
    print("=" * 60)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="冰箱测试异常状态智能监测系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python -m backend.app.cli MPL6.dat
  python -m backend.app.cli data/test.dat --config config/rules.yaml
  python -m backend.app.cli MPL6.dat --verbose
        """
    )
    
    parser.add_argument(
        "dat_file",
        type=str,
        help="要处理的 .dat 文件路径"
    )
    
    parser.add_argument(
        "--config", "-c",
        type=str,
        default="config/rules.yaml",
        help="规则配置文件路径 (默认: config/rules.yaml)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细输出模式"
    )
    
    parser.add_argument(
        "--run-id",
        type=str,
        help="自定义测试会话ID (默认使用文件名)"
    )
    
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 检查文件
    dat_path = Path(args.dat_file)
    if not dat_path.exists():
        print(f"❌ 错误: 文件不存在 - {dat_path}")
        sys.exit(1)
    
    if not dat_path.suffix.lower() == '.dat':
        print(f"❌ 错误: 不是 .dat 文件 - {dat_path}")
        sys.exit(1)
    
    # 检查配置文件
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"❌ 错误: 配置文件不存在 - {config_path}")
        sys.exit(1)
    
    # 生成运行ID
    run_id = args.run_id or f"RUN_{dat_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # 打印头部信息
        print_header(dat_path)
        
        # 创建监控服务
        monitor_service = MonitorService()
        monitor_service.add_alarm_handler(custom_alarm_handler)
        
        # 初始化服务
        logger.info("初始化监控服务...")
        monitor_service.rule_loader.config_path = config_path
        monitor_service.initialize()
        
        # 显示规则信息
        summary = monitor_service.get_rule_summary()
        print(f"✅ 加载了 {summary['enabled_rules']} 条规则")
        print(f"   规则ID: {', '.join(summary['rule_ids'])}")
        print("-" * 60)
        
        # 处理数据文件
        logger.info("开始处理数据文件...")
        start_time = datetime.now()
        
        alarms, records_count = monitor_service.process_data_file(str(dat_path), run_id)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 打印摘要
        print_summary(records_count, len(alarms), processing_time)
        
        logger.info("处理完成")
        
    except KeyboardInterrupt:
        print("\n⚠️  用户中断处理")
        sys.exit(1)
    except Exception as e:
        logger.error(f"处理失败: {e}")
        print(f"❌ 错误: {e}")
        sys.exit(1)


def interactive_demo():
    """交互式demo：让用户选择data/下的文件，处理前30条记录并输出告警"""
    import os
    from pathlib import Path
    from app.usecases.Monitor import MonitorService, default_alarm_handler
    
    # 修改为查找项目根目录下的data目录
    data_dir = Path(__file__).parent.parent.parent / "data"
    if not data_dir.exists():
        print(f"❌ data目录不存在: {data_dir}")
        return
    dat_files = [f for f in os.listdir(data_dir) if f.endswith('.dat')]
    if not dat_files:
        print("❌ data目录下没有.dat文件")
        return
    
    print("🔍 冰箱测试异常状态智能监测系统 - 交互式Demo")
    print("=" * 60)
    print("可用的.dat文件：")
    for idx, fname in enumerate(dat_files):
        print(f"  [{idx+1}] {fname}")
    
    # 选择文件
    while True:
        choice = input("\n请输入要处理的文件名（或序号）：").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(dat_files):
            file_name = dat_files[int(choice)-1]
            break
        elif choice in dat_files:
            file_name = choice
            break
        else:
            print("输入无效，请重新输入。")
    
    file_path = data_dir / file_name
    print(f"\n✅ 选择文件: {file_path}")
    
    # 询问是否打印每条record
    print_record = input("\n是否需要打印每条record的详细信息？(y/n): ").strip().lower() == 'y'
    print_count = 30
    if print_record:
        try:
            count_input = input("打印前几条record？(默认30): ").strip()
            if count_input:
                print_count = int(count_input)
        except ValueError:
            print("输入无效，使用默认值30")
    
    print(f"\n开始处理，{'将打印前' + str(print_count) + '条record' if print_record else '不打印record详情'}")
    print("-" * 60)
    
    # 初始化服务
    monitor_service = MonitorService()
    monitor_service.add_alarm_handler(custom_alarm_handler)
    monitor_service.rule_loader.config_path = Path(__file__).parent.parent / "config/rules.yaml"
    monitor_service.initialize()
    
    # 处理记录
    from app.infra.datastore.DatParser import iter_new_records
    run_id = f"DEMO_{file_name}"
    records = []
    total_alarms = 0
    
    for i, record in enumerate(iter_new_records(file_path, run_id)):
        if i >= 30:  # 最多处理30条
            break
        
        records.append(record)
        
        # 打印record信息（如果开启）
        if print_record and i < print_count:
            print(f"\n📊 Record #{i+1}")
            print(f"   时间戳: {record.ts}")
            print(f"   传感器值: {record.metrics}")
            print(f"   文件位置: {record.file_pos}")
        
        # 处理record并获取告警
        alarms = monitor_service.process_record(record, run_id)
        total_alarms += len(alarms)
        
        # 打印告警信息（如果开启）
        if print_record and i < print_count and alarms:
            print(f"   🚨 触发 {len(alarms)} 个告警")
        elif print_record and i < print_count:
            print(f"   ✅ 无告警")
    
    print(f"\n" + "=" * 60)
    print("📊 处理摘要")
    print("=" * 60)
    print(f"📈 总记录数: {len(records)}")
    print(f"🚨 告警事件: {total_alarms}")
    if total_alarms > 0:
        print(f"⚠️  告警率: {total_alarms/len(records)*100:.2f}%")
    else:
        print("✅ 无异常告警")
    print("=" * 60)


if __name__ == "__main__":
    main() 