"""
Oscillator指标 - Cross-sectional PV Rank Divergence (横截面价量排名背离)

因子描述:
    横截面价量排名背离因子,基于币种间的相对强度识别反转机会
    在同一时刻对所有币种按价格动量和成交量强度分别排名
    当某币种价格排名高(强势)但成交量排名低(弱势)时,预示该币种相对超买可能反转
    当某币种价格排名低(弱势)但成交量排名高(强势)时,预示该币种相对超卖可能反弹

    因子为负值表示反转向下信号(价格相对强势但成交量相对弱势)
    因子为正值表示反转向上信号(价格相对弱势但成交量相对强势)

参数:
    period: 36 (3小时)

计算公式:
    1. price_momentum = (close - close.shift(period)) / close.shift(period)  # 价格动量
    2. volume_strength = volume / volume.rolling(period).mean()  # 相对成交量强度
    3. price_rank = price_momentum在横截面(币种维度)的排名百分位 [0, 1]
    4. volume_rank = volume_strength在横截面(币种维度)的排名百分位 [0, 1]
    5. rank_divergence = volume_rank - price_rank  # 排名背离度 [-1, 1]
       - rank_divergence > 0: 成交量排名高于价格排名,成交量支撑强,看涨
       - rank_divergence < 0: 价格排名高于成交量排名,成交量支撑弱,看跌
    6. factor = rank_divergence  # 正值看涨,负值看跌

输出:
    因子值DataFrame,范围[-1, 1],数值越大表示反转向上信号越强

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-14
版本: v2.2 (第3次优化)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Cross-sectional PV Rank Divergence因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    period = 36

    # 计算价格动量
    price_momentum = (close - close.shift(period)) / close.shift(period)

    # 计算相对成交量强度
    volume_mean = volume.rolling(period).mean()
    volume_strength = volume / volume_mean

    # 在每个时间点(横截面)对所有币种进行排名
    # rank(pct=True)返回排名百分位,范围[0, 1]
    # axis=1表示在列(币种)维度排名
    price_rank = price_momentum.rank(axis=1, pct=True)
    volume_rank = volume_strength.rank(axis=1, pct=True)

    # 计算排名背离度
    # volume_rank > price_rank: 成交量相对强势,看涨信号
    # volume_rank < price_rank: 价格相对强势但成交量弱势,看跌信号
    rank_divergence = volume_rank - price_rank

    factor = rank_divergence

    return factor
