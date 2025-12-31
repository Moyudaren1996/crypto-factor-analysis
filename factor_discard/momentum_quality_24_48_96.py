"""
Momentum指标 - MomentumQuality (动量质量)

因子描述:
    动量质量因子，衡量动量信号的质量（稳定性）而非仅仅是强度。
    核心思想：
    1. 计算累积动量（多个周期收益率的累加）
    2. 计算动量的波动性（收益率的滚动标准差）
    3. 用累积动量除以波动性，类似于动量的Sharpe Ratio
    4. 高值表示持续稳定的上涨/下跌，低值表示波动剧烈方向不明

    这与简单动量因子不同，因为它关注的是动量的"质量"而非"数量"。

参数:
    sum_period: 24 (2小时，累积动量窗口)
    vol_period: 48 (4小时，波动率计算窗口)

计算公式:
    1. returns = pct_change(close, 1)
    2. cum_return = rolling_sum(returns, sum_period)
    3. volatility = rolling_std(returns, vol_period)
    4. factor = cum_return / volatility

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
    计算MomentumQuality因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    sum_period = 24      # 累积动量窗口 (2小时)
    vol_period = 48      # 波动率窗口 (4小时)

    # 计算单根K线收益率
    returns = close.pct_change(1)

    # 计算累积收益率（近N期收益率之和）
    cum_return = returns.rolling(sum_period).sum()

    # 计算收益率波动率
    volatility = returns.rolling(vol_period).std()
    volatility = volatility.replace(0, np.nan)

    # 动量质量 = 累积收益 / 波动率 (类似于Sharpe Ratio)
    momentum_quality = cum_return / volatility

    # 用时序排名转化为百分位，使因子在[-0.5, 0.5]范围内
    rank_period = 96  # 8小时
    factor = momentum_quality.rolling(rank_period).rank(pct=True) - 0.5

    return factor
