"""
Oscillator指标 - 成交量反转确认因子

因子描述:
    基于成交量异常与价格动量的反转因子。当价格上升幅度大但成交量衰减时，或价格下跌
    幅度大但成交量放大时，识别反转机会。该因子结合价格动量和成交量强度的背离特征，
    捕捉动量虚弱的反转信号。

参数:
    momentum_period: 6 (30分钟)
    volume_period: 12 (60分钟)

计算公式:
    roc = close.pct_change(6)
    volume_ma = volume.rolling(12).mean()
    volume_ratio = volume / (volume_ma + 1e-8)

    # 成交量标准化强度
    vol_strength = (volume_ratio - 1)

    # 动量与成交量背离：强动量+弱成交量 或 弱动量+强成交量
    divergence = roc - (0.1 * vol_strength)

    # 反向动量（反转信号）
    factor = -divergence

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-26
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量反转确认因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    momentum_period = 6   # 30分钟
    volume_period = 12    # 60分钟

    # 计算价格动量
    roc = close.pct_change(momentum_period)

    # 计算成交量强度
    volume_ma = volume.rolling(volume_period).mean()
    volume_ratio = volume / (volume_ma + 1e-8)

    # 成交量异常度 (ratio > 1 = 放量，ratio < 1 = 缩量)
    vol_strength = volume_ratio - 1

    # 核心逻辑：动量与成交量背离识别反转
    # 强上涨但缩量 = 虚弱的上涨 = 反转信号（负值）
    # 强下跌但放量 = 真实的下跌 = 延续信号（正值）
    # 因此用 -roc 来表示反转
    divergence = roc - (0.15 * vol_strength)

    # 反向因子：反转信号
    factor = -divergence

    return factor
