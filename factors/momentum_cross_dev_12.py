"""
Momentum指标 - 截面动量排名离差

因子描述:
    截面动量排名离差因子，衡量单个币种的动量相对于其他币种的排名位置。
    在每个时间点，计算该币种的动量在所有币种中的百分位排名，
    用当前排名减去其历史平均排名，捕捉相对动量的异常变化。
    正值表示相对动量高于历史水平，负值表示相对动量低于历史水平。

参数:
    momentum_period: 6 (30分钟)
    ranking_window: 12 (1小时)

计算公式:
    MOM = (close - close[t-6]) / close[t-6]
    Current_Rank = MOM在截面上的百分位排名
    Historical_Rank = Current_Rank.rolling(12).mean()
    Deviation = Current_Rank - Historical_Rank

输出:
    因子值DataFrame，表示相对动量的排名离差

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算截面动量排名离差因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    momentum_period = 6      # 6个5分钟K线 = 30分钟
    ranking_window = 12      # 12个5分钟K线 = 1小时

    # 计算动量 (百分比变化)
    momentum = (close - close.shift(momentum_period)) / close.shift(momentum_period)

    # 计算截面排名百分位 (0-100)
    # rank(pct=True)返回0-1之间的值，乘以100转换为0-100
    rank_pct = momentum.rank(axis=1, pct=True) * 100

    # 计算排名的移动平均 (历史平均排名)
    rank_ma = rank_pct.rolling(window=ranking_window).mean()

    # 计算离差
    deviation = rank_pct - rank_ma

    return deviation
