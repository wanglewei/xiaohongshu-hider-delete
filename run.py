#!/usr/bin/env python3
"""
小红书笔记批量隐藏工具 - 启动脚本
"""

import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from main import main
    
    if __name__ == "__main__":
        print("正在启动小红书笔记批量隐藏工具...")
        print("请确保已安装Chrome浏览器")
        print("=" * 50)
        main()
        
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包:")
    print("pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"程序启动失败: {e}")
    sys.exit(1)
