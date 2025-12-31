"""
Volatility指标 - Range Deviation (波动率偏离因子)

因子描述:
    衡量当前波动率相对于历史均值的偏离程度及其变化趋势。
    计算高低价范围相对于EMA范围的比率,然后测量该比率的动量变化。
    当波动率快速扩张后偏离历史均值过远时,预示均值回归的反转机会。

    核心逻辑:
    1. 计算日内波幅(high-low)的EMA作为基准波动率
    2. 计算当前波幅与EMA波幅的比率(标准化波幅)
    3. 计算该比率的短期变化率(波动率动量)
    4. 用时序百分位排名识别极端情况

参数:
    short_period: 24 (2小时,短期波动率)
    long_period: 72 (6小时,长期基准)

计算公式:
    range = high - low
    range_ema = EMA(range, long_period)
    range_ratio = range / range_ema
    range_ratio_ma = SMA(range_ratio, short_period)
    range_mom = range_ratio - range_ratio_ma
    factor = rolling_rank(range_mom, long_period)

输出:
    因子值DataFrame,值越高表示波动率正在快速扩张

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需,用于方向判断)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率偏离因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 24  # 2小时
    long_period = 72   # 6小时

    # 计算日内波幅
    price_range = high - low

    # 计算波幅的EMA作为基准
    range_ema = price_range.ewm(span=long_period, adjust=False).mean()

    # 计算标准化波幅比率
    range_ratio = price_range / range_ema.replace(0, np.nan)

    # 计算比率的短期均值
    range_ratio_ma = range_ratio.rolling(short_period).mean()

    # 计算波动率动量(当前比率偏离均值的程度)
    range_mom = range_ratio - range_ratio_ma

    # 用时序百分位排名标准化
    factor = range_mom.rolling(long_period).rank(pct=True)

    # 结合价格方向：当价格上涨但波动率扩张过快时预示反转
    price_direction = np.sign(close - close.shift(short_period))

    # 最终因子：波动率扩张方向与价格方向的组合
    # 波动率快速扩张(factor高)且价格单边运动时,反转机会更大
    factor = factor * price_direction

    return factor
