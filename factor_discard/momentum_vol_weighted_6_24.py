"""
Momentum指标 - 成交量加权动量强度反转

因子描述:
    基于成交量确认的动量反转因子。结合价格动量强度和成交量变化，
    识别高成交量支撑的动量过度时的反转机会。当价格动量处于极端
    且成交量相对萎缩时，预示反转信号。

参数:
    momentum_period: 3 (15分钟)
    volume_period: 24 (2小时成交量周期)

计算公式:
    momentum = (close - close[t-3]) / close[t-3]
    volume_ratio = volume / volume[t-24:t].mean()
    vol_weighted_mom = momentum * volume_ratio
    factor = vol_weighted_mom的Z-score

输出:
    因子值DataFrame，标准化后的无量纲值

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量加权动量强度反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    momentum_period = 3
    volume_period = 24
    standardize_window = 36

    # 计算动量
    momentum = (close - close.shift(momentum_period)) / close.shift(momentum_period)

    # 计算成交量的移动平均
    avg_volume = volume.rolling(window=volume_period).mean()

    # 成交量比率
    volume_ratio = volume / (avg_volume + 1e-6)

    # 成交量加权的动量
    vol_weighted_mom = momentum * volume_ratio

    # 对动量进行标准化，使用滚动Z-score
    mom_mean = vol_weighted_mom.rolling(window=standardize_window).mean()
    mom_std = vol_weighted_mom.rolling(window=standardize_window).std()

    # 避免除以零
    mom_std = mom_std.replace(0, np.nan)

    # Z-score标准化
    factor = (vol_weighted_mom - mom_mean) / (mom_std + 1e-6)

    return factor
