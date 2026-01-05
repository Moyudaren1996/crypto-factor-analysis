"""
Momentum指标 - TSI (True Strength Index)

因子描述:
    真实强度指数，使用双重平滑的动量指标

参数:
    long: 600, short: 300

计算公式:
    delta = close.diff()
    double_smoothed_pc = EMA(EMA(delta, short), long)
    double_smoothed_abs_pc = EMA(EMA(|delta|, short), long)
    TSI = 100 * double_smoothed_pc / double_smoothed_abs_pc

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
    计算TSI因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    long_period = 600
    short_period = 300

    # 计算价格变化
    delta = close.diff()

    # 双重EMA平滑
    pc_first_smooth = delta.ewm(span=short_period, adjust=False).mean()
    pc_double_smooth = pc_first_smooth.ewm(span=long_period, adjust=False).mean()

    # 对|delta|做同样的双重平滑
    abs_pc_first_smooth = delta.abs().ewm(span=short_period, adjust=False).mean()
    abs_pc_double_smooth = abs_pc_first_smooth.ewm(span=long_period, adjust=False).mean()

    # 计算TSI
    tsi = 100 * pc_double_smooth / abs_pc_double_smooth

    return tsi
