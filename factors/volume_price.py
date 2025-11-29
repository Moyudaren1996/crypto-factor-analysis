"""
量价因子 (Volume-Price Factor)
结合成交量和价格变化的复合因子
"""

import pandas as pd


def calculate(data):
    """
    计算量价因子

    Args:
        data: 字典包含 'open', 'high', 'low', 'close', 'volume'
              每个key对应DataFrame (index=datetime, columns=symbols)

    Returns:
        factor_values: 因子值DataFrame (index=datetime, columns=symbols)
    """
    # 获取收盘价和成交量
    close = data['close']
    volume = data['volume']

    # 计算价格变化率（过去10期）
    price_change = close.pct_change(10)

    # 计算成交量相对值（当前成交量 / 过去10期平均成交量）
    volume_ma = volume.rolling(10).mean()
    volume_ratio = volume / volume_ma

    # 量价因子 = 价格变化率 × 成交量相对值
    # 理念：价格上涨且伴随成交量放大，表示上涨动能强
    factor = price_change * volume_ratio

    return factor
