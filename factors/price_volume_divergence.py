"""
量价背离因子
价格上涨但成交量下跌（负向背离）
"""

def calculate(data):
    close = data['close']
    volume = data['volume']

    # 价格变化
    price_change = close.pct_change(5)
    # 成交量变化
    volume_change = volume.pct_change(5)

    # 背离 = 价格变化 * (-成交量变化)
    # 价格涨、成交量跌时为正
    divergence = price_change * (-volume_change)
    return divergence
