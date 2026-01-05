"""
Volume指标 - MFI (Money Flow Index)

因子描述:
    资金流量指数，结合价格和成交量的动量指标

参数:
    length: 6 (30分钟)

计算公式:
    TP = (high + low + close) / 3
    Raw MF = TP * volume
    Positive MF = Sum(Raw MF where TP > TP.shift(1), length)
    Negative MF = Sum(Raw MF where TP < TP.shift(1), length)
    MFR = Positive MF / Negative MF
    MFI = 100 - (100 / (1 + MFR))

输出:
    因子值DataFrame (0-100)

数据依赖:
    - high, low, close, volume

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算MFI因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    high = data['high']
    low = data['low']
    close = data['close']
    volume = data['volume']

    length = 6

    # 计算Typical Price
    tp = (high + low + close) / 3

    # 计算Raw Money Flow
    raw_mf = tp * volume

    # 判断资金流向
    tp_diff = tp.diff()
    positive_mf = raw_mf.where(tp_diff > 0, 0)
    negative_mf = raw_mf.where(tp_diff < 0, 0)

    # 计算周期内正负资金流
    sum_positive = positive_mf.rolling(window=length).sum()
    sum_negative = negative_mf.rolling(window=length).sum()

    # 计算MFR和MFI
    mfr = sum_positive / sum_negative
    mfi = 100 - (100 / (1 + mfr))

    return mfi
