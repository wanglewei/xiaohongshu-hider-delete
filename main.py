"""
小红书笔记批量隐藏工具 - 主程序

这个工具可以帮助用户批量管理小红书笔记的可见性设置。
支持按年份筛选、手动选择等多种方式来隐藏、显示或删除笔记。

作者: Xiaohongshu Note Manager Team
版本: 1.0.0
许可证: MIT License
"""

__version__ = "1.0.0"
__author__ = "Xiaohongshu Note Manager Team"
__license__ = "MIT"
__description__ = "一个小红书笔记批量管理工具"

import sys
import os
from typing import List, Dict, Optional

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scraper import XiaohongshuScraper
from permission import PermissionManager
from date_parser import DateParser
from ui import UserInterface
from logger import setup_logger, get_logger
from colorama import Fore


class XiaohongshuHider:
    """小红书笔记隐藏器主类"""
    
    def __init__(self):
        """初始化主程序"""
        self.ui = UserInterface()
        self.logger = setup_logger()
        self.scraper = None
        self.permission_manager = None
        self.date_parser = DateParser()
        self.notes_cache = None  # 缓存笔记数据，避免重复提取
        
    def run(self) -> None:
        """运行主程序"""
        try:
            self.ui.print_header()
            self.logger.info("程序启动")
            
            while True:
                mode = self.ui.get_operation_mode()
                
                if mode == 'exit':
                    self.ui.print_info("程序退出")
                    break
                elif mode == 'view':
                    self._view_notes_mode()
                elif mode == 'refresh':
                    self._refresh_notes_mode()
                elif mode == 'year_hide':
                    self._year_filter_mode('hide')
                elif mode == 'manual_hide':
                    self._manual_select_mode('hide')
                elif mode == 'year_show':
                    self._year_filter_mode('show')
                elif mode == 'manual_show':
                    self._manual_select_mode('show')
                elif mode == 'year_delete':
                    self._year_filter_mode('delete')
                elif mode == 'manual_delete':
                    self._manual_select_mode('delete')
                
                if mode != 'exit':
                    self.ui.wait_for_enter()
                    self.ui.print_header()
                    
        except KeyboardInterrupt:
            self.ui.print_warning("程序被用户中断")
            self.logger.info("程序被用户中断")
        except Exception as e:
            self.ui.print_error(f"程序运行出错: {e}")
            self.logger.error(f"程序运行出错: {e}")
        finally:
            self._cleanup()
    
    def _view_notes_mode(self) -> None:
        """仅查看笔记模式"""
        notes = self._extract_notes()
        if notes:
            self.ui.display_notes_summary(notes, "所有笔记")
            
            # 显示年份统计
            available_years = self.date_parser.get_available_years(notes)
            if available_years:
                print(f"\n{Fore.CYAN}年份统计:")
                for year in available_years:
                    year_notes = self.date_parser.filter_by_year(notes, year)
                    print(f"{Fore.WHITE}  {year}年: {len(year_notes)} 条")
        else:
            self.ui.print_error("没有找到笔记")
    
    def _refresh_notes_mode(self) -> None:
        """刷新笔记模式，清除缓存并重新提取"""
        self.ui.print_info("正在清除笔记缓存...")
        self.notes_cache = None  # 清除缓存
        
        # 重新提取笔记
        notes = self._extract_notes()
        if notes:
            self.ui.print_success(f"刷新完成，共提取 {len(notes)} 条笔记")
            self.ui.display_notes_summary(notes, "刷新后的笔记")
            
            # 显示年份统计
            available_years = self.date_parser.get_available_years(notes)
            if available_years:
                print(f"\n{Fore.CYAN}年份统计:")
                for year in available_years:
                    year_notes = self.date_parser.filter_by_year(notes, year)
                    print(f"{Fore.WHITE}  {year}年: {len(year_notes)} 条")
        else:
            self.ui.print_error("刷新后没有找到笔记")
    
    def display_notes_info(self, notes: List[Dict]) -> None:
        """
        显示笔记详细信息
        
        Args:
            notes: 笔记列表
        """
        if not notes:
            self.ui.print_error("没有笔记信息可显示")
            return
        
        try:
            from colorama import Fore, Style
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}笔记详细信息 (共 {len(notes)} 条)")
            print(f"{Fore.CYAN}{'='*60}")
            
            for i, note in enumerate(notes, 1):
                print(f"\n{Fore.YELLOW}[{i}] {Fore.WHITE}{note['title'][:50]}{'...' if len(note['title']) > 50 else ''}")
                print(f"{Fore.CYAN}    ID: {Fore.WHITE}{note['note_id']}")
                print(f"{Fore.CYAN}    日期: {Fore.WHITE}{note['date']}")
                print(f"{Fore.CYAN}    链接: {Fore.WHITE}{note['url'][:80]}{'...' if len(note['url']) > 80 else ''}")
                
                # 尝试获取笔记的可见性状态
                if self.permission_manager and self.scraper and self.scraper.driver:
                    try:
                        note_element = self.permission_manager._refresh_note_element(note['note_id'])
                        if note_element:
                            visibility = self.permission_manager.check_note_visibility(note_element)
                            status_text = {
                                'private': f"{Fore.MAGENTA}仅自己可见",
                                'public': f"{Fore.GREEN}公开可见",
                                'unknown': f"{Fore.YELLOW}未知状态",
                                None: f"{Fore.RED}无法获取"
                            }.get(visibility, f"{Fore.RED}错误")
                            print(f"{Fore.CYAN}    状态: {status_text}{Style.RESET_ALL}")
                        else:
                            print(f"{Fore.CYAN}    状态: {Fore.RED}元素未找到{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.CYAN}    状态: {Fore.RED}获取失败 ({str(e)[:30]}...){Style.RESET_ALL}")
                else:
                    print(f"{Fore.CYAN}    状态: {Fore.YELLOW}未检查{Style.RESET_ALL}")
            
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"{Fore.CYAN}显示完成{Style.RESET_ALL}")
            
        except Exception as e:
            self.ui.print_error(f"显示笔记信息时发生错误: {e}")
    
    def _year_filter_mode(self, operation: str = 'hide') -> None:
        """
        按年份筛选模式
        
        Args:
            operation: 操作类型 ('hide' 或 'show')
        """
        notes = self._extract_notes()
        if not notes:
            self.ui.print_error("没有找到笔记")
            return
        
        # 获取可用年份
        available_years = self.date_parser.get_available_years(notes)
        if not available_years:
            self.ui.print_error("没有找到有效的日期信息")
            return
        
        # 选择年份
        selected_year = self.ui.select_year(available_years)
        if not selected_year:
            return
        
        # 筛选指定年份的笔记
        filtered_notes = self.date_parser.filter_by_year(notes, selected_year)
        if not filtered_notes:
            self.ui.print_info(f"{selected_year}年没有笔记")
            return
        
        operation_text = "隐藏" if operation == 'hide' else "显示"
        self.ui.print_info(f"找到 {selected_year}年的笔记 {len(filtered_notes)} 条")
        self.ui.display_notes_summary(filtered_notes, f"{selected_year}年的笔记")
        
        # 确认操作
        if self.ui.confirm_batch_operation(filtered_notes, operation):
            self._execute_operation(filtered_notes, operation)
    
    def _manual_select_mode(self, operation: str = 'hide') -> None:
        """
        手动选择模式
        
        Args:
            operation: 操作类型 ('hide' 或 'show')
        """
        notes = self._extract_notes()
        if not notes:
            self.ui.print_error("没有找到笔记")
            return
        
        # 手动选择笔记
        selected_notes = self.ui.select_notes_manually(notes)
        if not selected_notes:
            self.ui.print_info("没有选择任何笔记")
            return
        
        operation_text = "隐藏" if operation == 'hide' else "显示"
        self.ui.print_info(f"已选择 {len(selected_notes)} 条笔记进行{operation_text}")
        
        # 确认操作
        if self.ui.confirm_batch_operation(selected_notes, operation):
            self._execute_operation(selected_notes, operation)
    
    def _extract_notes(self) -> List[Dict]:
        """
        提取笔记数据，支持Chrome会话复用和笔记缓存
        
        Returns:
            笔记列表
        """
        try:
            # 检查是否有缓存的笔记数据
            if self.notes_cache is not None:
                self.ui.print_info(f"使用缓存的笔记数据，共 {len(self.notes_cache)} 条笔记")
                return self.notes_cache
            
            # 检查是否已有Chrome会话
            if self.scraper and self.scraper.driver:
                try:
                    # 测试现有连接是否有效
                    self.scraper.driver.current_url
                    self.ui.print_info("检测到现有Chrome会话，复用现有连接...")
                    
                    # 重新提取笔记（因为页面状态可能已经改变）
                    self.logger.log_extraction_start()
                    notes = self.scraper.extract_notes_with_auto_scroll()
                    self.logger.log_extraction_end(len(notes))
                    
                    if notes:
                        self.ui.print_success(f"成功提取 {len(notes)} 条笔记")
                        self.notes_cache = notes  # 缓存笔记数据
                    else:
                        self.ui.print_error("没有提取到笔记")
                    
                    return notes
                    
                except Exception as e:
                    self.ui.print_warning(f"现有Chrome会话无效: {e}")
                    self.scraper = None
            
            # 需要创建新的Chrome会话
            self.ui.print_info("正在启动浏览器...")
            
            # 创建爬虫实例（不使用with语句，避免自动关闭）
            scraper = XiaohongshuScraper(headless=False)
            scraper.setup_driver()
            self.scraper = scraper
            self.logger.log_extraction_start()
            
            # 提取笔记（使用自动滚动功能）
            notes = scraper.extract_notes_with_auto_scroll()
            
            self.logger.log_extraction_end(len(notes))
            
            if notes:
                self.ui.print_success(f"成功提取 {len(notes)} 条笔记")
                self.notes_cache = notes  # 缓存笔记数据
            else:
                self.ui.print_error("没有提取到笔记")
            
            return notes
                
        except Exception as e:
            self.ui.print_error(f"提取笔记失败: {e}")
            self.logger.error(f"提取笔记失败: {e}")
            return []
    
    def _execute_operation(self, notes: List[Dict], operation: str = 'hide') -> None:
        """
        执行操作（隐藏、显示或删除）
        
        Args:
            notes: 要操作的笔记列表
            operation: 操作类型 ('hide', 'show', 或 'delete')
        """
        if not self.scraper or not self.scraper.driver:
            self.ui.print_error("浏览器连接已断开，请重新提取笔记")
            return
        
        try:
            # 创建权限管理器
            self.permission_manager = PermissionManager(self.scraper.driver)
            
            if operation == 'hide':
                operation_text = "隐藏"
                operation_name = "批量隐藏笔记"
            elif operation == 'show':
                operation_text = "显示"
                operation_name = "批量显示笔记"
            elif operation == 'delete':
                operation_text = "删除"
                operation_name = "批量删除笔记"
            else:
                self.ui.print_error("未知的操作类型")
                return
            
            # 记录操作开始
            self.logger.log_operation_start(operation_name, len(notes))
            
            # 执行批量操作
            if operation == 'hide':
                results = self.permission_manager.hide_notes_batch(notes)
            elif operation == 'show':
                results = self.permission_manager.show_notes_batch(notes)
            elif operation == 'delete':
                results = self.permission_manager.delete_notes_batch(notes)
            else:
                results = {'success': 0, 'failed': len(notes), 'total': len(notes)}
            
            # 记录操作结束
            self.logger.log_operation_end(operation_name, results)
            
            # 显示结果
            self.ui.display_operation_results(results)
            
            # 显示日志文件位置
            log_file = self.logger.get_log_file_path()
            if log_file:
                self.ui.print_info(f"详细日志已保存到: {log_file}")
                
        except Exception as e:
            self.ui.print_error(f"执行{operation_text}操作失败: {e}")
            self.logger.error(f"执行{operation_text}操作失败: {e}")
    
    def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.scraper:
                self.scraper.close()
            if self.logger:
                self.logger.close()
        except Exception as e:
            print(f"清理资源时发生错误: {e}")


def main():
    """主函数"""
    try:
        # 检查Python版本
        if sys.version_info < (3, 7):
            print("错误: 需要Python 3.7或更高版本")
            sys.exit(1)
        
        # 运行主程序
        hider = XiaohongshuHider()
        hider.run()
        
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
