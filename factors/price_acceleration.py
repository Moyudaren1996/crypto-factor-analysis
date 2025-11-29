"""
价格加速度因子
收益率的变化率（二阶导数）
"""

def calculate(data):
    close = data['close']
    # 一阶导数：收益率
    returns = close.pct_change()
    # 二阶导数：收益率的变化
    acceleration = returns.diff()
    return acceleration
