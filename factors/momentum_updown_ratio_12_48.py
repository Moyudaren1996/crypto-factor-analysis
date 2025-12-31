"""
Momentum指标 - UpDownRatio (上下动量比率)

因子描述:
    上下动量比率因子,衡量一段时间内上涨动量与下跌动量的相对强度。
    计算滚动窗口内正收益绝对值之和与负收益绝对值之和的比率对数。
    当比率为正表示上涨动量占优,为负表示下跌动量占优。

    核心思想:不是看价格偏离均线,而是直接衡量上涨下跌力量的不平衡程度。
    这与RSI类似但计算方式不同:RSI用EMA平滑,本因子用简单求和。
    为避免与RSI相关性过高,使用短期与长期比率的差值作为最终因子。

参数:
    short_period: 12 (1小时,短期窗口)
    long_period: 48 (4小时,长期窗口)

计算公式:
    1. returns = close.pct_change() - 计算收益率
    2. pos_sum_short = sum(max(returns, 0), short_period) - 短期正收益之和
    3. neg_sum_short = sum(abs(min(returns, 0)), short_period) - 短期负收益绝对值之和
    4. ratio_short = log(pos_sum_short / neg_sum_short) - 短期比率对数
    5. ratio_long 同理计算长期
    6. factor = ratio_short - ratio_long - 短期与长期比率的差值

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算UpDownRatio因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 12  # 1小时
    long_period = 48   # 4小时

    # 计算收益率
    returns = close.pct_change()

    # 分离正负收益
    pos_returns = returns.clip(lower=0)
    neg_returns = (-returns).clip(lower=0)  # 取绝对值

    # 计算滚动求和
    pos_sum_short = pos_returns.rolling(window=short_period, min_periods=short_period).sum()
    neg_sum_short = neg_returns.rolling(window=short_period, min_periods=short_period).sum()

    pos_sum_long = pos_returns.rolling(window=long_period, min_periods=long_period).sum()
    neg_sum_long = neg_returns.rolling(window=long_period, min_periods=long_period).sum()

    # 避免除以0,添加小量
    epsilon = 1e-10

    # 计算比率对数
    ratio_short = np.log((pos_sum_short + epsilon) / (neg_sum_short + epsilon))
    ratio_long = np.log((pos_sum_long + epsilon) / (neg_sum_long + epsilon))

    # 最终因子 = 短期比率 - 长期比率
    # 当短期上涨动量相对强于长期时,因子为正
    factor = ratio_short - ratio_long

    return factor
