"""
Oscillator指标 - PriceExtremeMomentum (价格极值动量反转)

因子描述:
    基于价格在滚动高低点区间的相对位置与其短期动量变化的反转因子。
    当价格触及或接近极端位置（极高或极低）且其动量方向改变时，
    预示反转机会。核心逻辑：价格极端往往是反转的起点。

参数:
    period: 24 (2小时用于计算高低点)
    momentum_period: 3 (15分钟用于计算动量)

计算公式:
    price_position = (close - lowest) / (highest - lowest)  # 0-1标准化
    momentum = close.pct_change(momentum_period)
    momentum_signal = 动量变化率(acceleration)
    factor = price_position极端程度 × 动量方向倒转强度

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算价格极值动量反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']

    period = 24      # 2小时
    momentum_period = 3  # 15分钟

    # 1. 计算价格在滚动高低点的相对位置（0-1）
    high = close.rolling(window=period).max()
    low = close.rolling(window=period).min()
    range_val = high - low
    range_val = range_val.where(range_val != 0, 1)

    price_position = (close - low) / range_val

    # 2. 计算价格极端程度（接近0或1时返回1，中间返回0）
    # 使用二次函数使得极端更明显：-4(x-0.5)^2 + 1
    extremeness = -4 * (price_position - 0.5) ** 2 + 1
    extremeness = extremeness.clip(lower=0)

    # 3. 计算短期动量
    momentum = close.pct_change(momentum_period)

    # 4. 计算动量变化（二阶导数，即加速度）
    momentum_change = momentum.diff()

    # 5. 动量反转信号
    # 当动量变化反向（从正转负或从负转正）时信号强
    momentum_reversal = momentum_change.abs().rolling(window=6).mean()

    # 6. 方向性反转信号
    # 当价格位置极端且动量即将反向时
    # 价格极高(>0.7) + 动量变负 = 看跌
    # 价格极低(<0.3) + 动量变正 = 看涨

    bullish = ((price_position < 0.3) & (momentum > momentum.shift(3))).astype(float)
    bearish = ((price_position > 0.7) & (momentum < momentum.shift(3))).astype(float)

    factor = bullish - bearish

    # 加权合并
    factor = factor * extremeness

    # 平滑
    factor = factor.ewm(span=5, adjust=False).mean()

    factor = factor.fillna(0)

    return factor
