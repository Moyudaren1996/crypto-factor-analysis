"""
Volatility指标 - Inertia (波动率惯性)

因子描述:
    波动率惯性因子,衡量高/低波动率状态的持续性强度。
    核心逻辑:
    - 计算波动率相对于其移动均值的偏离(上方为高波动,下方为低波动)
    - 统计连续处于同一状态(高/低波动)的时间长度
    - 连续高波动越久 -> 预期波动率下降 -> 买入信号
    - 连续低波动越久 -> 预期波动率上升 -> 卖出信号
    - 结合偏离强度和持续时间的乘积

参数:
    atr_period: 6 (30分钟,计算短期波动率)
    ma_period: 36 (3小时,计算波动率均值)
    lookback: 72 (6小时,统计持续性)

计算公式:
    1. TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
    2. ATR = rolling_mean(TR, atr_period)
    3. ATR_ma = rolling_mean(ATR, ma_period)
    4. vol_regime = sign(ATR - ATR_ma)  # +1高波动, -1低波动
    5. regime_duration = 连续同向regime的计数
    6. deviation = (ATR - ATR_ma) / ATR_ma
    7. factor = -deviation * regime_duration  # 负号:高波动+持续久 -> 看涨反转

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率惯性因子

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
    atr_period = 6    # 30分钟,短期波动率
    ma_period = 36    # 3小时,波动率均值
    lookback = 72     # 6小时,统计窗口

    # 计算True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = np.maximum(np.maximum(tr1, tr2), tr3)

    # 计算ATR
    atr = tr.rolling(atr_period).mean()

    # 波动率移动均值
    atr_ma = atr.rolling(ma_period).mean()

    # 波动率偏离度
    deviation = (atr - atr_ma) / atr_ma

    # 波动率区制 (+1高波动, -1低波动)
    vol_regime = np.sign(deviation)

    # 计算区制持续时间
    # 用滚动窗口内同向信号的占比作为持续性度量
    regime_persistence = vol_regime.rolling(lookback).mean()

    # 因子 = 偏离度 × 持续性强度 (取负)
    # 高波动(正偏离) + 高持续性(正) -> 负因子 (预期反转下跌后买入)
    # 改用持续性分位数来标准化
    persistence_pct = regime_persistence.rolling(lookback).rank(pct=True)
    deviation_pct = deviation.rolling(lookback).rank(pct=True)

    # 组合: 当波动率持续偏高且处于历史高位时,预期反转
    factor = -(deviation_pct - 0.5) * (persistence_pct - 0.5) * 4

    return factor
