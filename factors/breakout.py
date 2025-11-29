"""
突破因子
价格突破20期高点为1，跌破20期低点为-1
"""

def calculate(data):
    close = data['close']
    high = data['high']
    low = data['low']

    # 20期最高价和最低价
    highest = high.rolling(20).max()
    lowest = low.rolling(20).min()

    # 突破信号
    breakout = (close > highest.shift(1)).astype(float) - (close < lowest.shift(1)).astype(float)

    return breakout
