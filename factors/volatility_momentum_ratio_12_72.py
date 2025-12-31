"""
波动率指标 - Volatility Momentum Ratio (波动率动量比率)

因子描述:
    波动率动量比率因子，捕捉价格动量与波动率变化之间的非对称关系。

    核心假设：
    1. 健康的趋势应该伴随适度的波动率扩张
    2. 当价格动量远大于波动率扩张时，可能是趋势过热，预示反转
    3. 当价格动量远小于波动率扩张时，可能是恐慌性波动，也预示反转

    计算逻辑：
    1. 计算价格动量的Z-score (短期收益率在历史中的位置)
    2. 计算波动率变化的Z-score (ATR变化在历史中的位置)
    3. 计算两者的差值，当动量Z-score与波动率Z-score出现显著背离时产生信号
    4. 差值为正（动量强但波动率扩张慢）预示下跌反转
    5. 差值为负（动量弱但波动率扩张快）预示上涨反转

参数:
    short_period: 12 (1小时, 12个5分钟K线)
    long_period: 72 (6小时, 72个5分钟K线)

计算公式:
    1. returns = close.pct_change(short_period)
    2. atr = rolling_mean(high-low, short_period)
    3. atr_change = (atr - atr.shift(short_period)) / atr.shift(short_period)
    4. ret_z = (returns - rolling_mean(returns, long_period)) / rolling_std(returns, long_period)
    5. atr_z = (atr_change - rolling_mean(atr_change, long_period)) / rolling_std(atr_change, long_period)
    6. factor = -(ret_z - atr_z)  # 取负值做反转

输出:
    因子值DataFrame

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
    计算Volatility Momentum Ratio因子

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
    short_period = 12   # 1小时
    long_period = 72    # 6小时

    # 计算价格动量 (短期收益率)
    returns = close.pct_change(short_period)

    # 计算ATR及其变化
    true_range = high - low
    atr = true_range.rolling(short_period).mean()
    atr_shifted = atr.shift(short_period)
    atr_change = (atr - atr_shifted) / atr_shifted.replace(0, np.nan)

    # 计算收益率的Z-score
    ret_mean = returns.rolling(long_period).mean()
    ret_std = returns.rolling(long_period).std()
    ret_z = (returns - ret_mean) / ret_std.replace(0, np.nan)

    # 计算ATR变化的Z-score
    atr_mean = atr_change.rolling(long_period).mean()
    atr_std = atr_change.rolling(long_period).std()
    atr_z = (atr_change - atr_mean) / atr_std.replace(0, np.nan)

    # 计算差值作为因子 (取负值做反转)
    # 当动量Z-score远大于波动率Z-score时，预示下跌反转
    factor = -(ret_z - atr_z)

    return factor
