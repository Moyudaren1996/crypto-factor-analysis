"""
布林带位置因子
价格在布林带中的相对位置
"""

def calculate(data):
    close = data['close']

    # 20期均线和标准差
    ma = close.rolling(20).mean()
    std = close.rolling(20).std()

    # 布林带上下轨
    upper_band = ma + 2 * std
    lower_band = ma - 2 * std

    # 相对位置
    bb_position = (close - lower_band) / (upper_band - lower_band + 1e-10)

    return bb_position
