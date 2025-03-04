# 验证模块
from sklearn.model_selection import TimeSeriesSplit
import logging

class TimeSeriesValidator:
    def __init__(self, n_splits=5):
        self.n_splits = n_splits
        self.logger = logging.getLogger(__name__)
    
    def cross_validate(self, model, X, y):
        tscv = TimeSeriesSplit(n_splits=self.n_splits)
        results = []
        
        for train_index, test_index in tscv.split(X):
            X_train, X_test = X.iloc[train_index], X.iloc[test_index]
            y_train, y_test = y.iloc[train_index], y.iloc[test_index]
            
            model.train(X_train, y_train)
            metrics = model.evaluate(X_test, y_test)
            results.append(metrics)
            self.logger.info(f"Fold metrics: {metrics}")
        
        return results