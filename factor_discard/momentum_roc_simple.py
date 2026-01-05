"""
Momentum指标 - ROC (不使用pandas_ta)

因子描述:
    使用pandas直接计算的ROC技术指标

参数:
    length: 6 (30分钟)

输出:
    标准化因子值
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
    results = {}

    for symbol in data['close'].columns:
        close = data['close'][symbol]
        # ROC = (当前价格 - N期前价格) / N期前价格
        roc = (close - close.shift(6)) / close.shift(6)
        results[symbol] = roc

    return pd.DataFrame(results)
