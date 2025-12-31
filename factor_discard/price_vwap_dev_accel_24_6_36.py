"""
Price指标 - VWAP Deviation Acceleration Reversal (VWAP偏离加速反转)

因子描述:
    计算收盘价相对于VWAP(成交量加权平均价)的偏离度,并衡量其加速度变化作为反转信号
    VWAP = 累积(price*volume) / 累积(volume),代表真实成交中心
    偏离度 = (close - VWAP) / VWAP
    短期偏离 = 偏离度的短期均值
    长期偏离 = 偏离度的长期均值
    加速度 = 短期偏离 - 长期偏离
    假设:当价格加速偏离VWAP时,往往预示过度,预示反转

参数:
    vwap_period: 24 (2小时,VWAP计算窗口)
    short_period: 6 (30分钟,短期偏离)
    long_period: 36 (3小时,长期基线)

计算公式:
    vwap = (close * volume).rolling(vwap_period).sum() / volume.rolling(vwap_period).sum()
    deviation = (close - vwap) / (vwap + 1e-8)
    short_dev = deviation.ewm(span=short_period).mean()
    long_dev = deviation.ewm(span=long_period).mean()
    acceleration = short_dev - long_dev
    factor = -acceleration  # 取负:加速偏离时因子值为负,预示反转

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-14
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算VWAP偏离加速反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    vwap_period = 24
    short_period = 6
    long_period = 36

    # 计算VWAP
    vwap_numerator = (close * volume).rolling(vwap_period).sum()
    vwap_denominator = volume.rolling(vwap_period).sum()
    vwap = vwap_numerator / (vwap_denominator + 1e-8)

    # 计算价格相对VWAP的偏离度
    deviation = (close - vwap) / (vwap + 1e-8)

    # 计算短期和长期偏离
    short_dev = deviation.ewm(span=short_period, adjust=False).mean()
    long_dev = deviation.ewm(span=long_period, adjust=False).mean()

    # 计算加速度
    acceleration = short_dev - long_dev

    # 取负值作为反转信号:加速偏离时因子值为负
    factor = -acceleration

    return factor
