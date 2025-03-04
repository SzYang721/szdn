# 数据库时序数据加载模块
import pandas as pd
from abc import ABC, abstractmethod

class BaseDatabaseConnector(ABC):
    """数据库连接基类"""
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
    
    @abstractmethod
    def get_time_series(self, query):
        """获取时序数据"""
        pass

class MySQLTimeSeriesLoader(BaseDatabaseConnector):
    """MySQL时序数据加载实现"""
    def __init__(self, host, port, user, password, database=None):
        super().__init__(host, port, user, password, database)
        self.connection = None
    
    def __enter__(self):
        import pymysql
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self
    
    def get_time_series(self, query):
        return pd.read_sql(query, self.connection)
    
    def get_coal_data(self, query):
        return pd.read_sql(query, self.connection)
    
    def get_weather_data(self, query):
        return pd.read_sql(query, self.connection)
    
    def get_electricity_data(self, query):
        return pd.read_sql(query, self.connection)
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.close()