"""
Volatility指标 - Volume Weighted Range Ratio (成交量加权波幅比率)

因子描述:
    该因子衡量简单平均波幅与成交量加权平均波幅的比率。
    VWRange = Sum(Range * Volume) / Sum(Volume)
    SimpleRange = Mean(Range)
    Ratio = SimpleRange / VWRange
    
    通常，高波幅伴随高成交量（健康市场）。此时VWRange > SimpleRange，Ratio < 1。
    如果Ratio上升（>1 或接近1），意味着波幅大但成交量小（流动性枯竭/假突破），
    或者成交量大但波幅小（分歧/吸筹）。
    
    该因子捕捉价格波动与成交量的背离关系。

参数:
    period: 48 (4小时)

计算公式:
    range = high - low
    simple_range = range.rolling(period).mean()
    vw_range = (range * volume).rolling(period).sum() / volume.rolling(period).sum()
    factor = simple_range / vw_range

输出:
    因子值DataFrame

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2024-05-22
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量加权波幅比率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    high = data['high']
    low = data['low']
    volume = data['volume']
    period = 48

    # 计算波幅
    price_range = high - low
    
    # 计算简单移动平均波幅
    simple_range = price_range.rolling(window=period).mean()
    
    # 计算成交量加权移动平均波幅
    # 避免volume和为0
    vol_sum = volume.rolling(window=period).sum()
    weighted_range_sum = (price_range * volume).rolling(window=period).sum()
    
    vw_range = weighted_range_sum / vol_sum
    
    # 计算比率
    # 避免分母为0
    factor = simple_range / vw_range
    
    # 处理可能的无限值
    factor = factor.replace([np.inf, -np.inf], np.nan)
    
    return factor
