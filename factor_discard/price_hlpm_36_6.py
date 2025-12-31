"""
Price指标 - High Low Position Momentum

因子描述:
    高低价位置动量因子,基于Alpha101思想衡量价格在高低区间相对位置的动态变化
    计算价格在N期高低区间的位置(Williams %R风格),然后计算该位置的变化率
    位置上升表示价格向高位移动(强势),位置下降表示价格向低位移动(弱势)
    在5分钟高频数据中,这种位置变化能捕捉短期动量的方向和强度

参数:
    hl_period: 36 (3小时高低区间)
    change_period: 6 (30分钟位置变化)

计算公式:
    1. 计算N期最高价和最低价: high_n = high.rolling(36).max(), low_n = low.rolling(36).min()
    2. 计算价格在区间的相对位置: position = (close - low_n) / (high_n - low_n)
    3. 计算位置的变化率: position_change = position - position.shift(6)
    4. 用ATR标准化消除波动率影响: true_range = high - low
    5. 最终因子: factor = position_change / true_range.rolling(36).mean()

输出:
    因子值DataFrame
    正值表示价格位置上升(强势),负值表示价格位置下降(弱势)

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-07
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算高低价位置动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    hl_period = 36         # 3小时高低区间
    change_period = 6      # 30分钟位置变化

    # 计算N期最高价和最低价
    high_n = high.rolling(hl_period).max()
    low_n = low.rolling(hl_period).min()

    # 计算价格在区间的相对位置(0到1之间)
    position = (close - low_n) / (high_n - low_n)

    # 计算位置的变化率
    position_change = position - position.shift(change_period)

    # 用真实波幅标准化
    true_range = high - low
    atr = true_range.rolling(hl_period).mean()

    # 计算最终因子
    factor = position_change / atr

    return factor
