"""
成交量分布不对称因子 - Volume Distribution Asymmetry

因子描述:
    衡量成交量在价格区间内的分布不对称性
    计算成交量加权价格位置与价格区间中点的偏离程度

    如果成交量主要集中在高价区,表示买方力量强(看涨)
    如果成交量主要集中在低价区,表示卖方力量强(看跌)

参数:
    period: 6 (30分钟)

计算公式:
    对于每个周期:
    1. 计算价格区间中点 = (high + low) / 2
    2. 计算收盘价相对位置 = (close - low) / (high - low)  # 范围[0,1]
    3. 计算成交量加权的相对位置均值
    4. 不对称度 = 加权位置 - 0.5  # 范围[-0.5, 0.5]
    5. 对N期不对称度求移动平均

    取值:
    - 正值: 成交集中在高价区,买盘强
    - 负值: 成交集中在低价区,卖盘强
    - 接近0: 成交均匀分布

输出:
    因子值DataFrame,取值范围约[-0.5, 0.5]

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-06
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量分布不对称因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']
    volume = data['volume']

    period = 6

    # 计算价格区间
    price_range = high - low

    # 避免除零,当区间为0时设为nan
    price_range = price_range.replace(0, np.nan)

    # 计算收盘价在区间内的相对位置[0, 1]
    # 0表示在最低点,1表示在最高点,0.5表示在中点
    close_position = (close - low) / price_range

    # 计算不对称度 = 位置 - 0.5
    # 正值表示偏向高价区,负值表示偏向低价区
    asymmetry = close_position - 0.5

    # 用成交量加权不对称度
    # 成交量大的K线权重更高
    weighted_asymmetry = asymmetry * volume

    # 计算N期内的平均成交量加权不对称度
    sum_weighted = weighted_asymmetry.rolling(window=period).sum()
    sum_volume = volume.rolling(window=period).sum()

    # 避免除零
    sum_volume = sum_volume.replace(0, np.nan)

    # 最终因子值
    factor = sum_weighted / sum_volume

    return factor
