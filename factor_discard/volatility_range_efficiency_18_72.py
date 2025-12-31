"""
Volatility指标 - Range Efficiency (波幅效率)

因子描述:
    波幅效率因子，衡量价格在给定时间窗口内的实际移动距离与日内波幅累积的效率比。
    高效率意味着价格有明确方向性运动(趋势)，低效率意味着价格在区间内震荡。
    该因子结合短期和长期的波幅效率差异，捕捉趋势形成或衰退的信号。

    与Path Efficiency不同，本因子使用High-Low波幅(Parkinson估计器)而非收盘价变化，
    能更好地捕捉日内波动特征。

参数:
    short_period: 18 (1.5小时) - 短期窗口
    long_period: 72 (6小时) - 长期窗口

计算公式:
    1. price_move = abs(close - close.shift(period))  # 净移动距离
    2. range_sum = (high - low).rolling(period).sum()  # 累积波幅
    3. efficiency = price_move / range_sum  # 效率比 [0,1]
    4. factor = short_efficiency - long_efficiency  # 短期效率减长期效率

输出:
    因子值DataFrame，正值表示短期效率高于长期(趋势形成)，负值反之(趋势衰退)

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波幅效率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 18   # 1.5小时
    long_period = 72    # 6小时

    # 计算日内波幅
    intraday_range = high - low

    # 短期波幅效率
    short_move = (close - close.shift(short_period)).abs()
    short_range_sum = intraday_range.rolling(short_period).sum()
    short_efficiency = short_move / (short_range_sum + 1e-10)

    # 长期波幅效率
    long_move = (close - close.shift(long_period)).abs()
    long_range_sum = intraday_range.rolling(long_period).sum()
    long_efficiency = long_move / (long_range_sum + 1e-10)

    # 效率差
    factor = short_efficiency - long_efficiency

    return factor
