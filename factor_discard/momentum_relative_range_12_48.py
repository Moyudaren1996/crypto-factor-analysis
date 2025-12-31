"""
Momentum指标 - Relative Range Position (相对区间位置动量)

因子描述:
    相对区间位置动量因子,衡量收盘价在短期和长期高低区间内的相对位置差异。
    核心逻辑:
    1. 计算收盘价在短期(12期)高低区间的相对位置 (0-1)
    2. 计算收盘价在长期(48期)高低区间的相对位置 (0-1)
    3. 两者之差表示短期动量相对于长期的"超前"或"落后"程度
    4. 当短期位置远高于长期时,表示短期过度上涨,存在反转机会

    与StochasticK不同的是:
    - 本因子关注的是多时间尺度位置的"差异"
    - 用成交量变化对信号进行加权调整

参数:
    short_period: 12 (1小时)
    long_period: 48 (4小时)

计算公式:
    pos_short = (close - low_12) / (high_12 - low_12)
    pos_long = (close - low_48) / (high_48 - low_48)
    raw_factor = pos_short - pos_long
    vol_change = volume / volume.rolling(long_period).mean()
    factor = raw_factor * np.log1p(vol_change)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算相对区间位置动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']

    # 定义参数
    short_period = 12   # 1小时
    long_period = 48    # 4小时
    epsilon = 1e-10

    # 计算短期高低点
    high_short = high.rolling(short_period).max()
    low_short = low.rolling(short_period).min()
    range_short = high_short - low_short + epsilon

    # 计算长期高低点
    high_long = high.rolling(long_period).max()
    low_long = low.rolling(long_period).min()
    range_long = high_long - low_long + epsilon

    # 计算价格在两个区间内的相对位置 (0-1)
    pos_short = (close - low_short) / range_short
    pos_long = (close - low_long) / range_long

    # 位置差异:正值表示短期位置高于长期,价格可能过热
    pos_diff = pos_short - pos_long

    # 成交量变化作为权重
    vol_ma = volume.rolling(long_period).mean()
    vol_ratio = volume / (vol_ma + epsilon)
    vol_weight = np.log1p(vol_ratio.clip(0.1, 10))

    # 综合因子
    raw_factor = pos_diff * vol_weight

    # 使用滚动Z-score标准化
    factor_mean = raw_factor.rolling(long_period).mean()
    factor_std = raw_factor.rolling(long_period).std()
    factor = (raw_factor - factor_mean) / (factor_std + epsilon)

    # 截断极端值
    factor = factor.clip(-5, 5)

    return factor
