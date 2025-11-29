"""
短期反转因子
过去3期收益率的负值（短期反转效应）
"""

def calculate(data):
    close = data['close']
    # 短期反转：过去3期收益率取负
    ret_3 = close.pct_change(3)
    return -ret_3
