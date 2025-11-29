"""
隔夜跳空因子
当前开盘价与上一期收盘价的价差
"""

def calculate(data):
    open_price = data['open']
    close = data['close']
    # 跳空 = (open - close_prev) / close_prev
    gap = (open_price - close.shift(1)) / close.shift(1)
    return gap
