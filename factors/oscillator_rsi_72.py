"""
Oscillator指标 - RSI (Relative Strength Index)

因子描述:
    相对强弱指数，衡量价格变动速度和变化的动量振荡器

参数:
    length: 72

计算公式:
    delta = close.diff()
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)
    avg_gain = gain.ewm(alpha=1/length, min_periods=length).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length).mean()
    RS = avg_gain / avg_loss
    RSI = 100 - (100 / (1 + RS))

输出:
    因子值DataFrame (0-100)

数据依赖:
    - close: 收盘价

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算RSI因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    length = 72

    # 计算价格变化
    delta = close.diff()

    # 分离涨跌
    gain = delta.where(delta > 0, 0)
    loss = (-delta).where(delta < 0, 0)

    # 使用EMA计算平均涨跌幅（与pandas_ta一致）
    avg_gain = gain.ewm(alpha=1/length, min_periods=length, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/length, min_periods=length, adjust=False).mean()

    # 计算RS和RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
