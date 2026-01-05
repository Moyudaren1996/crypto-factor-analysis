"""
Oscillator指标 - Stochastic Oscillator (随机振荡器)

因子描述:
    随机振荡器，比较收盘价与一定时期内价格范围的关系

参数:
    k: 6, d: 3, smooth_k: 2

计算公式:
    lowest_low = low.rolling(k).min()
    highest_high = high.rolling(k).max()
    fast_k = 100 * (close - lowest_low) / (highest_high - lowest_low)
    slow_k = fast_k.rolling(smooth_k).mean()  (输出此值)
    slow_d = slow_k.rolling(d).mean()

输出:
    因子值DataFrame (slow_k, 0-100)

数据依赖:
    - high, low, close

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Stochastic Oscillator因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值 (slow_k)
    """
    high = data['high']
    low = data['low']
    close = data['close']

    k_period = 6
    d_period = 3
    smooth_k = 2

    # 计算最低价和最高价
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()

    # 计算Fast %K
    fast_k = 100 * (close - lowest_low) / (highest_high - lowest_low)

    # 计算Slow %K（平滑后的%K）
    slow_k = fast_k.rolling(window=smooth_k).mean()

    return slow_k
