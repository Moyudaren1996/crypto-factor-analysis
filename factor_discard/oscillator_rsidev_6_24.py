"""
Oscillator指标 - RSI Deviation Reversal

因子描述:
    RSI偏离反转因子
    计算短期RSI相对于其移动平均的偏离度
    RSI超买但偏离加剧时产生反转做空信号
    RSI超卖但偏离加剧时产生反转做多信号

参数:
    rsi_period: 6 (30分钟,计算RSI)
    ma_period: 24 (2小时,计算RSI的移动平均)

计算公式:
    1. gains = Max(close - close.shift(1), 0)
    2. losses = Max(close.shift(1) - close, 0)
    3. avg_gain = EMA(gains, 6)
    4. avg_loss = EMA(losses, 6)
    5. rs = avg_gain / (avg_loss + eps)
    6. rsi = 100 - 100 / (1 + rs)  # RSI指标,0-100
    7. rsi_ma = SMA(rsi, 24)  # RSI的移动平均
    8. rsi_deviation = rsi - rsi_ma  # RSI偏离度
    9. factor = -rsi_deviation  # 取负:RSI高于均值(超买)时为负(反转做空信号反向)

输出:
    因子值DataFrame,正值表示RSI低于均值且加剧(超卖反转做多),负值表示RSI高于均值且加剧(超买反转做空)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-13
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算RSI偏离反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']

    # 定义参数
    rsi_period = 6   # 30分钟,计算RSI
    ma_period = 24   # 2小时,计算RSI均值

    # 1. 计算价格变化
    price_change = close.diff()

    # 2. 分离涨跌幅
    gains = price_change.where(price_change > 0, 0)  # 上涨时保留,否则为0
    losses = (-price_change).where(price_change < 0, 0)  # 下跌时保留绝对值,否则为0

    # 3. 计算平均涨跌幅(使用EMA)
    avg_gain = gains.ewm(span=rsi_period, adjust=False).mean()
    avg_loss = losses.ewm(span=rsi_period, adjust=False).mean()

    # 4. 计算RS和RSI
    rs = avg_gain / (avg_loss + 1e-8)
    rsi = 100 - 100 / (1 + rs)  # RSI公式,结果在0-100之间

    # 5. 计算RSI的移动平均
    rsi_ma = rsi.rolling(ma_period).mean()

    # 6. 计算RSI偏离度
    rsi_deviation = rsi - rsi_ma
    # RSI > rsi_ma(超买):deviation为正
    # RSI < rsi_ma(超卖):deviation为负

    # 7. 反转信号:取负值
    # 超买时(RSI高),deviation正,取负后为负值(做空信号)
    # 超卖时(RSI低),deviation负,取负后为正值(做多信号)
    factor = -rsi_deviation

    return factor
