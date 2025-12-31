"""
Momentum指标 - Directional Pressure (方向性压力)

因子描述:
    方向性压力因子,通过计算加权动量(近期权重更高)与简单动量的差异,
    识别近期动量是否与中长期动量存在分歧。当近期压力与历史趋势方向
    相反或显著强于历史时,预示趋势可能反转或加速。

    核心思想:
    1. 计算线性加权动量(近期收益率权重更大)
    2. 计算简单平均动量作为基准
    3. 两者差值反映近期动量相对历史的强度变化
    4. 用短期波动率标准化,使不同币种可比

参数:
    short_period: 12 (1小时, 用于波动率计算)
    long_period: 48 (4小时, 用于动量计算窗口)

计算公式:
    weighted_return = Σ(return_i * weight_i) / Σ(weight_i), where weight_i = i (线性递增)
    simple_return = mean(return over long_period)
    pressure = (weighted_return - simple_return) / rolling_std(return, short_period)

输出:
    因子值DataFrame,正值表示近期动量强于历史,负值表示近期动量弱于历史

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Directional Pressure因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 12  # 1小时,用于波动率计算
    long_period = 48   # 4小时,用于动量计算窗口

    # 计算收益率
    returns = close.pct_change()

    # 计算短期波动率(用于标准化)
    volatility = returns.rolling(short_period).std()

    # 计算线性加权动量
    # 权重为1,2,3,...,long_period (近期权重更大)
    weights = np.arange(1, long_period + 1, dtype=float)
    weight_sum = weights.sum()

    def weighted_mean(x):
        if len(x) < long_period:
            return np.nan
        return np.sum(x * weights) / weight_sum

    weighted_return = returns.rolling(long_period).apply(weighted_mean, raw=True)

    # 计算简单平均动量
    simple_return = returns.rolling(long_period).mean()

    # 计算压力差异(近期相对历史的强度变化)
    pressure_diff = weighted_return - simple_return

    # 用波动率标准化
    factor = pressure_diff / volatility

    # 处理极端值
    factor = factor.replace([np.inf, -np.inf], np.nan)

    return factor
