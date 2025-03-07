import time
import functools
import logging
from typing import Callable, Any, Optional

def timer(func: Optional[Callable] = None, *, name: Optional[str] = None, 
          log_level: str = 'info', logger: Optional[logging.Logger] = None):
    """
    装饰器：计算函数运行时间
    
    参数:
    func (Callable, optional): 要装饰的函数
    name (str, optional): 自定义函数名称，默认使用函数的__name__
    log_level (str): 日志级别，可选 'debug', 'info', 'warning', 'error'
    logger (logging.Logger, optional): 自定义日志记录器，默认使用标准日志记录器
    
    返回:
    Callable: 装饰后的函数
    
    示例:
    @timer
    def slow_function():
        time.sleep(1)
        
    @timer(name="自定义名称", log_level="debug")
    def another_function():
        time.sleep(0.5)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_name = name or func.__name__
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                elapsed = end_time - start_time
                
                log_message = f"函数 '{func_name}' 运行时间: {elapsed:.4f} 秒"
                print(log_message)
                
                if logger:
                    if log_level == 'debug':
                        logger.debug(log_message)
                    elif log_level == 'warning':
                        logger.warning(log_message)
                    elif log_level == 'error':
                        logger.error(log_message)
                    else:
                        logger.info(log_message)
                else:
                    if log_level == 'debug':
                        logging.debug(log_message)
                    elif log_level == 'warning':
                        logging.warning(log_message)
                    elif log_level == 'error':
                        logging.error(log_message)
                    else:
                        logging.info(log_message)
                        
                return result
            except Exception as e:
                end_time = time.time()
                elapsed = end_time - start_time
                
                log_message = f"函数 '{func_name}' 运行出错，耗时: {elapsed:.4f} 秒，错误: {str(e)}"
                print(log_message)
                
                if logger:
                    logger.error(log_message)
                else:
                    logging.error(log_message)
                    
                raise
                
        return wrapper
    
    # 支持 @timer 和 @timer() 两种用法
    if func is None:
        return decorator
    return decorator(func)

def timed(name: Optional[str] = None, log_level: str = 'info', 
          logger: Optional[logging.Logger] = None):
    """
    上下文管理器：计算代码块运行时间
    
    参数:
    name (str, optional): 代码块名称，默认为"代码块"
    log_level (str): 日志级别，可选 'debug', 'info', 'warning', 'error'
    logger (logging.Logger, optional): 自定义日志记录器，默认使用标准日志记录器
    
    示例:
    with timed("数据处理"):
        process_data()
        
    with timed("文件读取", log_level="debug"):
        read_large_file()
    """
    class TimedContextManager:
        def __init__(self):
            self.block_name = name or "代码块"
            self.start_time = None
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            end_time = time.time()
            elapsed = end_time - self.start_time
            
            if exc_type is None:
                log_message = f"{self.block_name} 运行时间: {elapsed:.4f} 秒"
                
                if logger:
                    if log_level == 'debug':
                        logger.debug(log_message)
                    elif log_level == 'warning':
                        logger.warning(log_message)
                    elif log_level == 'error':
                        logger.error(log_message)
                    else:
                        logger.info(log_message)
                else:
                    if log_level == 'debug':
                        logging.debug(log_message)
                    elif log_level == 'warning':
                        logging.warning(log_message)
                    elif log_level == 'error':
                        logging.error(log_message)
                    else:
                        logging.info(log_message)
            else:
                log_message = f"{self.block_name} 运行出错，耗时: {elapsed:.4f} 秒，错误: {str(exc_val)}"
                
                if logger:
                    logger.error(log_message)
                else:
                    logging.error(log_message)
                    
            return False  # 不抑制异常
    
    return TimedContextManager() 

if __name__ == "__main__":
    @timer
    def slow_function():
        time.sleep(1)
        
    slow_function()