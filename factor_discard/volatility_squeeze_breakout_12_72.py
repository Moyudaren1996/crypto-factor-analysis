"""
波动率指标 - Volatility Squeeze Breakout (波动率压缩突破)

因子描述:
    基于波动率压缩效应设计的趋势延续因子。核心原理：
    当波动率极度收缩后突然扩张时，通常预示着趋势的开始，
    价格倾向于朝当前方向继续运动。

    本因子直接使用波动率水平与价格位置的组合：
    1. 计算ATR相对于其历史均值的比率(波动率水平)
    2. 计算价格在最近N期高低区间内的相对位置
    3. 当波动率低于均值时(压缩状态)，取价格位置的负值(反转预期)
    4. 当波动率高于均值时(扩张状态)，取价格位置的正值(趋势延续)

参数:
    atr_period: 12 (1小时, ATR计算周期)
    lookback: 72 (6小时, 历史均值回溯窗口)

计算公式:
    tr = max(high-low, abs(high-prev_close), abs(low-prev_close))
    atr = tr.rolling(atr_period).mean()
    atr_mean = atr.rolling(lookback).mean()
    atr_ratio = atr / atr_mean  # 波动率水平

    highest = high.rolling(lookback).max()
    lowest = low.rolling(lookback).min()
    price_position = (close - lowest) / (highest - lowest)  # 0到1之间

    # 将价格位置转换为-1到1
    price_signal = (price_position - 0.5) * 2

    # 波动率压缩时反转，扩张时趋势延续
    factor = price_signal * (atr_ratio - 1)

输出:
    因子值DataFrame，正值预期上涨，负值预期下跌

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Volatility Squeeze Breakout因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    atr_period = 12   # 1小时
    lookback = 72     # 6小时

    # 计算真实波幅 (True Range)
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    # 计算TR最大值
    tr = tr1.copy()
    tr = tr.where(tr >= tr2, tr2)
    tr = tr.where(tr >= tr3, tr3)

    # 计算ATR
    atr = tr.rolling(atr_period).mean()

    # 计算ATR的历史均值
    atr_mean = atr.rolling(lookback).mean()

    # 波动率比率 (>1表示扩张, <1表示压缩)
    atr_ratio = atr / atr_mean

    # 计算价格在历史区间内的相对位置
    highest = high.rolling(lookback).max()
    lowest = low.rolling(lookback).min()
    price_range = highest - lowest
    price_position = (close - lowest) / price_range.replace(0, np.nan)

    # 将价格位置转换为-1到1的信号
    price_signal = (price_position - 0.5) * 2

    # 因子值：价格信号 × (波动率比率 - 1)
    # 压缩状态(ratio<1): 因子方向与价格位置相反 → 反转预期
    # 扩张状态(ratio>1): 因子方向与价格位置相同 → 趋势延续
    factor = price_signal * (atr_ratio - 1)

    return factor
