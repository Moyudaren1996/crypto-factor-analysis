"""
收盘价位置因子
close在(high, low)区间中的相对位置
"""

def calculate(data):
    high = data['high']
    low = data['low']
    close = data['close']

    # 相对位置 = (close - low) / (high - low)
    # 接近1表示收在高位，接近0表示收在低位
    relative_position = (close - low) / (high - low + 1e-10)
    return relative_position
