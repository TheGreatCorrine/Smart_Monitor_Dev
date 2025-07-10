"""
backend/app/__main__.py
------------------------------------
模块入口点 - 当运行 python -m backend.app 时执行
"""
from .cli import interactive_demo

if __name__ == "__main__":
    interactive_demo() 