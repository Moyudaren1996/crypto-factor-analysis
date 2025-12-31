"""
Trend指标 - TCONS (Trend Consistency)

因子描述:
    多尺度趋势一致性指标,通过比较短期趋势和长期趋势的方向一致性
    来识别趋势的强度和可持续性。当短期趋势与长期趋势方向一致时,
    趋势更可能延续;当背离时,可能出现反转。
    使用波动率归一化来消除不同币种波动率差异的影响。

参数:
    short_period: 24 (2小时,5分钟K线×24)
    long_period: 72 (6小时,5分钟K线×72)

计算公式:
    1. short_trend = (close - close.shift(24)) / close.shift(24)  # 短期趋势
    2. long_trend = (close - close.shift(72)) / close.shift(72)   # 长期趋势
    3. trend_consistency = short_trend * long_trend  # 趋势一致性(同向为正,反向为负)
    4. volatility = close.pct_change()的72期标准差
    5. factor = trend_consistency / volatility  # 波动率标准化的趋势一致性

    解释:
    - 当短长期趋势同向上涨(都>0)时,factor>0,预示趋势延续
    - 当短长期趋势同向下跌(都<0)时,factor>0,预示下跌趋势延续
    - 当短长期趋势反向时,factor<0,预示趋势反转
    - 波动率调整使得因子在不同波动环境下可比

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-08
版本: v1.3 (第3次优化)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算TCONS因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']

    # 定义参数
    short_period = 24
    long_period = 72

    # 计算短期趋势(24期,2小时)
    short_trend = (close - close.shift(short_period)) / close.shift(short_period)

    # 计算长期趋势(72期,6小时)
    long_trend = (close - close.shift(long_period)) / close.shift(long_period)

    # 计算趋势一致性
    # 当short_trend和long_trend同号(都为正或都为负)时,乘积为正,表示趋势一致
    # 当short_trend和long_trend异号时,乘积为负,表示趋势背离
    trend_consistency = short_trend * long_trend

    # 计算波动率(使用收益率的标准差)
    returns = close.pct_change()
    volatility = returns.rolling(long_period).std()

    # 波动率标准化的趋势一致性因子
    factor = trend_consistency / volatility

    return factor
