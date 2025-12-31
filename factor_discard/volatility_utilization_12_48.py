"""
波动率指标 - 波动率利用率因子 (Volatility Utilization)

因子描述:
    衡量日内波动被有效利用的程度。计算收盘价变化相对于日内波幅(高低价差)
    的比率，结合成交量加权，识别波动被充分/未充分利用的状态。

    核心逻辑:
    1. 计算日内波幅利用率: |close - open| / (high - low)
    2. 利用率高说明日内波动沿一个方向有效推进(趋势性强)
    3. 利用率低说明日内波动被抵消(盘整/反转信号)
    4. 结合短期与中期利用率的差异识别状态变化
    5. 当短期利用率远高于中期，说明趋势可能过度延伸，预示反转

参数:
    short_period: 12 (1小时)
    long_period: 48 (4小时)
    lookback: 72 (用于Z-score标准化)

计算公式:
    utilization = |close - open| / (high - low + epsilon)
    short_util = EMA(utilization, short_period)
    long_util = EMA(utilization, long_period)
    util_diff = short_util - long_util
    util_zscore = (util_diff - rolling_mean) / rolling_std
    momentum_sign = sign(close - shift(close, 12))
    factor = util_zscore * momentum_sign  # 高利用率+正动量->反转做空

输出:
    因子值DataFrame，负向因子(做多低值组)

数据依赖:
    - open: 开盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率利用率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    open_price = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 12   # 短期EMA窗口
    long_period = 48    # 长期EMA窗口
    lookback = 72       # Z-score标准化窗口

    # 计算日内波幅
    range_hl = high - low
    # 避免除零
    range_hl = range_hl.replace(0, np.nan)

    # 计算日内波幅利用率: |close - open| / (high - low)
    body_size = (close - open_price).abs()
    utilization = body_size / range_hl

    # 计算短期和长期利用率的EMA
    short_util = utilization.ewm(span=short_period, adjust=False).mean()
    long_util = utilization.ewm(span=long_period, adjust=False).mean()

    # 计算利用率差异
    util_diff = short_util - long_util

    # Z-score标准化
    util_mean = util_diff.rolling(window=lookback).mean()
    util_std = util_diff.rolling(window=lookback).std()
    util_zscore = (util_diff - util_mean) / util_std

    # 计算价格动量方向
    momentum = close - close.shift(12)
    momentum_sign = np.sign(momentum)

    # 构建因子
    # 利用率突然提高(短期>长期)且动量为正 -> 趋势过度延伸 -> 预示反转下跌
    # 利用率突然提高且动量为负 -> 预示反转上涨
    factor = util_zscore * momentum_sign

    return factor
