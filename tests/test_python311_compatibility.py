#!/usr/bin/env python3
"""
test_python311_compatibility.py
------------------------------------
Python 3.11兼容性测试脚本
确保所有代码在Python 3.11中正常运行
"""
import sys
import importlib
from pathlib import Path

def test_imports():
    """测试所有模块导入"""
    print("🔍 测试模块导入...")
    
    # 添加项目路径
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    
    modules_to_test = [
        "backend.app.entities.Record",
        "backend.app.entities.Rule", 
        "backend.app.entities.AlarmEvent",
        "backend.app.entities.Sensor",
        "backend.app.entities.TestSession",
        "backend.app.services.RuleEngineService",
        "backend.app.services.AlarmService",
        "backend.app.usecases.Monitor",
        "backend.app.controllers.MonitorController",
        "backend.app.controllers.RuleController",
        "backend.app.controllers.AlarmController",
        "backend.app.controllers.DataController",
        "backend.app.infra.datastore.DatParser",
        "backend.app.infra.config.RuleLoader",
        "backend.app.infra.config.SystemConfig",
        "backend.app.gui",
    ]
    
    failed_imports = []
    
    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✅ {module_name}")
        except Exception as e:
            print(f"❌ {module_name}: {e}")
            failed_imports.append((module_name, str(e)))
    
    if failed_imports:
        print(f"\n❌ 导入失败: {len(failed_imports)} 个模块")
        for module, error in failed_imports:
            print(f"   {module}: {error}")
        return False
    else:
        print(f"\n✅ 所有模块导入成功!")
        return True

def test_syntax():
    """测试语法兼容性"""
    print("\n🔍 测试语法兼容性...")
    
    # 测试Python 3.11兼容的语法
    try:
        # 测试类型注解语法
        from typing import Union, Optional, List, Dict
        test_var: Optional[Union[int, float]] = None
        test_list: List[str] = []
        test_dict: Dict[str, int] = {}
        print("✅ 类型注解语法")
    except Exception as e:
        print(f"❌ 类型注解语法: {e}")
        return False
    
    try:
        # 测试dataclass语法
        from dataclasses import dataclass
        @dataclass
        class TestClass:
            name: str
            value: int
        print("✅ dataclass语法")
    except Exception as e:
        print(f"❌ dataclass语法: {e}")
        return False
    
    try:
        # 测试枚举语法
        from enum import Enum
        class TestEnum(Enum):
            A = "a"
            B = "b"
        print("✅ 枚举语法")
    except Exception as e:
        print(f"❌ 枚举语法: {e}")
        return False
    
    try:
        # 测试tkinter
        import tkinter as tk
        print("✅ tkinter可用")
    except Exception as e:
        print(f"❌ tkinter: {e}")
        return False
    
    try:
        # 测试yaml
        import yaml
        print("✅ PyYAML可用")
    except Exception as e:
        print(f"❌ PyYAML: {e}")
        return False
    
    return True

def test_basic_functionality():
    """测试基本功能"""
    print("\n🔍 测试基本功能...")
    
    try:
        # 测试实体创建
        from backend.app.entities.record import Record
        from backend.app.entities.rule import Rule, Condition, ConditionType, Operator, Severity
        from datetime import datetime
        
        # 创建测试记录
        record = Record(
            run_id="test",
            ts=datetime.now(),
            metrics={"T1": 25.5, "P1": 1.2}
        )
        print("✅ Record实体创建")
        
        # 创建测试规则
        condition = Condition(
            type=ConditionType.THRESHOLD,
            sensor="T1",
            operator=Operator.GREATER_THAN,
            value=30.0
        )
        
        rule = Rule(
            id="test_rule",
            name="测试规则",
            description="测试规则描述",
            conditions=[condition],
            severity=Severity.HIGH
        )
        print("✅ Rule实体创建")
        
        # 测试序列化
        record_dict = record.to_dict()
        print("✅ Record序列化")
        
    except Exception as e:
        print(f"❌ 基本功能测试: {e}")
        return False
    
    return True

def main():
    """主测试函数"""
    print("🚀 Python 3.11兼容性测试")
    print("=" * 50)
    
    # 显示Python版本
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print()
    
    # 运行测试
    tests = [
        ("语法兼容性", test_syntax),
        ("模块导入", test_imports),
        ("基本功能", test_basic_functionality),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            if not test_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过! Python 3.11兼容性良好!")
    else:
        print("❌ 部分测试失败，需要修复兼容性问题")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 