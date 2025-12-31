"""
Volatility指标 - Intraday Intensity (日内波动强度因子)

因子描述:
    基于日内K线形态计算波动率强度指标。该因子衡量收盘价相对于
    日内高低区间的位置(买卖压力)与波动率变化的组合效应。

    核心逻辑:当收盘价位于日内区间高位但波动率在收缩(相对于历史),
    表明上涨动能减弱;反之,当收盘价位于低位但波动率收缩时,
    表明下跌动能减弱。这种背离往往预示反转。

参数:
    short_period: 12 (1小时)
    long_period: 48 (4小时)

计算公式:
    price_position = (close - low) / (high - low)  # 0-1之间
    true_range = max(high-low, |high-prev_close|, |low-prev_close|)
    vol_ratio = rolling_mean(true_range, short) / rolling_mean(true_range, long)
    factor = (price_position - 0.5) * (1 - vol_ratio)

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
    计算Intraday Intensity因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 12  # 1小时
    long_period = 48   # 4小时

    # 计算价格在日内区间的相对位置 (0-1)
    hl_range = high - low
    hl_range = hl_range.replace(0, np.nan)  # 避免除零
    price_position = (close - low) / hl_range

    # 计算True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=0).groupby(level=0).max()

    # 如果上面方法有问题,用逐元素比较
    true_range = tr1.copy()
    true_range = true_range.where(true_range >= tr2, tr2)
    true_range = true_range.where(true_range >= tr3, tr3)

    # 计算短期和长期波动率
    vol_short = true_range.rolling(short_period).mean()
    vol_long = true_range.rolling(long_period).mean()

    # 波动率比率
    vol_ratio = vol_short / vol_long
    vol_ratio = vol_ratio.replace([np.inf, -np.inf], np.nan)

    # 波动率收缩程度 (1 - ratio):正值表示波动率收缩,负值表示扩张
    vol_contraction = 1 - vol_ratio

    # 价格位置偏离中心 (position - 0.5): 正值表示偏高位,负值表示偏低位
    position_deviation = price_position - 0.5

    # 核心因子: 高位置 + 波动率收缩 -> 反转做空(正值)
    #          低位置 + 波动率收缩 -> 反转做多(负值)
    raw_factor = position_deviation * vol_contraction

    # 对因子进行滚动标准化
    factor_mean = raw_factor.rolling(long_period).mean()
    factor_std = raw_factor.rolling(long_period).std()
    factor = (raw_factor - factor_mean) / factor_std
    factor = factor.replace([np.inf, -np.inf], np.nan)

    # 取负值使得因子为负向(做多低值组)
    factor = -factor

    return factor
