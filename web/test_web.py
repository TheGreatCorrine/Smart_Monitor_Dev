#!/usr/bin/env python3
"""
web/test_web.py
------------------------------------
测试Web应用是否正常工作
"""
import requests
import time
import sys

def test_web_app():
    """测试Web应用"""
    print("🧪 测试Web应用...")
    
    base_url = "http://localhost:8080"
    
    # 测试健康检查
    print("\n1. 测试健康检查API...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {data}")
            print("✅ 健康检查API正常")
        else:
            print(f"❌ 健康检查API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查API错误: {e}")
    
    # 测试主页面
    print("\n2. 测试主页面...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 主页面加载成功")
            print(f"页面大小: {len(response.text)} 字符")
        else:
            print(f"❌ 主页面加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 主页面错误: {e}")
    
    # 测试简化页面
    print("\n3. 测试简化页面...")
    try:
        response = requests.get(f"{base_url}/simple", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ 简化页面加载成功")
            print(f"页面大小: {len(response.text)} 字符")
        else:
            print(f"❌ 简化页面加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 简化页面错误: {e}")
    
    # 测试静态文件
    print("\n4. 测试静态文件...")
    try:
        response = requests.get(f"{base_url}/static/css/style.css", timeout=5)
        print(f"CSS状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ CSS文件加载成功")
        else:
            print(f"❌ CSS文件加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ CSS文件错误: {e}")
    
    try:
        response = requests.get(f"{base_url}/static/js/app.js", timeout=5)
        print(f"JS状态码: {response.status_code}")
        if response.status_code == 200:
            print("✅ JavaScript文件加载成功")
        else:
            print(f"❌ JavaScript文件加载失败: {response.status_code}")
    except Exception as e:
        print(f"❌ JavaScript文件错误: {e}")

if __name__ == '__main__':
    print("🚀 开始Web应用测试...")
    print("请确保Flask应用正在运行在端口8080上")
    print("如果应用没有运行，请先运行: python app.py")
    print()
    
    # 等待应用启动
    print("⏳ 等待应用启动...")
    time.sleep(2)
    
    test_web_app()
    
    print("\n" + "="*50)
    print("📊 测试完成")
    print("如果所有测试都通过，请访问:")
    print("主页面: http://localhost:8080")
    print("简化页面: http://localhost:8080/simple")
    print("健康检查: http://localhost:8080/api/health") 