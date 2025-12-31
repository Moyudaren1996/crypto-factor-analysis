"""
Volatility指标 - ReturnKurtosis (收益率峰度)

因子描述:
    收益率峰度因子衡量收益率分布的尾部厚度(肥尾程度)。
    高峰度意味着极端收益出现的频率高于正态分布,市场处于不稳定状态。
    结合当前价格相对于均值的偏离方向,当峰度高且价格偏离大时识别反转机会。
    低峰度的稳定市场可能预示趋势延续。

参数:
    kurt_period: 36 (3小时) - 计算峰度的滚动窗口
    zscore_period: 72 (6小时) - 计算价格Z-score的窗口

计算公式:
    1. ret = close.pct_change() 收益率
    2. kurt = ret.rolling(kurt_period).kurt() 滚动峰度
    3. price_mean = close.rolling(zscore_period).mean()
    4. price_std = close.rolling(zscore_period).std()
    5. price_zscore = (close - price_mean) / price_std 价格Z-score
    6. kurt_percentile = kurt.rolling(zscore_period).rank(pct=True) 峰度时序排名
    7. factor = (kurt_percentile - 0.5) * 2 * price_zscore

输出:
    因子值DataFrame，高峰度+价格高偏离=正值预期下跌，反之亦然

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-30
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算收益率峰度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    kurt_period = 36    # 3小时计算峰度
    zscore_period = 72  # 6小时Z-score

    # 计算收益率
    ret = close.pct_change()

    # 滚动峰度
    kurt = ret.rolling(kurt_period, min_periods=kurt_period).kurt()

    # 价格Z-score (衡量当前价格相对于近期的偏离程度)
    price_mean = close.rolling(zscore_period, min_periods=zscore_period).mean()
    price_std = close.rolling(zscore_period, min_periods=zscore_period).std()
    price_zscore = (close - price_mean) / price_std.replace(0, np.nan)

    # 峰度的时序百分位排名
    kurt_percentile = kurt.rolling(zscore_period, min_periods=zscore_period).rank(pct=True)

    # 组合逻辑:
    # 高峰度(接近1) + 价格正向偏离(zscore>0) -> 市场不稳定且过热,预期下跌(正因子)
    # 高峰度(接近1) + 价格负向偏离(zscore<0) -> 市场不稳定且过冷,预期上涨(负因子)
    factor = (kurt_percentile - 0.5) * 2 * price_zscore

    return factor
