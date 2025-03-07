import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, Dict, Any, Union

def setup_logger(
    name: Optional[str] = None,
    log_file: Optional[str] = None,
    level: Union[int, str] = logging.INFO,
    format_str: Optional[str] = None,
    rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    console: bool = True
) -> logging.Logger:
    """
    设置日志记录器
    
    参数:
    name (str, optional): 日志记录器名称，默认为root
    log_file (str, optional): 日志文件路径，如果为None则不记录到文件
    level (int/str): 日志级别，可以是logging模块的常量或字符串
    format_str (str, optional): 日志格式字符串，默认为'%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    rotation (bool): 是否使用滚动日志文件
    max_bytes (int): 单个日志文件的最大字节数
    backup_count (int): 保留的备份文件数量
    console (bool): 是否输出到控制台
    
    返回:
    logging.Logger: 日志记录器
    
    示例:
    logger = setup_logger('my_app', 'logs/app.log')
    logger.info('应用启动')
    """
    # 处理日志级别
    if isinstance(level, str):
        level = getattr(logging, level.upper())
    
    # 设置默认格式
    if format_str is None:
        format_str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 创建格式化器
    formatter = logging.Formatter(format_str)
    
    # 获取日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 清除现有的处理器
    logger.handlers = []
    
    # 添加文件处理器
    if log_file:
        # 确保日志目录存在
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        if rotation:
            file_handler = RotatingFileHandler(
                log_file, maxBytes=max_bytes, backupCount=backup_count
            )
        else:
            file_handler = logging.FileHandler(log_file)
        
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # 添加控制台处理器
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger

def get_log_level(level_name: str) -> int:
    """
    获取日志级别常量
    
    参数:
    level_name (str): 日志级别名称，如 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
    
    返回:
    int: 日志级别常量
    """
    return getattr(logging, level_name.upper())

def log_exception(logger: logging.Logger, exc: Exception, 
                 message: str = "发生异常", level: str = "ERROR") -> None:
    """
    记录异常信息
    
    参数:
    logger (logging.Logger): 日志记录器
    exc (Exception): 异常对象
    message (str): 日志消息
    level (str): 日志级别
    """
    log_method = getattr(logger, level.lower())
    log_method(f"{message}: {type(exc).__name__}: {str(exc)}", exc_info=True)

class LoggerAdapter(logging.LoggerAdapter):
    """
    日志适配器，用于添加上下文信息
    
    示例:
    logger = setup_logger('my_app')
    adapter = LoggerAdapter(logger, {'user_id': '12345'})
    adapter.info('用户登录')  # 输出: ... - 用户登录 [user_id=12345]
    """
    
    def process(self, msg, kwargs):
        extra = kwargs.get('extra', {})
        extra.update(self.extra)
        kwargs['extra'] = extra
        
        if extra:
            context = ' '.join(f"[{k}={v}]" for k, v in extra.items())
            msg = f"{msg} {context}"
        
        return msg, kwargs 