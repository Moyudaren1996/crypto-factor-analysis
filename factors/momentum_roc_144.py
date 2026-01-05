"""
Momentum指标 - ROC (Rate of Change)

因子描述:
    价格变化率，计算当前价格相对于N期前价格的百分比变化

参数:
    length: 144 (12小时)

计算公式:
    ROC = (close - close.shift(length)) / close.shift(length) * 100

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算ROC因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    length = 144

    # ROC = (当前价格 - N期前价格) / N期前价格 * 100
    roc = (close - close.shift(length)) / close.shift(length) * 100

    return roc
