"""
VWAP偏离因子
当前价格偏离成交量加权平均价
"""

def calculate(data):
    close = data['close']
    volume = data['volume']

    # 计算20期VWAP
    vwap = (close * volume).rolling(20).sum() / volume.rolling(20).sum()

    # 价格偏离VWAP
    deviation = (close - vwap) / vwap
    return deviation
