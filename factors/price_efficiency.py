"""
价格效率因子
净价格变化 / 总路径长度
"""

def calculate(data):
    close = data['close']

    # 20期的净变化
    net_change = close - close.shift(20)

    # 20期的总路径长度（累计绝对变化）
    abs_changes = close.diff().abs().rolling(20).sum()

    # 效率 = 净变化 / 路径长度
    efficiency = net_change / (abs_changes + 1e-10)
    return efficiency
