"""
成交量加权收益因子
用成交量加权的价格变化
"""

def calculate(data):
    close = data['close']
    volume = data['volume']

    # 收益率
    returns = close.pct_change()
    # 成交量权重（标准化）
    vol_weight = volume / volume.rolling(20).mean()

    # 成交量加权收益
    vol_weighted_return = returns * vol_weight
    return vol_weighted_return.rolling(10).mean()
