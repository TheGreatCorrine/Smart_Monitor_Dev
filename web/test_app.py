#!/usr/bin/env python3
"""
web/test_app.py
------------------------------------
测试Flask应用是否正常工作
"""
import requests
import time
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))

def test_flask_app():
    """测试Flask应用"""
    print("🧪 测试Flask应用...")
    
    try:
        # 测试健康检查API
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            print("✅ 健康检查API正常")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 健康检查API失败: {response.status_code}")
            return False
            
        # 测试基础API
        response = requests.get('http://localhost:5000/api/test', timeout=5)
        if response.status_code == 200:
            print("✅ 基础API正常")
            print(f"响应: {response.json()}")
        else:
            print(f"❌ 基础API失败: {response.status_code}")
            return False
            
        # 测试主页面
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            print("✅ 主页面正常")
        else:
            print(f"❌ 主页面失败: {response.status_code}")
            return False
            
        print("🎉 所有测试通过！Flask应用运行正常")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Flask应用，请确保应用正在运行")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False

if __name__ == '__main__':
    # 等待应用启动
    print("⏳ 等待Flask应用启动...")
    time.sleep(2)
    
    success = test_flask_app()
    sys.exit(0 if success else 1) 