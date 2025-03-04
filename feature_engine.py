# 特征工程模块
from sklearn.preprocessing import StandardScaler

class FeatureEngineer:
    """时序特征工程处理器"""
    def __init__(self, window_size=7, lag_steps=3):
        self.window_size = window_size
        self.lag_steps = lag_steps
        self.scaler = StandardScaler()
    
    def create_features(self, df, target_col):
        """创建时序特征"""
        # 时间特征
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        # 滑动窗口特征
        df['rolling_mean'] = df[target_col].rolling(self.window_size).mean()
        df['rolling_std'] = df[target_col].rolling(self.window_size).std()
        
        # 滞后特征
        for lag in range(1, self.lag_steps+1):
            df[f'lag_{lag}'] = df[target_col].shift(lag)
        
        # 处理缺失值
        df = df.dropna()
        return df
    
    def normalize(self, df):
        """数据标准化"""
        return pd.DataFrame(self.scaler.fit_transform(df), columns=df.columns)