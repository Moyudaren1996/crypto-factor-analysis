"""
Volume指标 - CMF (Chaikin Money Flow)

因子描述:
    蔡金资金流量，衡量一段时间内资金流入流出的指标

参数:
    length: 3 (15分钟)

计算公式:
    MFM = ((close - low) - (high - close)) / (high - low)
    MFV = MFM * volume
    CMF = Sum(MFV, length) / Sum(volume, length)

输出:
    因子值DataFrame (-1到1)

数据依赖:
    - high, low, close, volume

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算CMF因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    high = data['high']
    low = data['low']
    close = data['close']
    volume = data['volume']

    length = 3

    # 计算Money Flow Multiplier
    mfm = ((close - low) - (high - close)) / (high - low)

    # 计算Money Flow Volume
    mfv = mfm * volume

    # 计算CMF
    cmf = mfv.rolling(window=length).sum() / volume.rolling(window=length).sum()

    return cmf
