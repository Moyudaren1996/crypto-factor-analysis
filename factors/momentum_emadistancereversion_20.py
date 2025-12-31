"""
Momentum指标 - EMADistanceReversion (EMA Distance Mean Reversion)

因子描述:
    基于价格与EMA距离的短期均值回归因子。
    完全不同于之前的方法：仅基于价格动量和EMA乖离。

参数:
    ema_period: 20
    lookback: 24

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    close = data['close']

    ema_period = 20
    lookback = 24

    # EMA指数移动平均
    ema = close.ewm(span=ema_period, adjust=False).mean()

    # 价格相对于EMA的偏离度（百分比）
    dev = (close - ema) / ema * 100

    # 计算偏离度的历史范围（用于标准化）
    dev_max = dev.rolling(lookback).max()
    dev_min = dev.rolling(lookback).min()
    dev_range = dev_max - dev_min
    dev_range = dev_range.where(dev_range != 0, 1)

    # 标准化偏离度至0-1范围
    dev_normalized = (dev - dev_min) / dev_range

    # 反转逻辑：
    # 价格偏离EMA过多（极端值）-> 预示回归
    # 极高偏离(>0.8) = 看跌反转信号
    # 极低偏离(<0.2) = 看涨反转信号

    extreme_high = (dev_normalized > 0.8).astype(float)  # 看跌
    extreme_low = (dev_normalized < 0.2).astype(float)   # 看涨

    factor = extreme_low - extreme_high

    # 平滑
    factor = factor.ewm(span=8, adjust=False).mean()
    factor = factor.fillna(0)

    return factor
