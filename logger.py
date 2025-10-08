"""
日志记录模块
处理程序运行日志和错误记录
"""

import logging
import os
from datetime import datetime
from typing import Optional


class Logger:
    """日志管理器"""
    
    def __init__(self, log_dir: str = "logs", log_level: int = logging.INFO):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志目录
            log_level: 日志级别
        """
        self.log_dir = log_dir
        self.log_level = log_level
        self.logger = None
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志记录器"""
        # 创建日志目录
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"xiaohongshu_{timestamp}.log")
        
        # 创建logger
        self.logger = logging.getLogger("xiaohongshu_hider")
        self.logger.setLevel(self.log_level)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            # 文件handler
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            
            # 控制台handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)
            
            # 格式化器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # 添加handler
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """记录信息日志"""
        if self.logger:
            self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """记录警告日志"""
        if self.logger:
            self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """记录错误日志"""
        if self.logger:
            self.logger.error(message)
    
    def debug(self, message: str) -> None:
        """记录调试日志"""
        if self.logger:
            self.logger.debug(message)
    
    def log_operation_start(self, operation: str, note_count: int) -> None:
        """
        记录操作开始
        
        Args:
            operation: 操作类型
            note_count: 笔记数量
        """
        self.info(f"开始执行操作: {operation}, 笔记数量: {note_count}")
    
    def log_operation_end(self, operation: str, results: dict) -> None:
        """
        记录操作结束
        
        Args:
            operation: 操作类型
            results: 操作结果
        """
        self.info(f"操作完成: {operation}, 结果: {results}")
    
    def log_note_operation(self, note_id: str, title: str, success: bool, error_msg: Optional[str] = None) -> None:
        """
        记录单条笔记操作
        
        Args:
            note_id: 笔记ID
            title: 笔记标题
            success: 是否成功
            error_msg: 错误消息
        """
        status = "成功" if success else "失败"
        message = f"笔记操作 - ID: {note_id}, 标题: {title[:50]}, 状态: {status}"
        
        if not success and error_msg:
            message += f", 错误: {error_msg}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_extraction_start(self) -> None:
        """记录数据提取开始"""
        self.info("开始提取笔记数据")
    
    def log_extraction_end(self, note_count: int) -> None:
        """
        记录数据提取结束
        
        Args:
            note_count: 提取的笔记数量
        """
        self.info(f"数据提取完成，共提取 {note_count} 条笔记")
    
    def log_filtering(self, filter_type: str, before_count: int, after_count: int) -> None:
        """
        记录筛选操作
        
        Args:
            filter_type: 筛选类型
            before_count: 筛选前数量
            after_count: 筛选后数量
        """
        self.info(f"筛选操作 - 类型: {filter_type}, 筛选前: {before_count}, 筛选后: {after_count}")
    
    def log_login_attempt(self) -> None:
        """记录登录尝试"""
        self.info("尝试登录小红书创作者平台")
    
    def log_login_success(self) -> None:
        """记录登录成功"""
        self.info("登录成功")
    
    def log_login_failure(self, error_msg: str) -> None:
        """
        记录登录失败
        
        Args:
            error_msg: 错误消息
        """
        self.error(f"登录失败: {error_msg}")
    
    def get_log_file_path(self) -> Optional[str]:
        """
        获取当前日志文件路径
        
        Returns:
            日志文件路径或None
        """
        if self.logger and self.logger.handlers:
            for handler in self.logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    return handler.baseFilename
        return None
    
    def close(self) -> None:
        """关闭日志记录器"""
        if self.logger:
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)


# 全局日志实例
_global_logger = None


def get_logger() -> Logger:
    """
    获取全局日志实例
    
    Returns:
        日志实例
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger()
    return _global_logger


def setup_logger(log_dir: str = "logs", log_level: int = logging.INFO) -> Logger:
    """
    设置全局日志实例
    
    Args:
        log_dir: 日志目录
        log_level: 日志级别
        
    Returns:
        日志实例
    """
    global _global_logger
    _global_logger = Logger(log_dir, log_level)
    return _global_logger
