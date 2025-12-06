"""
Volume指标 - VWM (Volume-Weighted Momentum)

因子描述:
    成交量加权动量指标,结合价格变化率与相对成交量强度
    计算价格收益率乘以相对成交量的组合指标
    高正值表示放量上涨,高负值表示放量下跌,接近0表示缩量震荡

参数:
    price_period: 6 (30分钟价格动量)
    volume_period: 12 (1小时成交量标准化)

计算公式:
    price_momentum = (close - close.shift(price_period)) / close.shift(price_period)
    volume_ratio = volume / volume.rolling(volume_period).mean()
    VWM = price_momentum * volume_ratio

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-06
版本: v2.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Volume-Weighted Momentum因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    price_period = 6
    volume_period = 12

    # 计算价格动量(收益率)
    price_momentum = (close - close.shift(price_period)) / close.shift(price_period)

    # 计算相对成交量(当前成交量 / 均值成交量)
    volume_ma = volume.rolling(volume_period).mean()
    volume_ratio = volume / volume_ma

    # 计算成交量加权动量
    vwm = price_momentum * volume_ratio

    # 处理异常值和NaN
    vwm = vwm.fillna(0)
    vwm = vwm.replace([np.inf, -np.inf], 0)

    return vwm

