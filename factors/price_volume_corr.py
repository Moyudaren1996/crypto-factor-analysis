"""
量价相关性因子
短期价格与成交量的相关系数
"""

def calculate(data):
    close = data['close']
    volume = data['volume']

    # 计算20期滚动相关系数
    correlation = close.rolling(20).corr(volume)
    return correlation
