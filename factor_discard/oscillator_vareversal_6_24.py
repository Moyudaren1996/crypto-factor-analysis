"""
Oscillator指标 - Volatility Adjusted Reversal (波动率调整反转)

因子描述:
    基于波动率标准化的价格冲击识别反转信号
    当短期价格冲击(收益率/波动率)显著强于长期时,预示过度反应和反转
    使用相对强度比率(短期/长期)而非绝对差异,提高稳定性

参数:
    short_period: 6 (30分钟,短期观察窗口)
    long_period: 24 (2小时,长期观察窗口)

计算公式:
    1. 短期标准化收益 = return_short / std_short
       return_short = (close - close.shift(short_period)) / close.shift(short_period)
       std_short = close.pct_change().rolling(short_period).std()

    2. 长期标准化收益 = return_long / std_long
       return_long = (close - close.shift(long_period)) / close.shift(long_period)
       std_long = close.pct_change().rolling(long_period).std()

    3. 反转信号 = -(短期标准化收益 / (长期标准化收益 + 1e-6) - 1)
       当短期冲击/长期冲击比率>1时(短期过度反应),产生负信号预示反转

输出:
    因子值DataFrame,负值预示反转向下,正值预示反转向上

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-13
版本: v2.0 (最优版本)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率调整反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 6   # 30分钟
    long_period = 24   # 2小时

    # 计算短期收益率
    short_return = (close - close.shift(short_period)) / close.shift(short_period)

    # 计算长期收益率
    long_return = (close - close.shift(long_period)) / close.shift(long_period)

    # 计算滚动波动率
    pct_change = close.pct_change()
    short_vol = pct_change.rolling(short_period).std()
    long_vol = pct_change.rolling(long_period).std()

    # 避免除以0
    short_vol = short_vol.replace(0, np.nan)
    long_vol = long_vol.replace(0, np.nan)

    # 计算标准化收益(价格冲击强度)
    short_impact = short_return / short_vol
    long_impact = long_return / long_vol

    # 计算相对冲击强度比率
    # 当短期冲击>>长期冲击时,意味着过度反应,预示反转
    impact_ratio = short_impact / (long_impact.abs() + 1e-6)

    # 反转信号:取负值,使得过度上涨(高比率)预示下跌
    reversal_signal = -(impact_ratio - 1)

    return reversal_signal
