"""
Volatility指标 - ATR Contraction Rank (ATR收缩排名)

因子描述:
    衡量ATR收缩程度在历史分布中的排名位置。
    当短期ATR相对于长期ATR处于历史低位时,表示波动率极度收缩,
    往往是趋势启动的前兆。通过计算ATR比率在历史窗口的百分位排名,
    识别波动率收缩/扩张的极端状态。

参数:
    short_period: 6 (30分钟ATR)
    long_period: 72 (6小时ATR)
    rank_period: 96 (8小时排名窗口)

计算公式:
    true_range = max(high - low, |high - close.shift(1)|, |low - close.shift(1)|)
    short_atr = true_range.rolling(short_period).mean()
    long_atr = true_range.rolling(long_period).mean()
    atr_ratio = short_atr / long_atr
    factor = atr_ratio.rolling(rank_period).rank(pct=True)

输出:
    因子值DataFrame,0-1之间,低值表示波动率收缩,高值表示波动率扩张

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算ATR收缩排名因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    short_period = 6   # 30分钟
    long_period = 72   # 6小时
    rank_period = 96   # 8小时排名窗口
    epsilon = 1e-10

    # 计算True Range
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    true_range = np.maximum(tr1, np.maximum(tr2, tr3))

    # 计算短期和长期ATR
    short_atr = true_range.rolling(short_period).mean()
    long_atr = true_range.rolling(long_period).mean()

    # 计算ATR比率
    atr_ratio = short_atr / (long_atr + epsilon)

    # 计算历史百分位排名
    factor = atr_ratio.rolling(rank_period).rank(pct=True)

    return factor
