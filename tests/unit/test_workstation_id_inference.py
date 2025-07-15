#!/usr/bin/env python3
"""
测试工作站ID推断功能
"""
import re
from pathlib import Path

def test_workstation_id_inference():
    """测试从文件名推断工作站ID"""
    
    test_files = [
        "MPL6.dat",
        "mpl3.dat", 
        "MPL12.dat",
        "mpl1.dat",
        "test.dat",  # 不匹配的文件
        "MPL.dat",   # 没有数字的文件
    ]
    
    print("🔍 测试工作站ID推断功能")
    print("=" * 50)
    
    for filename in test_files:
        path = Path(filename)
        workstation_id = "1"  # 默认值
        
        if path.stem.startswith('mpl') or path.stem.startswith('MPL'):
            # 从文件名中提取工作站ID
            match = re.search(r'mpl(\d+)', path.stem.lower())
            if match:
                workstation_id = match.group(1)
                print(f"✅ {filename} -> 工作站ID: {workstation_id}")
            else:
                print(f"❌ {filename} -> 无法推断工作站ID，使用默认值: {workstation_id}")
        else:
            print(f"❌ {filename} -> 不是MPL文件，使用默认值: {workstation_id}")
    
    print("\n🎯 测试结果:")
    print("- MPL6.dat 应该推断为工作站ID: 6")
    print("- mpl3.dat 应该推断为工作站ID: 3") 
    print("- MPL12.dat 应该推断为工作站ID: 12")
    print("- mpl1.dat 应该推断为工作站ID: 1")
    print("- test.dat 应该使用默认值: 1")
    print("- MPL.dat 应该使用默认值: 1")

if __name__ == "__main__":
    test_workstation_id_inference() 