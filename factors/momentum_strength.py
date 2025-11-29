"""
动量强度因子
上涨期数 vs 下跌期数的比率
"""

def calculate(data):
    close = data['close']

    # 计算收益率
    returns = close.pct_change()

    # 过去20期中上涨的次数
    up_counts = (returns > 0).rolling(20).sum()
    # 过去20期中下跌的次数
    down_counts = (returns < 0).rolling(20).sum()

    # 上涨强度 = 上涨次数 / 下跌次数
    momentum_strength = up_counts / (down_counts + 1)

    return momentum_strength
