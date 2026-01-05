"""
Volatility指标 - Volume Adjusted Bar Strength

因子描述:
    计算成交量加权的K线实体与极差比率。
    Strength = ((Close - Open) / (High - Low)) * (Volume / MeanVolume)
    
    原始 Bar Strength 衡量价格运动的效率。
    引入相对成交量 (Relative Volume) 进行加权，强调成交量放大的K线信号。
    
    逻辑：
    - 高效的上涨K线（实体大）且成交量放大 -> 强买入信号
    - 高效的下跌K线（实体大）且成交量放大 -> 强卖出信号
    - 缩量K线信号被减弱
    
    预期效果：降低与纯价格效率因子（如RSI, PathEfficiency）的相关性，因为引入了Volume维度。

参数:
    window: 24 (2小时)

计算公式:
    Strength = (Close - Open) / (High - Low)
    VolRatio = Volume / Mean(Volume, window)
    Factor = Mean(Strength * VolRatio, window)

输出:
    因子值DataFrame (无固定范围，通常在 -2 到 2 之间)

数据依赖:
    - open, high, low, close, volume

创建日期: 2026-01-02
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算 Volume Adjusted Bar Strength 因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    open_price = data['open']
    high = data['high']
    low = data['low']
    close = data['close']
    volume = data['volume']
    
    window = 24
    
    # Range
    rng = high - low
    rng = rng.replace(0, np.nan)
    
    # Bar Strength
    strength = (close - open_price) / rng
    
    # Volume Ratio
    vol_mean = volume.rolling(window).mean()
    # Avoid division by zero
    vol_mean = vol_mean.replace(0, np.nan)
    vol_ratio = volume / vol_mean
    
    # Weighted Strength
    weighted_strength = strength * vol_ratio
    
    # Rolling Mean
    factor = weighted_strength.rolling(window).mean()
    
    return factor
