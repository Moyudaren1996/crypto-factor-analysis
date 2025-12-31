"""
Oscillator指标 - High-Low Extreme Reversal

因子描述:
    基于价格在高低区间极端位置的反转因子。当收盘价处于N期高低价的极端位置(>80%或<20%)
    且成交量出现异常衰弱信号时,预示假突破后的均值回归反转。结合K线形态识别上下影线过长
    的形态,提高反转信号的可靠性。

参数:
    lookback: 12 (1小时)

计算公式:
    1. 计算价格在N期高低区间的相对位置 (Stochastic)
    2. 识别极端位置 (>0.8或<0.2)
    3. 计算成交量相对强度偏离
    4. 识别K线上下影线极长的形态
    5. 组合三个信号作为最终因子

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - open: 开盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算High-Low Extreme Reversal因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    high = data['high']
    low = data['low']
    open_price = data['open']
    volume = data['volume']

    # 定义参数
    lookback = 12  # 1小时

    # 1. 计算价格在N期高低区间的位置 (Stochastic %K)
    high_n = high.rolling(lookback).max()
    low_n = low.rolling(lookback).min()
    stoch_k = (close - low_n) / (high_n - low_n + 1e-10)

    # 2. 识别极端价格位置
    extreme_high = (stoch_k > 0.8).astype(float)  # 价格极高
    extreme_low = (stoch_k < 0.2).astype(float)   # 价格极低

    # 3. 计算成交量相对强度
    volume_sma = volume.rolling(lookback).mean()
    volume_strength = volume / (volume_sma + 1e-10)

    # 成交量衰弱信号: volume_strength < 中位数
    volume_weak = (volume_strength < volume_strength.rolling(lookback).median()).astype(float)

    # 4. 识别K线上下影线形态
    # 上影线长度 = (high - close) / (high - low)
    # 下影线长度 = (close - low) / (high - low)
    range_hl = high - low + 1e-10
    upper_shadow = (high - close) / range_hl
    lower_shadow = (close - low) / range_hl

    # 极长上影线 + 价格极高 = 空头反转信号
    # 极长下影线 + 价格极低 = 多头反转信号
    long_upper_shadow = (upper_shadow > upper_shadow.rolling(lookback).quantile(0.75)).astype(float)
    long_lower_shadow = (lower_shadow > lower_shadow.rolling(lookback).quantile(0.75)).astype(float)

    # 5. 组合因子
    # 多头反转: 价格极低 + 成交量衰弱 + 下影线长
    bullish_reversal = extreme_low * volume_weak * long_lower_shadow

    # 空头反转: 价格极高 + 成交量衰弱 + 上影线长
    bearish_reversal = extreme_high * volume_weak * long_upper_shadow

    # 最终因子值
    factor = bullish_reversal - bearish_reversal

    # 6. 加强信号：乘以相对成交量强度的倒数（成交量越弱，信号越强）
    volume_intensity = 1 / (volume_strength.clip(lower=0.1, upper=10) + 1e-10)
    factor_weighted = factor * volume_intensity

    # 7. 滚动标准化 (Z-score on rolling window)
    factor_mean = factor_weighted.rolling(lookback).mean()
    factor_std = factor_weighted.rolling(lookback).std()
    factor_normalized = (factor_weighted - factor_mean) / (factor_std + 1e-10)

    # 处理异常值
    factor_final = factor_normalized.clip(-3, 3)

    return factor_final
