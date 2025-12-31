"""
Momentum指标 - BreakoutVelocity (突破速度动量因子)

因子描述:
    衡量价格突破近期高低点的速度和强度。当价格快速突破近期高点时,
    表明动量过强,可能过度扩张,预示反转;反之亦然。

    核心逻辑:
    1. 计算价格相对于近期高低区间的位置 (类似Williams %R)
    2. 计算该位置的变化速度 (一阶导数)
    3. 当变化速度极端时,表明突破过于激进,可能反转

参数:
    range_period: 24 (2小时) - 计算高低区间的周期
    velocity_period: 6 (30分钟) - 计算速度的周期
    smooth_period: 3 (15分钟) - 平滑参数

计算公式:
    1. highest = close.rolling(range_period).max()
    2. lowest = close.rolling(range_period).min()
    3. position = (close - lowest) / (highest - lowest) # 0-1之间
    4. velocity = position.diff(velocity_period) # 位置变化速度
    5. factor = velocity.ewm(span=smooth_period).mean() # 平滑后的速度

输出:
    因子值DataFrame,高正值表示快速向上突破(预期反转向下)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算突破速度动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    range_period = 24     # 2小时
    velocity_period = 6   # 30分钟
    smooth_period = 3     # 15分钟

    # 计算滚动高低区间
    highest = close.rolling(range_period).max()
    lowest = close.rolling(range_period).min()

    # 计算价格在区间内的相对位置 (0-1之间)
    range_size = highest - lowest
    # 避免除零
    range_size = range_size.replace(0, np.nan)
    position = (close - lowest) / range_size

    # 计算位置的变化速度
    velocity = position.diff(velocity_period)

    # 平滑处理
    factor = velocity.ewm(span=smooth_period, adjust=False).mean()

    return factor
