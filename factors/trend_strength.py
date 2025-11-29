"""
趋势强度因子
过去20期收益率除以标准差（夏普风格）
"""

def calculate(data):
    close = data['close']
    # 计算过去20期收益率
    returns = close.pct_change()
    ret_20 = returns.rolling(20).sum()
    std_20 = returns.rolling(20).std()
    # 趋势强度 = 累计收益 / 波动率
    trend_strength = ret_20 / std_20
    return trend_strength
