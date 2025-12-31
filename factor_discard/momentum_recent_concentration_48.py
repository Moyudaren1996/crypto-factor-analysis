"""
Momentum指标 - RecentMomentumConcentration (近期动量集中度)

因子描述:
    衡量动量在时间维度上的集中程度。

    核心思想:
    1. 将N期总动量分解为前半段和后半段
    2. 计算后半段(近期)动量占总动量的比例
    3. 如果动量主要集中在近期,说明趋势可能刚形成或加速
    4. 如果动量主要在前期,说明趋势可能在减速

    这与RSI不同:
    - RSI衡量涨跌幅度比
    - 本因子衡量动量的时间分布

参数:
    period: 48 (4小时总周期)

计算公式:
    1. total_return = close / shift(close, period) - 1
    2. recent_return = close / shift(close, period/2) - 1
    3. early_return = shift(close, period/2) / shift(close, period) - 1
    4. concentration = recent_return / total_return (当total_return != 0)
    5. factor = concentration * sign(total_return)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算RecentMomentumConcentration因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    period = 48       # 4小时总周期
    half_period = 24  # 2小时半周期

    # 1. 计算不同时间段的收益率
    # 总收益率 (N期)
    total_return = close / close.shift(period) - 1

    # 近期收益率 (后半段 N/2期)
    recent_return = close / close.shift(half_period) - 1

    # 2. 计算近期动量集中度
    # 近期收益占总收益的比例
    epsilon = 1e-10
    # 为避免除以接近0的数,使用相对大小关系
    concentration = recent_return / (total_return.abs() + epsilon)

    # 3. 取符号:
    # - 上涨趋势中,近期集中度高为正
    # - 下跌趋势中,近期集中度高为负
    trend_sign = np.sign(total_return)

    # 4. 对集中度进行截断处理,避免极端值
    concentration_clipped = concentration.clip(-3, 3)

    # 5. 最终因子
    factor = concentration_clipped * trend_sign

    # 6. 滚动标准化,减少极端值影响
    factor_mean = factor.rolling(period*2).mean()
    factor_std = factor.rolling(period*2).std()
    factor_normalized = (factor - factor_mean) / (factor_std + epsilon)

    return factor_normalized
