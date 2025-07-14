#!/usr/bin/env python3
"""
backend/app/__main__.py
------------------------------------
应用主入口 - 支持CLI和GUI两种模式
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.cli import main as cli_main
from backend.app.gui import main as gui_main


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="冰箱测试异常状态智能监测系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # CLI模式 - 处理单个文件
  python -m backend.app --cli data/MPL6.dat
  
  # GUI模式 - 图形界面
  python -m backend.app --gui
  
  # CLI模式 - 交互式
  python -m backend.app --cli --interactive
        """
    )
    
    parser.add_argument(
        "--cli",
        action="store_true",
        help="使用命令行界面模式"
    )
    
    parser.add_argument(
        "--gui",
        action="store_true",
        help="使用图形用户界面模式"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="CLI模式下的交互式选择"
    )
    
    # 传递其他参数给CLI
    parser.add_argument("dat_file", nargs="?", help="数据文件路径")
    parser.add_argument("--config", "-c", default="config/rules.yaml", help="配置文件路径")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--run-id", help="自定义运行ID")
    
    args = parser.parse_args()
    
    # 如果没有指定模式，默认使用GUI
    if not args.cli and not args.gui:
        args.gui = True
    
    if args.cli and args.gui:
        print("❌ 错误: 不能同时使用CLI和GUI模式")
        sys.exit(1)
    
    if args.cli:
        # CLI模式
        if args.interactive:
            # 交互式模式
            from backend.app.cli import interactive_demo
            interactive_demo()
        else:
            # 标准CLI模式
            if not args.dat_file:
                print("❌ 错误: CLI模式需要指定数据文件")
                print("使用示例: python -m backend.app --cli data/MPL6.dat")
                sys.exit(1)
            
            # 设置sys.argv以兼容CLI的参数解析
            sys.argv = [sys.argv[0], args.dat_file]
            if args.config != "config/rules.yaml":
                sys.argv.extend(["--config", args.config])
            if args.verbose:
                sys.argv.append("--verbose")
            if args.run_id:
                sys.argv.extend(["--run-id", args.run_id])
            
            cli_main()
    
    elif args.gui:
        # GUI模式
        try:
            gui_main()
        except ImportError as e:
            print(f"❌ 错误: GUI模式需要tkinter支持: {e}")
            print("请确保Python安装了tkinter模块")
            sys.exit(1)
        except Exception as e:
            print(f"❌ GUI启动失败: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main() 