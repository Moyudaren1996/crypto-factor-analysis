"""
Volatility指标 - Range Percentile Momentum (波幅分位动量)

因子描述:
    结合波动率水平和价格在区间内的位置变化,构建一个波动率调整的反转因子。

    核心逻辑:
    1. 计算当前波动率相对历史的分位数(波动率状态)
    2. 计算当前收盘价在短期高低区间的相对位置
    3. 当波动率处于低位时,价格位置的极端值更有可能反转
    4. 当波动率处于高位时,趋势可能延续
    5. 因子 = 价格区间位置 * (1 - 波动率分位数)

    这个因子在低波动率时对价格极端位置给予更高权重,
    在高波动率时权重较低(因为高波动时趋势可能延续)

参数:
    vol_period: 48 (4小时, 用于计算波动率分位数)
    position_period: 24 (2小时, 用于计算价格区间位置)

计算公式:
    returns = close.pct_change()
    realized_vol = rolling_std(returns, vol_period)
    vol_percentile = rolling_rank(realized_vol, vol_period) / vol_period

    rolling_high = rolling_max(high, position_period)
    rolling_low = rolling_min(low, position_period)
    position = (close - rolling_low) / (rolling_high - rolling_low) - 0.5

    factor = position * (1 - vol_percentile)

输出:
    因子值DataFrame,正值表示低波动率环境下价格偏高(可能反转向下)

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
    计算波幅分位动量因子

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
    vol_period = 48      # 4小时
    position_period = 24 # 2小时

    # 计算已实现波动率
    returns = close.pct_change()
    realized_vol = returns.rolling(vol_period).std()

    # 计算波动率在历史中的分位数 (0-1)
    def rolling_percentile_rank(series, window):
        return series.rolling(window).apply(
            lambda x: (x.values[-1] > x.values[:-1]).sum() / (len(x) - 1) if len(x) > 1 else 0.5,
            raw=False
        )

    vol_percentile = realized_vol.rolling(vol_period).rank(pct=True)

    # 计算滚动高低价
    rolling_high = high.rolling(position_period).max()
    rolling_low = low.rolling(position_period).min()

    # 计算价格在区间内的相对位置 (-0.5 到 0.5)
    price_range = rolling_high - rolling_low
    position = (close - rolling_low) / price_range.replace(0, np.nan) - 0.5

    # 因子: 价格位置 * (1 - 波动率分位)
    # 低波动率时权重高,高波动率时权重低
    factor = position * (1 - vol_percentile)

    return factor
