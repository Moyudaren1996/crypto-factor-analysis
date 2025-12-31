"""
Volatility指标 - HLAccel (高低价波动加速度)

因子描述:
    高低价波动加速度因子,衡量日内波幅(high-low)变化的二阶导数(加速度)。
    当波动率突然加速扩张时,市场可能处于恐慌或过度反应状态,存在反转机会。
    结合波动率水平的历史分位,识别波动率极端加速时的反转信号。

参数:
    hl_period: 12 (1小时平滑波幅)
    accel_period: 6 (30分钟加速度)
    lookback: 72 (6小时历史分位)

计算公式:
    1. hl_range = (high - low) / close  (标准化波幅)
    2. hl_smooth = hl_range.ewm(hl_period).mean()
    3. hl_velocity = hl_smooth.diff(accel_period)  (速度)
    4. hl_accel = hl_velocity.diff(accel_period)    (加速度)
    5. factor = -hl_accel.rolling(lookback).rank(pct=True)  (取负捕捉反转)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np


def calculate(data):
    """
    计算HLAccel因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    hl_period = 12      # 1小时平滑波幅
    accel_period = 6    # 30分钟计算速度/加速度
    lookback = 72       # 6小时历史分位

    # 计算标准化波幅
    hl_range = (high - low) / close

    # EMA平滑波幅
    hl_smooth = hl_range.ewm(span=hl_period, adjust=False).mean()

    # 计算波幅速度 (一阶导数)
    hl_velocity = hl_smooth.diff(accel_period)

    # 计算波幅加速度 (二阶导数)
    hl_accel = hl_velocity.diff(accel_period)

    # 转换为历史分位数并取负值(捕捉反转)
    accel_rank = hl_accel.rolling(lookback).rank(pct=True)

    # 因子: 波动加速度极端时的反转信号
    # 高加速度(波动率快速扩张) -> 预期回落,做空
    # 低加速度(波动率快速收缩) -> 预期扩张,做多
    factor = -(accel_rank - 0.5) * 2  # 映射到 [-1, 1]

    return factor
