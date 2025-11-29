"""
RSI风格因子
相对强弱指标
"""

def calculate(data):
    close = data['close']

    # 计算价格变化
    delta = close.diff()

    # 分离涨跌
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    # RSI
    rs = gain / (loss + 1e-10)
    rsi = 100 - (100 / (1 + rs))

    # 中心化：减去50
    return (rsi - 50) / 50
