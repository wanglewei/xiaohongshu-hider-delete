"""
测试滚动修复功能的脚本
"""

import sys
import os
from time import sleep

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import XiaohongshuScraper
from permission import PermissionManager


def test_scroll_functionality():
    """测试滚动功能"""
    print("=== 测试小红书滚动功能 ===")
    
    try:
        # 创建爬虫实例
        scraper = XiaohongshuScraper(headless=False)
        scraper.setup_driver()
        
        print("✓ 浏览器启动成功")
        
        # 检查登录状态
        if not scraper.login_if_needed():
            print("❌ 登录失败")
            return
        
        print("✓ 登录检查通过")
        
        # 等待页面完全加载
        print("等待页面加载完成...")
        sleep(5)
        
        # 测试查找滚动容器
        print("\n--- 测试滚动容器查找 ---")
        scroll_container = scraper._find_scroll_container()
        
        if scroll_container:
            print("✓ 成功找到滚动容器")
            
            # 测试滚动功能
            print("\n--- 测试滚动功能 ---")
            for i in range(3):
                success = scraper._scroll_container(scroll_container)
                if success:
                    print(f"✓ 第 {i+1} 次滚动成功")
                else:
                    print(f"⚠ 第 {i+1} 次滚动失败或已到底部")
                    break
                sleep(2)
        else:
            print("❌ 未找到滚动容器")
        
        # 测试查找笔记元素
        print("\n--- 测试笔记元素查找 ---")
        note_elements = scraper._find_note_elements()
        print(f"✓ 找到 {len(note_elements)} 个笔记元素")
        
        if note_elements:
            # 显示前3个笔记的信息
            print("\n--- 前3个笔记信息 ---")
            for i, element in enumerate(note_elements[:3]):
                try:
                    note_data = scraper._extract_note_data(element, i)
                    if note_data:
                        print(f"笔记 {i+1}: {note_data['title'][:30]}... | {note_data['date']}")
                        print(f"  权限按钮: {'✓' if note_data['has_permission_button'] else '✗'}")
                except Exception as e:
                    print(f"笔记 {i+1}: 提取失败 - {e}")
        
        # 测试自动滚动
        print("\n--- 测试自动滚动 ---")
        input("按回车键开始自动滚动测试...")
        
        notes = scraper.extract_notes_with_auto_scroll()
        print(f"✓ 自动滚动完成，共提取 {len(notes)} 条笔记")
        
        # 测试权限管理器
        if notes:
            print("\n--- 测试权限管理器 ---")
            permission_manager = PermissionManager(scraper.driver)
            
            # 测试获取笔记ID
            first_note = notes[0]
            note_id = permission_manager.get_note_id(first_note['element'])
            print(f"第一条笔记ID: {note_id}")
            
            # 测试检查可见性
            if first_note['element']:
                visibility = permission_manager.check_note_visibility(first_note['element'])
                print(f"第一条笔记可见性: {visibility}")
        
        print("\n=== 测试完成 ===")
        input("按回车键关闭浏览器...")
        
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键关闭浏览器...")
    
    finally:
        try:
            scraper.close()
        except:
            pass


if __name__ == "__main__":
    test_scroll_functionality()
