import os
import sys
# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录
parent_dir = os.path.dirname(current_dir)
# 将项目根目录添加到Python路径
sys.path.append(parent_dir)

from sqlalchemy import create_engine
import mysql.connector
import pandas as pd
from typing import List, Dict, Optional, Union
import logging
from datetime import datetime, timedelta
from configs.db_config import *
import asyncio
from concurrent.futures import ThreadPoolExecutor

class MySQLService:
    """MySQL数据库服务类，用于获取时间序列数据"""
    
    def __init__(self, host: str, user: str, password: str, database: str):
        """
        初始化MySQL服务
        
        参数:
        host (str): 数据库主机地址
        user (str): 数据库用户名
        password (str): 数据库密码
        database (str): 数据库名称
        """
        self.connection_params = {
            'host': host,
            'user': user,
            'password': password,
            'database': database
        }
        # 创建 SQLAlchemy 引擎
        self.engine = create_engine(
            f'mysql+pymysql://{user}:{password}@{host}/{database}'
        )
        self.connection = None
        self._connect()
        
    def _connect(self):
        """建立数据库连接"""
        try:
            self.connection = mysql.connector.connect(**self.connection_params)
            logging.info("Successfully connected to MySQL database")
        except mysql.connector.Error as err:
            logging.error(f"Error connecting to MySQL database: {err}")
            raise
    
    def _disconnect(self):
        """关闭数据库连接"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logging.info("MySQL connection closed")
            
    def get_table_data(self, table: str, where_conditions: Dict[str, str]) -> pd.DataFrame:
        """
        获取实时数据
        
        参数:
        table (str): 表名
        """
        try:
            query = f"SELECT * FROM {table}"
            if where_conditions:
                query += " WHERE " + " AND ".join([f"{k} = '{v}'" for k, v in where_conditions.items()])
            df = pd.read_sql(query, self.connection)
            return df
        except Exception as e:
            logging.error(f"Error fetching real-time data: {e}")
            raise
        
    def get_monthly_yearly_data(
        self,
        table: str,
        columns: List[str],
        time_column: str,
        current_month: bool = False,
        current_year: bool = False,
        where_conditions: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        获取当前月或当前年的数据
        
        参数:
        table (str): 表名
        columns (List[str]): 需要选取的列名列表
        time_column (str): 时间列名
        current_month (bool): 是否获取当前月数据
        current_year (bool): 是否获取当前年数据
        where_conditions (Dict[str, str], optional): 额外的WHERE条件字典
        
        返回:
        pd.DataFrame: 包含查询结果的DataFrame
        
        异常:
        ValueError: 如果表中没有指定的时间列
        """
        try:
            # 检查表中是否存在时间列
            check_query = f"SHOW COLUMNS FROM {table} LIKE '{time_column}'"
            cursor = self.connection.cursor()
            cursor.execute(check_query)
            if not cursor.fetchone():
                raise ValueError(f"时间列 '{time_column}' 在表 '{table}' 中不存在")
            
            # 构建查询语句
            columns_str = ", ".join(columns)
            query = f"SELECT {columns_str} FROM {table}"
            
            # 添加时间条件
            conditions = []
            now = datetime.now()
            
            if current_month:
                month_start = datetime(now.year, now.month, 1).strftime('%Y-%m-%d')
                next_month = now.month + 1 if now.month < 12 else 1
                next_year = now.year if now.month < 12 else now.year + 1
                month_end = datetime(next_year, next_month, 1).strftime('%Y-%m-%d')
                conditions.append(f"{time_column} >= '{month_start}' AND {time_column} < '{month_end}'")
            
            if current_year:
                year_start = datetime(now.year, 1, 1).strftime('%Y-%m-%d')
                year_end = datetime(now.year + 1, 1, 1).strftime('%Y-%m-%d')
                conditions.append(f"{time_column} >= '{year_start}' AND {time_column} < '{year_end}'")
            
            # 添加额外的WHERE条件
            if where_conditions:
                for col, value in where_conditions.items():
                    conditions.append(f"{col} = '{value}'")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # 执行查询
            df = pd.read_sql(query, self.engine)
            return df
            
        except mysql.connector.Error as err:
            logging.error(f"数据库查询错误: {err}")
            raise
        except Exception as e:
            logging.error(f"获取月度/年度数据时出错: {e}")
            raise
        
    def get_time_series_data(
        self,
        table: str,
        time_column: str,
        value_column: str,
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        group_by: Optional[str] = None,
        additional_columns: Optional[List[str]] = None,
        where_conditions: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        获取时间序列数据
        
        参数:
        table (str): 表名
        time_column (str): 时间列名
        value_column (str): 值列名
        start_time (str/datetime, optional): 开始时间
        end_time (str/datetime, optional): 结束时间
        group_by (str, optional): 分组列名
        additional_columns (List[str], optional): 额外的列名列表
        where_conditions (Dict[str, str], optional): WHERE条件字典
        
        返回:
        pd.DataFrame: 包含时间序列数据的DataFrame
        """
        try:
            # 构建查询语句
            query = f"SELECT {time_column}, {value_column}"
            
            # 添加额外的列
            if additional_columns:
                query += f", {', '.join(additional_columns)}"
            
            query += f" FROM {table}"
            
            # 添加WHERE条件
            conditions = []
            if start_time:
                conditions.append(f"{time_column} >= '{start_time}'")
            if end_time:
                conditions.append(f"{time_column} <= '{end_time}'")
            if where_conditions:
                for col, value in where_conditions.items():
                    conditions.append(f"{col} = '{value}'")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # 添加分组
            if group_by:
                query += f" GROUP BY {group_by}"
            
            # 按时间排序
            query += f" ORDER BY {time_column}"
            
            # 执行查询
            df = pd.read_sql(query, self.engine)
            
            # 确保时间列是datetime类型
            df[time_column] = pd.to_datetime(df[time_column])
            
            return df
            
        except Exception as e:
            logging.error(f"Error fetching time series data: {e}")
            raise
    
    def get_aggregated_data(
        self,
        table: str,
        time_column: str,
        value_column: str,
        aggregation: str = 'AVG',
        time_interval: str = '1D',
        start_time: Optional[Union[str, datetime]] = None,
        end_time: Optional[Union[str, datetime]] = None,
        where_conditions: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        获取聚合后的时间序列数据
        
        参数:
        table (str): 表名
        time_column (str): 时间列名
        value_column (str): 值列名
        aggregation (str): 聚合函数 ('AVG', 'SUM', 'MAX', 'MIN', 'COUNT')
        time_interval (str): 时间间隔 ('1D', '1H', '1W', '1M')
        start_time (str/datetime, optional): 开始时间
        end_time (str/datetime, optional): 结束时间
        where_conditions (Dict[str, str], optional): WHERE条件字典
        
        返回:
        pd.DataFrame: 包含聚合后时间序列数据的DataFrame
        """
        try:
            # 构建时间间隔表达式
            interval_expr = f"DATE_FORMAT({time_column}, '%Y-%m-%d %H:00:00')"
            if time_interval == '1H':
                interval_expr = f"DATE_FORMAT({time_column}, '%Y-%m-%d %H:00:00')"
            elif time_interval == '1D':
                interval_expr = f"DATE({time_column})"
            elif time_interval == '1W':
                interval_expr = f"DATE_SUB(DATE({time_column}), INTERVAL WEEKDAY({time_column}) DAY)"
            elif time_interval == '1M':
                interval_expr = f"DATE_FORMAT({time_column}, '%Y-%m-01')"
            
            # 构建查询语句
            query = f"""
                SELECT 
                    {interval_expr} as time_interval,
                    {aggregation}({value_column}) as value
                FROM {table}
            """
            
            # 添加WHERE条件
            conditions = []
            if start_time:
                conditions.append(f"{time_column} >= '{start_time}'")
            if end_time:
                conditions.append(f"{time_column} <= '{end_time}'")
            if where_conditions:
                for col, value in where_conditions.items():
                    conditions.append(f"{col} = '{value}'")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # 添加分组和排序
            query += f" GROUP BY time_interval ORDER BY time_interval"
            
            # 执行查询
            df = pd.read_sql(query, self.engine)
            
            # 确保时间列是datetime类型
            df['time_interval'] = pd.to_datetime(df['time_interval'])
            
            return df
            
        except Exception as e:
            logging.error(f"Error fetching aggregated data: {e}")
            raise
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self._disconnect()


if __name__ == "__main__":
    print("系统目录：",sys.path)
    
    # 测试数据库连接
    print("数据库连接...")
    mysql_service = MySQLService(
        host=MYSQL_IP,
        user=MYSQL_ACCOUNT,
        password=MYSQL_PASSWORD,
        database=MYSQL_DBNAME
    )
    
    # 测试获取月度/年度数据
    print("\n获取月度数据...")
    try:
        monthly_data = mysql_service.get_monthly_yearly_data(
            table="load_actual_running",
            columns=["日期", "时刻", "统调负荷", "省内B类电源", "西电东送电力", 
                     "省内A类电源","地方电源出力","粤港联络线"],
            time_column="日期", #检查是否是时间列
            current_month=True, #是否是当前月
            # where_conditions={"device_type": "heater"}
        )
        print(f"获取到 {len(monthly_data)} 条月度数据")
        print(monthly_data.head())
    except Exception as e:
        print(f"获取月度数据失败: {e}")
    
    