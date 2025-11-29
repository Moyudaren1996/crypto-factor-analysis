"""
实现波动率因子
使用Parkinson波动率估计（基于high和low）
"""
import numpy as np

def calculate(data):
    high = data['high']
    low = data['low']
    # Parkinson波动率: sqrt(1/(4*ln(2)) * (ln(high/low))^2)
    log_hl = np.log(high / low)
    parkinson_vol = (log_hl ** 2) / (4 * np.log(2))
    # 20期移动平均
    realized_vol = parkinson_vol.rolling(20).mean()
    return realized_vol
