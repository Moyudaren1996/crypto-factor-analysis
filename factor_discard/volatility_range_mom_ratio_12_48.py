"""
Volatility指标 - RangeMomRatio (波幅动量比率因子)

因子描述:
    衡量价格动量与波幅变化之间的关系。
    当价格动量强但波幅扩张速度相对慢时，趋势可能具有可持续性；
    当波幅快速扩张但价格动量不强时，可能是过度波动或假突破。

    核心逻辑：
    1. 计算价格动量的强度（收益率/历史波动率，即Z-score）
    2. 计算波幅的变化速度（当前波幅/过去波幅）
    3. 计算价格动量强度与波幅变化速度的差值
    4. 差值为正说明价格动量强而波幅变化慢，预示趋势延续
    5. 差值为负说明波幅扩张快而价格动量弱，预示反转

参数:
    short_period: 12 (1小时，短期窗口)
    long_period: 48 (4小时，长期窗口)

计算公式:
    returns = close.pct_change(short_period)
    volatility = returns.rolling(long_period).std()

    # 价格动量Z-score
    price_zscore = returns / (volatility + 1e-10)

    # 波幅变化率（用高低价范围）
    hl_range = (high - low) / close
    range_short = hl_range.rolling(short_period).mean()
    range_long = hl_range.rolling(long_period).mean()
    range_ratio = range_short / range_long

    # 波幅变化率的Z-score
    range_ratio_mean = range_ratio.rolling(long_period).mean()
    range_ratio_std = range_ratio.rolling(long_period).std()
    range_zscore = (range_ratio - range_ratio_mean) / (range_ratio_std + 1e-10)

    # 因子：价格动量强度 - 波幅变化强度
    # 正值表示动量强于波幅变化，负值表示波幅变化强于动量
    factor_raw = price_zscore - range_zscore

    # 转换为时序百分位排名
    factor = factor_raw.rolling(long_period).rank(pct=True) - 0.5

输出:
    因子值DataFrame

数据依赖:
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
    计算RangeMomRatio因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 12   # 1小时
    long_period = 48    # 4小时

    # 价格收益率
    returns = close.pct_change(short_period)

    # 历史波动率
    ret_1 = close.pct_change()
    volatility = ret_1.rolling(long_period).std()

    # 价格动量Z-score
    price_zscore = returns / (volatility + 1e-10)

    # 波幅变化率（用高低价范围）
    hl_range = (high - low) / (close + 1e-10)
    range_short = hl_range.rolling(short_period).mean()
    range_long = hl_range.rolling(long_period).mean()
    range_ratio = range_short / (range_long + 1e-10)

    # 波幅变化率的Z-score
    range_ratio_mean = range_ratio.rolling(long_period).mean()
    range_ratio_std = range_ratio.rolling(long_period).std()
    range_zscore = (range_ratio - range_ratio_mean) / (range_ratio_std + 1e-10)

    # 限制极端值
    price_zscore = price_zscore.clip(-5, 5)
    range_zscore = range_zscore.clip(-5, 5)

    # 因子：价格动量强度 - 波幅变化强度
    factor_raw = price_zscore - range_zscore

    # 转换为时序百分位排名（-0.5到0.5）
    factor = factor_raw.rolling(long_period).rank(pct=True) - 0.5

    return factor
