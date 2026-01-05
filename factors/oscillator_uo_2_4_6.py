"""
Oscillator指标 - Ultimate Oscillator (终极振荡器)

因子描述:
    终极振荡器，使用三个不同时间周期的加权平均来减少波动

参数:
    fast: 2, medium: 4, slow: 6

计算公式:
    BP = close - min(low, previous_close)
    TR = max(high, previous_close) - min(low, previous_close)
    Avg_fast = Sum(BP, fast) / Sum(TR, fast)
    Avg_medium = Sum(BP, medium) / Sum(TR, medium)
    Avg_slow = Sum(BP, slow) / Sum(TR, slow)
    UO = 100 * ((4 * Avg_fast) + (2 * Avg_medium) + Avg_slow) / 7

输出:
    因子值DataFrame (0-100)

数据依赖:
    - high, low, close

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Ultimate Oscillator因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    high = data['high']
    low = data['low']
    close = data['close']

    fast = 2
    medium = 4
    slow = 6

    # 前一期收盘价
    prev_close = close.shift(1)

    # Buying Pressure
    bp = close - pd.DataFrame(np.minimum(low.values, prev_close.values),
                               index=close.index, columns=close.columns)

    # True Range
    tr_high = pd.DataFrame(np.maximum(high.values, prev_close.values),
                            index=close.index, columns=close.columns)
    tr_low = pd.DataFrame(np.minimum(low.values, prev_close.values),
                           index=close.index, columns=close.columns)
    tr = tr_high - tr_low

    # 计算各周期平均值
    avg_fast = bp.rolling(window=fast).sum() / tr.rolling(window=fast).sum()
    avg_medium = bp.rolling(window=medium).sum() / tr.rolling(window=medium).sum()
    avg_slow = bp.rolling(window=slow).sum() / tr.rolling(window=slow).sum()

    # 计算UO
    uo = 100 * ((4 * avg_fast) + (2 * avg_medium) + avg_slow) / 7

    return uo
