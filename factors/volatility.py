"""
波动率因子 (Volatility Factor)
使用历史波动率作为因子
"""

import pandas as pd


def calculate(data):
    """
    计算波动率因子

    Args:
        data: 字典包含 'open', 'high', 'low', 'close', 'volume'
              每个key对应DataFrame (index=datetime, columns=symbols)

    Returns:
        factor_values: 因子值DataFrame (index=datetime, columns=symbols)
    """
    # 获取收盘价
    close = data['close']

    # 计算过去20期的收益率标准差（波动率）
    returns = close.pct_change()
    volatility = returns.rolling(20).std()

    # 波动率因子：历史波动率越高的资产可能风险越大
    return volatility
