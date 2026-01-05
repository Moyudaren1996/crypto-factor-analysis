"""
Momentum指标 - PPO (Percentage Price Oscillator)

因子描述:
    价格震荡百分比，MACD的百分比版本

参数:
    fast: 3, slow: 6, signal: 2

计算公式:
    PPO = ((EMA(close, fast) - EMA(close, slow)) / EMA(close, slow)) * 100
    Signal = EMA(PPO, signal)
    输出PPO线

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算PPO因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值 (PPO线)
    """
    close = data['close']

    fast = 3
    slow = 6
    signal = 2

    # 计算快慢EMA
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()

    # 计算PPO
    ppo = ((ema_fast - ema_slow) / ema_slow) * 100

    return ppo
