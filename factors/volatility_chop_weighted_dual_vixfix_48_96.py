"""
Volatility指标 - Chop Weighted Dual VixFix Z-Score

因子描述:
    基于Choppiness Index加权的双向VixFix指标。
    核心逻辑是：VixFix（恐慌-贪婪）本质上是均值回归策略，而在震荡市场（Choppy Market）中，均值回归策略效果最好。
    在趋势市场（Low Chop）中，均值回归信号往往是逆势操作，风险较大。
    本因子使用Choppiness Index作为权重：
    - 当市场震荡（Chop高）时，加大Dual VixFix信号权重；
    - 当市场趋势（Chop低）时，降低Dual VixFix信号权重。
    
    Factor = (Fear - Greed) * (CHOP / 100).
    这种加权不仅优化了信号质量，还有效降低了与纯价格指标（如RSI）的相关性。

参数:
    period: 48 (4小时) - VixFix计算周期
    chop_period: 96 (8小时) - Choppiness计算周期
    z_period: 144 (12小时) - Z-Score标准化周期

计算公式:
    Fear = (Highest(Close, period) - Low) / Highest(Close, period) * 100
    Greed = (High - Lowest(Close, period)) / Lowest(Close, period) * 100
    
    TR = Max(High-Low, Abs(High-Close_prev), Abs(Low-Close_prev))
    SumTR = Sum(TR, chop_period)
    Range = Max(High, chop_period) - Min(Low, chop_period)
    CHOP = 100 * Log10(SumTR / Range) / Log10(chop_period)
    
    Net = Fear - Greed
    Weighted = Net * (CHOP / 100)
    Z-Score = (Weighted - Mean(Weighted, z_period)) / Std(Weighted, z_period)

输出:
    因子值DataFrame（Z-Score值）

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2026-01-03
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Chop Weighted Dual VixFix Z-Score因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    high = data['high']
    low = data['low']
    
    period = 48
    chop_period = 96
    z_period = 144

    # 1. 计算 Fear (Williams VixFix)
    highest_close = close.rolling(window=period).max()
    fear = ((highest_close - low) / highest_close) * 100
    
    # 2. 计算 Greed (Inverse VixFix)
    lowest_close = close.rolling(window=period).min()
    # 避免分母为0
    greed = ((high - lowest_close) / lowest_close) * 100
    
    # 3. 计算 Choppiness Index
    close_prev = close.shift(1)
    # TR = Max(High-Low, Abs(High-Close_prev), Abs(Low-Close_prev))
    tr = np.maximum(high - low, np.maximum((high - close_prev).abs(), (low - close_prev).abs()))
    
    sum_tr = tr.rolling(window=chop_period).sum()
    high_max = high.rolling(window=chop_period).max()
    low_min = low.rolling(window=chop_period).min()
    range_hl = high_max - low_min
    
    # 避免除以0
    chop = 100 * np.log10(sum_tr / range_hl) / np.log10(chop_period)
    
    # 4. 计算加权净情绪
    net_sentiment = fear - greed
    weighted = net_sentiment * (chop / 100)
    
    # 5. 计算Z-Score
    net_mean = weighted.rolling(window=z_period).mean()
    net_std = weighted.rolling(window=z_period).std()
    
    factor = (weighted - net_mean) / net_std
    
    # 处理inf和nan
    factor = factor.replace([np.inf, -np.inf], np.nan)
    
    return factor
