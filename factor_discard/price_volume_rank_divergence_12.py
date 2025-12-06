"""
价格-成交量背离指标 - Rank Divergence (优化版)

因子描述:
    衡量价格排名位置与成交量排名位置的背离程度,并进行标准化
    当价格在高位但成交量在低位时为负背离(看跌),反之为正背离(看涨)

参数:
    period: 24 (2小时)
    zscore_window: 120 (10小时,用于标准化)

计算公式:
    price_rank = close在过去period内的百分位排名
    volume_rank = volume在过去period内的百分位排名
    divergence = price_rank - volume_rank

    # Z-score标准化增强信号
    factor = (divergence - mean(divergence, zscore_window)) / std(divergence, zscore_window)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-06
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算价格-成交量排名背离因子(标准化版)

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    period = 24
    zscore_window = 120

    # 计算价格在N期内的百分位排名(0-1之间)
    price_rank = close.rolling(window=period).rank(pct=True)

    # 计算成交量在N期内的百分位排名(0-1之间)
    volume_rank = volume.rolling(window=period).rank(pct=True)

    # 计算背离度:价格排名 - 成交量排名
    divergence = price_rank - volume_rank

    # Z-score标准化:使用滚动窗口标准化
    mean_div = divergence.rolling(window=zscore_window).mean()
    std_div = divergence.rolling(window=zscore_window).std()

    # 标准化因子值
    factor = (divergence - mean_div) / std_div

    return factor
