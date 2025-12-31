"""
Oscillator指标 - Volume Weighted Reversal

因子描述:
    成交量加权反转因子,结合价格偏离度和成交量异常来识别反转机会
    当价格大幅偏离均线且成交量放大时,可能出现反转
    因子值为负表示超买(预期下跌反转),因子值为正表示超卖(预期上涨反转)

参数:
    period: 24 (2小时)

计算公式:
    price_deviation = (close - close.rolling(period).mean()) / close.rolling(period).std()
    volume_ratio = volume / volume.rolling(period).mean()
    factor = -price_deviation * volume_ratio  # 负号使得超买为负值,超卖为正值

输出:
    因子值DataFrame,负值表示超买(看跌),正值表示超卖(看涨)

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-07
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Volume Weighted Reversal因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    period = 24

    # 计算价格偏离度(标准化)
    price_ma = close.rolling(period).mean()
    price_std = close.rolling(period).std()
    price_deviation = (close - price_ma) / (price_std + 1e-8)

    # 计算相对成交量
    volume_ma = volume.rolling(period).mean()
    volume_ratio = volume / (volume_ma + 1e-8)

    # 成交量加权反转因子:价格偏离越大,成交量越大,反转信号越强
    # 使用负号:价格上偏离(超买)为负值,价格下偏离(超卖)为正值
    factor = -price_deviation * volume_ratio

    return factor
