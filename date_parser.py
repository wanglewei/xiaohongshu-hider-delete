"""
日期解析模块
处理小红书笔记的发布日期解析和筛选
"""

import re
from datetime import datetime
from typing import Optional, List
from dateutil.parser import parse as date_parse


class DateParser:
    """日期解析器"""
    
    def __init__(self):
        self.date_patterns = [
            # 发布于 2024年06月20日 23:46
            r'发布于\s*(\d{4})年(\d{1,2})月(\d{1,2})日\s*(\d{1,2}):(\d{2})',
            # 2024-06-20 23:46
            r'(\d{4})-(\d{1,2})-(\d{1,2})\s*(\d{1,2}):(\d{2})',
            # 2024/06/20 23:46
            r'(\d{4})/(\d{1,2})/(\d{1,2})\s*(\d{1,2}):(\d{2})',
        ]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """
        解析日期字符串
        
        Args:
            date_str: 日期字符串
            
        Returns:
            datetime对象或None
        """
        if not date_str:
            return None
            
        # 尝试各种日期模式
        for pattern in self.date_patterns:
            match = re.search(pattern, date_str)
            if match:
                try:
                    year, month, day, hour, minute = map(int, match.groups())
                    return datetime(year, month, day, hour, minute)
                except ValueError:
                    continue
        
        # 尝试使用dateutil解析
        try:
            return date_parse(date_str)
        except:
            return None
    
    def filter_by_year(self, notes: List[dict], target_year: int) -> List[dict]:
        """
        按年份筛选笔记
        
        Args:
            notes: 笔记列表
            target_year: 目标年份
            
        Returns:
            筛选后的笔记列表
        """
        filtered_notes = []
        for note in notes:
            date_obj = self.parse_date(note.get('date', ''))
            if date_obj and date_obj.year == target_year:
                filtered_notes.append(note)
        return filtered_notes
    
    def filter_by_date_range(self, notes: List[dict], start_date: datetime, end_date: datetime) -> List[dict]:
        """
        按日期范围筛选笔记
        
        Args:
            notes: 笔记列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            筛选后的笔记列表
        """
        filtered_notes = []
        for note in notes:
            date_obj = self.parse_date(note.get('date', ''))
            if date_obj and start_date <= date_obj <= end_date:
                filtered_notes.append(note)
        return filtered_notes
    
    def get_available_years(self, notes: List[dict]) -> List[int]:
        """
        获取笔记中可用的年份列表
        
        Args:
            notes: 笔记列表
            
        Returns:
            年份列表（已排序）
        """
        years = set()
        for note in notes:
            date_obj = self.parse_date(note.get('date', ''))
            if date_obj:
                years.add(date_obj.year)
        return sorted(list(years))
    
    def format_date(self, date_obj: datetime) -> str:
        """
        格式化日期显示
        
        Args:
            date_obj: datetime对象
            
        Returns:
            格式化的日期字符串
        """
        return date_obj.strftime("%Y年%m月%d日 %H:%M")
