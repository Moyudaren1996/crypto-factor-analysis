"""
Volatility指标 - ATRRatio (ATR比率因子)

因子描述:
    ATR比率因子,衡量短期波动率相对于长期波动率的扩张或收缩程度。
    计算短期ATR与长期ATR的比率,并转换为时序Z-score。

    当短期波动率相对于长期波动率处于极端高位(Z-score高)时,
    表明波动率可能过度扩张,存在均值回归的可能性。

    结合横截面排名,识别波动率异常扩张的币种。

参数:
    short_atr: 6 (30分钟)
    long_atr: 72 (6小时)
    zscore_period: 48 (4小时)

计算公式:
    1. TR = max(high-low, abs(high-close.shift(1)), abs(low-close.shift(1)))
    2. short_atr = TR.rolling(short_atr_period).mean()
    3. long_atr = TR.rolling(long_atr_period).mean()
    4. atr_ratio = short_atr / long_atr
    5. zscore = (atr_ratio - atr_ratio.rolling(zscore_period).mean()) / atr_ratio.rolling(zscore_period).std()
    6. cross_rank = zscore.rank(axis=1, pct=True)
    7. factor = zscore * (cross_rank - 0.5)  # 高波动率扩张币种权重更高

输出:
    因子值DataFrame

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算ATRRatio因子

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
    short_atr_period = 6   # 30分钟
    long_atr_period = 72   # 6小时
    zscore_period = 48     # 4小时

    # 计算True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()

    # 使用numpy maximum来计算True Range
    tr = np.maximum(np.maximum(tr1, tr2), tr3)

    # 计算短期和长期ATR
    short_atr = tr.rolling(short_atr_period).mean()
    long_atr = tr.rolling(long_atr_period).mean()

    # 计算ATR比率
    atr_ratio = short_atr / (long_atr + 1e-10)

    # 计算时序Z-score
    ratio_mean = atr_ratio.rolling(zscore_period).mean()
    ratio_std = atr_ratio.rolling(zscore_period).std()
    zscore = (atr_ratio - ratio_mean) / (ratio_std + 1e-10)

    # 横截面排名加权 (高扩张币种权重更高)
    cross_rank = zscore.rank(axis=1, pct=True)

    # 因子值: 波动率扩张极端时做空(取负值)
    factor = -zscore * (cross_rank - 0.5) * 2

    return factor
