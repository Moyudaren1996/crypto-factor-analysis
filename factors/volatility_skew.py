"""
波动率偏斜因子
上行波动率 / 下行波动率
"""

def calculate(data):
    close = data['close']
    returns = close.pct_change()

    # 上行波动率（正收益的标准差）
    upside_vol = returns[returns > 0].rolling(20).std()
    # 下行波动率（负收益的标准差）
    downside_vol = returns[returns < 0].rolling(20).std()

    # 填充缺失值
    upside_vol = upside_vol.reindex(returns.index).fillna(method='ffill')
    downside_vol = downside_vol.reindex(returns.index).fillna(method='ffill')

    # 偏斜比率
    vol_skew = upside_vol / downside_vol
    return vol_skew
