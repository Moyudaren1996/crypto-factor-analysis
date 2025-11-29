"""
超短期动量因子
过去10期收益率
"""

def calculate(data):
    close = data['close']
    # 10期动量
    ret_10 = close.pct_change(10)
    return ret_10
