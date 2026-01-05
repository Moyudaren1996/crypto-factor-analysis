"""
Oscillator指标 - Williams %R (威廉指标)

因子描述:
    威廉指标，衡量超买超卖的动量指标

参数:
    length: 6 (30分钟)

计算公式:
    highest_high = high.rolling(length).max()
    lowest_low = low.rolling(length).min()
    Williams %R = -100 * (highest_high - close) / (highest_high - lowest_low)

输出:
    因子值DataFrame (-100到0)

数据依赖:
    - high, low, close

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Williams %R因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    high = data['high']
    low = data['low']
    close = data['close']

    length = 6

    # 计算最高价和最低价
    highest_high = high.rolling(window=length).max()
    lowest_low = low.rolling(window=length).min()

    # 计算Williams %R
    willr = -100 * (highest_high - close) / (highest_high - lowest_low)

    return willr
