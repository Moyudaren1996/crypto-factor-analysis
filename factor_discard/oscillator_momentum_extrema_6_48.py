"""
Oscillator指标 - 短期动量极值反转因子

因子描述:
    基于短期价格动量的极值识别反转机会。当短期动量达到相对极值时，
    预示动量可能减弱或反转。使用百分位数来识别极值，避免使用绝对阈值。
    该因子简单稳定，直接捕捉短期动量的均值回归效应。

参数:
    momentum_period: 6 (30分钟) - 短期动量周期
    extreme_lookback: 48 (240分钟) - 动量极值判断窗口
    percentile: 10/90 - 极值分位数

计算公式:
    1. 计算短期动量: momentum = (close - close[t-6]) / close[t-6]
    2. 计算动量的20期百分位排名: percentile_rank = rolling_rank(momentum, 48)
    3. 识别极值: extreme_high = (percentile_rank > 0.90), extreme_low = (percentile_rank < 0.10)
    4. 反转信号: signal = (extreme_low - extreme_high) / 2
    5. 平滑处理

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算短期动量极值反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']

    # 定义参数
    momentum_period = 6      # 30分钟
    extreme_lookback = 48    # 240分钟
    smooth_period = 6        # 平滑周期

    # 1. 计算短期动量（收益率）
    momentum = close.pct_change(momentum_period)

    # 2. 计算动量的百分位排名（在extreme_lookback窗口内）
    # 排名从0到1，低排名表示动量弱，高排名表示动量强
    percentile_rank = momentum.rolling(extreme_lookback).rank(pct=True)

    # 3. 识别极值
    # 当动量排名>0.90时，说明动量处于高位，预示即将回调（看跌）
    # 当动量排名<0.10时，说明动量处于低位，预示即将反弹（看涨）
    extreme_high = (percentile_rank > 0.90).astype(float)   # 看跌信号
    extreme_low = (percentile_rank < 0.10).astype(float)    # 看涨信号

    # 4. 构建因子
    # 正值：看涨（动量极低）
    # 负值：看跌（动量极高）
    factor = extreme_low - extreme_high

    # 5. 平滑处理
    factor = factor.rolling(smooth_period).mean()

    return factor
