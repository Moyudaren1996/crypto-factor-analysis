"""
Price指标 - GapVolumeReversion (Gap-Volume Reversal)

因子描述:
    基于开盘跳空与成交量突增的反转因子。
    当价格出现大幅跳空但成交量滞后时,预示反转信号。

参数:
    gap_period: 12
    vol_period: 6

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']
    open_ = data['open']

    gap_period = 12
    vol_period = 6

    # 计算开盘跳空大小（相对前日收盘）
    gap = (open_ - close.shift(1)) / close.shift(1)
    gap = gap.fillna(0).replace([np.inf, -np.inf], 0)

    # 计算跳空的绝对值和方向
    gap_size = gap.abs()
    gap_direction = np.sign(gap)

    # 计算成交量与均值的比率
    vol_ma = volume.rolling(vol_period).mean()
    vol_ma = vol_ma.where(vol_ma != 0, 1)
    vol_ratio = volume / vol_ma

    # 计算价格距离（当前close相对于open）
    intraday_move = (close - open_) / (high - low + 1e-10)

    # 反转信号逻辑：
    # 1. 大幅跳空存在（>1% 分位数）
    # 2. 日内运动与跳空方向相反 = 反转信号
    # 3. 成交量低于正常 = 反转确认

    gap_size_q75 = gap_size.rolling(gap_period).quantile(0.75)
    gap_threshold = (gap_size > gap_size_q75).astype(float)

    # 日内反向运动：跳空向上但收盘在下方，或跳空向下但收盘在上方
    reversal_signal = gap_direction * (-intraday_move)  # 同向为负（反转）
    reversal_signal = (reversal_signal < 0).astype(float)

    # 成交量确认：成交量低
    vol_weak = (vol_ratio < 1.0).astype(float)

    # 综合反转信号
    factor = gap_threshold * reversal_signal * (0.5 + 0.5 * vol_weak)

    # 中心化
    factor = factor - 0.5

    # 平滑
    factor = factor.ewm(span=6, adjust=False).mean()
    factor = factor.fillna(0)

    return factor
