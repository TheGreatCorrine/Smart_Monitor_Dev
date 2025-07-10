#!/usr/bin/env python3
"""
run_tests.py
------------------------------------
统一测试运行脚本
"""
import sys
import os
import subprocess
from pathlib import Path

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    print("=" * 60)
    
    unit_tests = [
        "tests/unit/test_record.py",
        "tests/unit/test_sensor_config.py", 
        "tests/unit/test_rule_engine.py"
    ]
    
    for test_file in unit_tests:
        if Path(test_file).exists():
            print(f"\n📝 运行: {test_file}")
            print("-" * 40)
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ 通过")
                else:
                    print("❌ 失败")
                    print(result.stdout)
                    print(result.stderr)
            except Exception as e:
                print(f"❌ 错误: {e}")
        else:
            print(f"⚠️  文件不存在: {test_file}")

def run_integration_tests():
    """运行集成测试"""
    print("\n🔗 运行集成测试...")
    print("=" * 60)
    
    integration_tests = [
        "tests/integration/test_monitor_integration.py",
        "tests/integration/test_parse_dat.py"
    ]
    
    for test_file in integration_tests:
        if Path(test_file).exists():
            print(f"\n📝 运行: {test_file}")
            print("-" * 40)
            try:
                result = subprocess.run([sys.executable, test_file], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    print("✅ 通过")
                else:
                    print("❌ 失败")
                    print(result.stdout)
                    print(result.stderr)
            except Exception as e:
                print(f"❌ 错误: {e}")
        else:
            print(f"⚠️  文件不存在: {test_file}")

def run_all_tests():
    """运行所有测试"""
    print("🚀 开始运行所有测试")
    print("=" * 60)
    
    run_unit_tests()
    run_integration_tests()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成!")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            run_unit_tests()
        elif sys.argv[1] == "integration":
            run_integration_tests()
        else:
            print("用法: python run_tests.py [unit|integration|all]")
    else:
        run_all_tests() 