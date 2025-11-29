"""
动量因子 (Momentum Factor)
计算过去N期的价格收益率作为因子值
"""

import pandas as pd


def calculate(data):
    """
    计算动量因子

    Args:
        data: 字典包含 'open', 'high', 'low', 'close', 'volume'
              每个key对应DataFrame (index=datetime, columns=symbols)

    Returns:
        factor_values: 因子值DataFrame (index=datetime, columns=symbols)
    """
    # 获取收盘价
    close = data['close']

    # 计算过去20期的收益率作为动量因子
    # 动量因子假设：过去表现好的资产未来仍会表现好
    momentum = close.pct_change(20)

    return momentum
