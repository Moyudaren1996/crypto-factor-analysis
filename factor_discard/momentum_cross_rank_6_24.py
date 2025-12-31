"""
动量指标 - Cross-Sectional Rank Momentum

因子描述:
    截面排名动量因子,衡量币种在市场中的相对强度排名变化
    通过计算短期和长期收益率在截面上的排名差异,捕捉轮动效应
    正值表示相对强度上升(资金流入),负值表示相对强度下降(资金流出)

参数:
    short_period: 6 (30分钟,短期动量)
    long_period: 24 (2小时,长期动量)

计算公式:
    1. 计算6期收益率: ret_short = close / close.shift(6) - 1
    2. 计算24期收益率: ret_long = close / close.shift(24) - 1
    3. 短期截面排名: rank_short = ret_short.rank(axis=1, pct=True)
    4. 长期截面排名: rank_long = ret_long.rank(axis=1, pct=True)
    5. 排名动量: factor = rank_short - rank_long

输出:
    因子值DataFrame,范围约[-1, 1]
    正值表示短期表现优于长期,负值表示短期表现弱于长期

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-11
版本: v1.3 (第3次优化)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算截面排名动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    # 参数定义
    short_period = 6   # 短期动量周期(30分钟)
    long_period = 24   # 长期动量周期(2小时)

    # 计算短期和长期收益率
    ret_short = close / close.shift(short_period) - 1
    ret_long = close / close.shift(long_period) - 1

    # 计算截面排名(每个时间点,在所有币种中的排名百分位)
    # axis=1表示横向(跨币种)排名, pct=True返回百分位[0,1]
    rank_short = ret_short.rank(axis=1, pct=True)
    rank_long = ret_long.rank(axis=1, pct=True)

    # 计算排名变化(排名动量)
    factor = rank_short - rank_long

    return factor
