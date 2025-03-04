# 模型基类
from abc import ABC, abstractmethod
import numpy as np

class BaseModel(ABC):
    """模型基类"""
    def __init__(self, model_params):
        self.model = None
        self.model_params = model_params
    
    @abstractmethod
    def train(self, X_train, y_train):
        pass
    
    @abstractmethod
    def predict(self, X_test):
        pass
    
    def evaluate(self, X_test, y_test):
        y_pred = self.predict(X_test)
        return {
            'mae': np.mean(np.abs(y_pred - y_test)),
            'mse': np.mean((y_pred - y_test)**2),
            'rmse': np.sqrt(np.mean((y_pred - y_test)**2))
        }