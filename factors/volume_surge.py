"""
成交量突破因子
当前成交量 / 20期均值
"""

def calculate(data):
    volume = data['volume']
    # 成交量相对强度
    vol_ma = volume.rolling(20).mean()
    vol_ratio = volume / vol_ma
    return vol_ratio
