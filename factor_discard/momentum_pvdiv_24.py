"""
Momentum指标 - PVDiv (Price-Volume Divergence Strength)

因子描述:
    价格成交量背离强度指标,衡量价格动量与成交量动量的不一致程度
    当价格强势上涨但成交量疲软时为正背离(可能见顶)
    当成交量放大但价格弱势时为负背离(可能筑底)

参数:
    period: 24 (2小时,即24个5分钟K线)

计算公式:
    price_momentum = (close - close[t-period]) / close[t-period]
    volume_momentum = (volume - volume[t-period]) / volume[t-period]
    price_z = (price_momentum - rolling_mean(price_momentum)) / rolling_std(price_momentum)
    volume_z = (volume_momentum - rolling_mean(volume_momentum)) / rolling_std(volume_momentum)
    divergence = price_z - volume_z

输出:
    因子值DataFrame,正值表示价格强于成交量(看跌信号),负值表示成交量强于价格(看涨信号)

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-07
版本: v1.0
废弃日期: 2025-12-07
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算价格成交量背离强度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    period = 24  # 2小时
    window = 120  # 10小时,用于标准化

    # 计算价格动量
    price_momentum = (close - close.shift(period)) / close.shift(period)

    # 计算成交量动量
    volume_momentum = (volume - volume.shift(period)) / volume.shift(period)

    # 对价格动量进行滚动标准化
    price_mean = price_momentum.rolling(window).mean()
    price_std = price_momentum.rolling(window).std()
    price_z = (price_momentum - price_mean) / price_std

    # 对成交量动量进行滚动标准化
    volume_mean = volume_momentum.rolling(window).mean()
    volume_std = volume_momentum.rolling(window).std()
    volume_z = (volume_momentum - volume_mean) / volume_std

    # 计算背离强度:价格标准化动量 - 成交量标准化动量
    divergence = price_z - volume_z

    return divergence
