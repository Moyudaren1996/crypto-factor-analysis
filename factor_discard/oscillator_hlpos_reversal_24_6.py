"""
Oscillator指标 - HL Position Momentum Reversal (高低价位置动量反转)

因子描述:
    计算收盘价在高低区间的相对位置,并衡量其短期动量变化作为反转信号
    位置指标 = (close - low_N) / (high_N - low_N),类似Williams %R
    位置动量 = 位置[t] - 位置[t-M]
    假设:当价格快速从低位冲向高位(位置动量大)时,往往预示反转

参数:
    hl_period: 24 (2小时,高低价窗口)
    mom_period: 6 (30分钟,动量窗口)

计算公式:
    hl_position = (close - low.rolling(hl_period).min()) /
                  (high.rolling(hl_period).max() - low.rolling(hl_period).min() + 1e-8)
    position_momentum = hl_position - hl_position.shift(mom_period)
    factor = -position_momentum  # 取负:快速冲高时因子值为负,预示反转

输出:
    因子值DataFrame

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-14
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算高低价位置动量反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    hl_period = 24
    mom_period = 6

    # 计算N期最高价和最低价
    high_n = high.rolling(hl_period).max()
    low_n = low.rolling(hl_period).min()

    # 计算收盘价在高低区间的相对位置(0-1之间)
    hl_position = (close - low_n) / ((high_n - low_n) + 1e-8)

    # 计算位置的短期动量
    position_momentum = hl_position - hl_position.shift(mom_period)

    # 取负值作为反转信号:快速冲高(正动量)时因子值为负
    factor = -position_momentum

    return factor
