"""
振幅因子
(high - low) / close
"""

def calculate(data):
    high = data['high']
    low = data['low']
    close = data['close']
    # 振幅
    amplitude = (high - low) / close
    return amplitude
