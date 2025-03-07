import os
import shutil
from datetime import datetime
from typing import Optional

def ensure_dir(directory: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    参数:
    directory (str): 目录路径
    
    返回:
    str: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    参数:
    file_path (str): 文件路径
    
    返回:
    str: 文件扩展名（包含点，如 '.xlsx'）
    """
    _, ext = os.path.splitext(file_path)
    return ext

def backup_file(file_path: str, backup_dir: Optional[str] = None, 
                suffix: Optional[str] = None) -> str:
    """
    备份文件
    
    参数:
    file_path (str): 要备份的文件路径
    backup_dir (str, optional): 备份目录，默认为文件所在目录
    suffix (str, optional): 备份文件名后缀，默认为时间戳
    
    返回:
    str: 备份文件路径
    
    示例:
    backup_file('/path/to/file.xlsx')  # 返回 '/path/to/file_20230101_120000.xlsx'
    backup_file('/path/to/file.xlsx', backup_dir='/backups')  # 返回 '/backups/file_20230101_120000.xlsx'
    backup_file('/path/to/file.xlsx', suffix='backup')  # 返回 '/path/to/file_backup.xlsx'
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    # 获取文件名和扩展名
    file_dir, file_name = os.path.split(file_path)
    name, ext = os.path.splitext(file_name)
    
    # 确定备份目录
    if backup_dir is None:
        backup_dir = file_dir
    else:
        ensure_dir(backup_dir)
    
    # 确定备份文件名后缀
    if suffix is None:
        suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 构建备份文件路径
    backup_name = f"{name}_{suffix}{ext}"
    backup_path = os.path.join(backup_dir, backup_name)
    
    # 复制文件
    shutil.copy2(file_path, backup_path)
    
    return backup_path

def safe_filename(filename: str) -> str:
    """
    将字符串转换为安全的文件名
    
    参数:
    filename (str): 原始文件名
    
    返回:
    str: 安全的文件名
    """
    # 替换不安全的字符
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename

def get_file_size(file_path: str, unit: str = 'MB') -> float:
    """
    获取文件大小
    
    参数:
    file_path (str): 文件路径
    unit (str): 单位，可选 'B', 'KB', 'MB', 'GB'
    
    返回:
    float: 文件大小
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    size_bytes = os.path.getsize(file_path)
    
    if unit.upper() == 'B':
        return size_bytes
    elif unit.upper() == 'KB':
        return size_bytes / 1024
    elif unit.upper() == 'MB':
        return size_bytes / (1024 * 1024)
    elif unit.upper() == 'GB':
        return size_bytes / (1024 * 1024 * 1024)
    else:
        raise ValueError(f"不支持的单位: {unit}，支持的单位有 'B', 'KB', 'MB', 'GB'")

def list_files(directory: str, pattern: Optional[str] = None, 
               recursive: bool = False) -> list:
    """
    列出目录中的文件
    
    参数:
    directory (str): 目录路径
    pattern (str, optional): 文件名模式，支持通配符，如 '*.xlsx'
    recursive (bool): 是否递归查找子目录
    
    返回:
    list: 文件路径列表
    """
    import fnmatch
    
    if not os.path.exists(directory):
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    result = []
    
    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                if pattern is None or fnmatch.fnmatch(file, pattern):
                    result.append(os.path.join(root, file))
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and (pattern is None or fnmatch.fnmatch(file, pattern)):
                result.append(file_path)
    
    return result 