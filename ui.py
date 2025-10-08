"""
用户交互界面模块
处理用户输入和显示输出
"""

import os
import sys
from typing import List, Dict, Optional
from datetime import datetime
from colorama import init, Fore, Style, Back
from date_parser import DateParser

# 初始化colorama
init(autoreset=True)


class UserInterface:
    """用户界面管理器"""
    
    def __init__(self):
        self.date_parser = DateParser()
    
    def clear_screen(self) -> None:
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self) -> None:
        """打印程序头部"""
        self.clear_screen()
        print(f"{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}           小红书笔记批量管理工具")
        print(f"{Fore.CYAN}{'='*60}")
        print()
    
    def print_success(self, message: str) -> None:
        """打印成功消息"""
        print(f"{Fore.GREEN}✓ {message}")
    
    def print_error(self, message: str) -> None:
        """打印错误消息"""
        print(f"{Fore.RED}✗ {message}")
    
    def print_warning(self, message: str) -> None:
        """打印警告消息"""
        print(f"{Fore.YELLOW}⚠ {message}")
    
    def print_info(self, message: str) -> None:
        """打印信息消息"""
        print(f"{Fore.BLUE}ℹ {message}")
    
    def get_user_confirmation(self, message: str, default: bool = False) -> bool:
        """
        获取用户确认
        
        Args:
            message: 确认消息
            default: 默认值
            
        Returns:
            用户确认结果
        """
        suffix = " [Y/n]" if default else " [y/N]"
        response = input(f"{Fore.YELLOW}{message}{suffix}: ").strip().lower()
        
        if not response:
            return default
        
        return response in ['y', 'yes', '是', '确认']
    
    def select_year(self, available_years: List[int]) -> Optional[int]:
        """
        选择年份
        
        Args:
            available_years: 可用年份列表
            
        Returns:
            选择的年份或None
        """
        if not available_years:
            self.print_error("没有可用的年份")
            return None
        
        print(f"\n{Fore.CYAN}可用年份:")
        for i, year in enumerate(available_years, 1):
            print(f"{Fore.WHITE}  {i}. {year}年")
        
        while True:
            try:
                choice = input(f"\n{Fore.YELLOW}请选择年份 (输入数字): ").strip()
                if not choice:
                    return None
                
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(available_years):
                    return available_years[choice_idx]
                else:
                    self.print_error("无效的选择，请重新输入")
            except ValueError:
                self.print_error("请输入有效的数字")
    
    def select_notes_manually(self, notes: List[Dict]) -> List[Dict]:
        """
        手动选择笔记
        
        Args:
            notes: 笔记列表
            
        Returns:
            选择的笔记列表
        """
        if not notes:
            return []
        
        print(f"\n{Fore.CYAN}笔记列表:")
        for i, note in enumerate(notes, 1):
            title = note['title'][:40] + "..." if len(note['title']) > 40 else note['title']
            date = note['date'] or "未知日期"
            print(f"{Fore.WHITE}  {i:2d}. {title} ({date})")
        
        print(f"\n{Fore.YELLOW}选择方式:")
        print(f"{Fore.WHITE}  1. 输入序号 (如: 2 或 1,3,5)")
        print(f"{Fore.WHITE}  2. 输入范围 (如: 1-5)")
        print(f"{Fore.WHITE}  3. 输入 'all' 选择全部")
        print(f"{Fore.WHITE}  4. 输入 'none' 取消选择")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}请选择: ").strip()
            
            if choice.lower() == 'all':
                return notes
            elif choice.lower() == 'none':
                return []
            elif choice.isdigit():
                # 处理单个序号
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(notes):
                        return [notes[idx]]
                    else:
                        self.print_error(f"序号 {idx+1} 无效")
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            elif ',' in choice:
                # 处理序号选择
                try:
                    indices = [int(x.strip()) - 1 for x in choice.split(',')]
                    selected = []
                    for idx in indices:
                        if 0 <= idx < len(notes):
                            selected.append(notes[idx])
                        else:
                            self.print_error(f"序号 {idx+1} 无效")
                    return selected
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            elif '-' in choice:
                # 处理范围选择
                try:
                    start, end = choice.split('-')
                    start_idx = int(start.strip()) - 1
                    end_idx = int(end.strip()) - 1
                    
                    if 0 <= start_idx <= end_idx < len(notes):
                        return notes[start_idx:end_idx + 1]
                    else:
                        self.print_error("范围无效，请重新输入")
                except ValueError:
                    self.print_error("输入格式错误，请重新输入")
            else:
                self.print_error("输入格式错误，请重新输入")
    
    def display_notes_summary(self, notes: List[Dict], title: str = "笔记列表") -> None:
        """
        显示笔记摘要
        
        Args:
            notes: 笔记列表
            title: 标题
        """
        print(f"\n{Fore.CYAN}{title} ({len(notes)} 条):")
        print(f"{Fore.CYAN}{'-'*50}")
        
        for i, note in enumerate(notes, 1):
            title = note['title'][:45] + "..." if len(note['title']) > 45 else note['title']
            date = note['date'] or "未知日期"
            status = "✓" if note.get('has_permission_button') else "✗"
            print(f"{Fore.WHITE}{i:2d}. {status} {title} ({date})")
        
        print(f"{Fore.CYAN}{'-'*50}")
    
    def confirm_batch_operation(self, notes: List[Dict], operation: str = "hide") -> bool:
        """
        确认批量操作
        
        Args:
            notes: 要操作的笔记列表
            operation: 操作类型 ("hide", "show", 或 "delete")
            
        Returns:
            是否确认操作
        """
        if operation == "hide":
            self.display_notes_summary(notes, "即将隐藏的笔记")
            print(f"\n{Fore.RED}警告: 此操作将把上述笔记设置为'仅自己可见'")
            print(f"{Fore.RED}操作后，其他用户将无法看到这些笔记")
            return self.get_user_confirmation("确认执行隐藏操作吗？", False)
        elif operation == "show":
            self.display_notes_summary(notes, "即将显示的笔记")
            print(f"\n{Fore.GREEN}提示: 此操作将把上述笔记设置为'所有人可见'")
            print(f"{Fore.GREEN}操作后，其他用户将可以看到这些笔记")
            return self.get_user_confirmation("确认执行显示操作吗？", False)
        elif operation == "delete":
            self.display_notes_summary(notes, "即将删除的笔记")
            print(f"\n{Back.RED}{Fore.WHITE}⚠️  危险操作警告 ⚠️")
            print(f"{Fore.RED}此操作将永久删除上述笔记")
            print(f"{Fore.RED}删除后无法恢复，请谨慎操作")
            print(f"{Fore.RED}建议先进行隐藏操作，确认不需要后再删除")
            return self.get_user_confirmation("确认执行删除操作吗？", False)
        else:
            return False
    
    def display_operation_results(self, results: Dict[str, int]) -> None:
        """
        显示操作结果
        
        Args:
            results: 操作结果统计
        """
        print(f"\n{Fore.CYAN}操作结果:")
        print(f"{Fore.CYAN}{'-'*30}")
        print(f"{Fore.WHITE}总计: {results['total']} 条")
        print(f"{Fore.GREEN}成功: {results['success']} 条")
        print(f"{Fore.RED}失败: {results['failed']} 条")
        
        if results['failed'] > 0:
            self.print_warning("部分操作失败，请检查网络连接和页面状态")
        else:
            self.print_success("所有操作已完成")
    
    def get_operation_mode(self) -> str:
        """
        获取操作模式
        
        Returns:
            操作模式
        """
        print(f"\n{Fore.CYAN}请选择操作模式:")
        print(f"{Fore.WHITE}  1. 按年份筛选并隐藏")
        print(f"{Fore.WHITE}  2. 手动选择笔记隐藏")
        print(f"{Fore.WHITE}  3. 按年份筛选并显示")
        print(f"{Fore.WHITE}  4. 手动选择笔记显示")
        print(f"{Fore.RED}  5. 按年份筛选并删除 ⚠️")
        print(f"{Fore.RED}  6. 手动选择笔记删除 ⚠️")
        print(f"{Fore.WHITE}  7. 仅查看笔记列表")
        print(f"{Fore.CYAN}  8. 刷新笔记数据")
        print(f"{Fore.WHITE}  9. 退出程序")
        
        while True:
            choice = input(f"\n{Fore.YELLOW}请选择 (1-9): ").strip()
            
            if choice == '1':
                return 'year_hide'
            elif choice == '2':
                return 'manual_hide'
            elif choice == '3':
                return 'year_show'
            elif choice == '4':
                return 'manual_show'
            elif choice == '5':
                return 'year_delete'
            elif choice == '6':
                return 'manual_delete'
            elif choice == '7':
                return 'view'
            elif choice == '8':
                return 'refresh'
            elif choice == '9':
                return 'exit'
            else:
                self.print_error("无效的选择，请重新输入")
    
    def show_progress(self, current: int, total: int, message: str = "") -> None:
        """
        显示进度
        
        Args:
            current: 当前进度
            total: 总数
            message: 附加消息
        """
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 30
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r{Fore.CYAN}[{bar}] {percentage:.1f}% ({current}/{total}) {message}", end='', flush=True)
        
        if current == total:
            print()  # 换行
    
    def wait_for_enter(self, message: str = "按回车键继续...") -> None:
        """
        等待用户按回车
        
        Args:
            message: 提示消息
        """
        input(f"\n{Fore.YELLOW}{message}")
