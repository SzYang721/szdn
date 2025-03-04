import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import sys
import os

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.time_series_model import TimeSeriesModel

def generate_sample_data(n=100):
    """生成示例时间序列数据"""
    np.random.seed(42)
    # 创建时间索引
    dates = pd.date_range(start='2020-01-01', periods=n, freq='D')
    
    # 创建趋势成分
    trend = np.linspace(0, 2, n)
    
    # 创建季节性成分
    seasonal = 0.5 * np.sin(np.linspace(0, 4*np.pi, n))
    
    # 创建噪声
    noise = 0.2 * np.random.randn(n)
    
    # 组合成时间序列
    y = trend + seasonal + noise
    
    # 创建特征矩阵（这里简单使用时间索引作为特征）
    X = np.arange(n).reshape(-1, 1)
    
    return X, y, dates

def main():
    # 生成示例数据
    X, y, dates = generate_sample_data(n=100)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    # 定义ARIMA模型参数
    arima_params = {
        'model_type': 'arima',
        'p': 2,  # 自回归阶数
        'd': 1,  # 差分阶数
        'q': 1   # 移动平均阶数
    }
    
    # 初始化并训练ARIMA模型
    arima_model = TimeSeriesModel(arima_params)
    arima_model.train(X_train, y_train)
    
    # 进行预测
    y_pred_arima = arima_model.predict(len(X_test))
    
    # 评估模型
    arima_metrics = arima_model.evaluate(X_test, y_test)
    print("ARIMA模型评估指标:")
    for metric, value in arima_metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # 定义指数平滑模型参数
    exp_params = {
        'model_type': 'exp_smoothing',
        'trend': 'add',           # 加法趋势
        'seasonal': 'add',        # 加法季节性
        'seasonal_periods': 7     # 季节周期（如每周）
    }
    
    # 初始化并训练指数平滑模型
    exp_model = TimeSeriesModel(exp_params)
    exp_model.train(X_train, y_train)
    
    # 进行预测
    y_pred_exp = exp_model.predict(len(X_test))
    
    # 评估模型
    exp_metrics = exp_model.evaluate(X_test, y_test)
    print("\n指数平滑模型评估指标:")
    for metric, value in exp_metrics.items():
        print(f"{metric}: {value:.4f}")
    
    # 可视化结果
    plt.figure(figsize=(12, 6))
    
    # 绘制训练数据
    train_dates = dates[:len(y_train)]
    plt.plot(train_dates, y_train, 'b-', label='训练数据')
    
    # 绘制测试数据
    test_dates = dates[len(y_train):len(y_train)+len(y_test)]
    plt.plot(test_dates, y_test, 'g-', label='测试数据')
    
    # 绘制ARIMA预测结果
    plt.plot(test_dates, y_pred_arima, 'r--', label='ARIMA预测')
    
    # 绘制指数平滑预测结果
    plt.plot(test_dates, y_pred_exp, 'm--', label='指数平滑预测')
    
    plt.title('时间序列预测对比')
    plt.xlabel('日期')
    plt.ylabel('值')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('time_series_prediction.png')
    plt.show()

if __name__ == "__main__":
    main() 