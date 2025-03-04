import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.preprocessing import StandardScaler
from .base_model import BaseModel

class TimeSeriesModel(BaseModel):
    """时间序列模型类，支持ARIMA和指数平滑等常见时间序列模型"""
    
    def __init__(self, model_params):
        """
        初始化时间序列模型
        
        参数:
        model_params (dict): 模型参数字典，包含以下键:
            - model_type: 'arima' 或 'exp_smoothing'
            - 对于ARIMA: p, d, q 参数
            - 对于指数平滑: trend, seasonal, seasonal_periods 参数
        """
        super().__init__(model_params)
        self.model_type = model_params.get('model_type', 'arima')
        self.scaler = StandardScaler()
        
    def train(self, X_train, y_train):
        """
        训练时间序列模型
        
        参数:
        X_train: 训练特征数据，对于某些时间序列模型可能不使用
        y_train: 训练目标数据，时间序列值
        
        返回:
        self: 训练好的模型实例
        """
        # 对目标变量进行标准化
        y_scaled = self.scaler.fit_transform(y_train.reshape(-1, 1)).flatten()
        
        if self.model_type == 'arima':
            # 获取ARIMA参数
            p = self.model_params.get('p', 1)
            d = self.model_params.get('d', 1)
            q = self.model_params.get('q', 0)
            
            # 训练ARIMA模型
            self.model = ARIMA(y_scaled, order=(p, d, q))
            self.model = self.model.fit()
            
        elif self.model_type == 'exp_smoothing':
            # 获取指数平滑参数
            trend = self.model_params.get('trend', None)
            seasonal = self.model_params.get('seasonal', None)
            seasonal_periods = self.model_params.get('seasonal_periods', None)
            
            # 训练指数平滑模型
            self.model = ExponentialSmoothing(
                y_scaled,
                trend=trend,
                seasonal=seasonal,
                seasonal_periods=seasonal_periods
            )
            self.model = self.model.fit()
        
        return self
    
    def predict(self, X_test):
        """
        使用训练好的模型进行预测
        
        参数:
        X_test: 测试特征数据，包含预测步数信息
        
        返回:
        y_pred: 预测结果
        """
        if self.model is None:
            raise ValueError("模型尚未训练，请先调用train方法")
        
        # 获取预测步数
        steps = len(X_test) if hasattr(X_test, '__len__') else X_test
        
        if self.model_type == 'arima':
            # 使用ARIMA模型预测
            forecast = self.model.forecast(steps=steps)
            
        elif self.model_type == 'exp_smoothing':
            # 使用指数平滑模型预测
            forecast = self.model.forecast(steps=steps)
        
        # 将预测结果转换回原始尺度
        y_pred = self.scaler.inverse_transform(forecast.reshape(-1, 1)).flatten()
        
        return y_pred
    
    def evaluate(self, X_test, y_test):
        """
        评估模型性能
        
        参数:
        X_test: 测试特征数据
        y_test: 测试目标数据
        
        返回:
        metrics: 包含评估指标的字典
        """
        # 调用父类的evaluate方法
        metrics = super().evaluate(X_test, y_test)
        
        # 添加时间序列特有的评估指标
        y_pred = self.predict(X_test)
        
        # 计算平均绝对百分比误差(MAPE)
        mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
        metrics['mape'] = mape
        
        return metrics 