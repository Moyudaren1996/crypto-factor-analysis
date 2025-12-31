"""
Volatility指标 - ExtremeReversion (波动率极值回归)

因子描述:
    波动率极值回归因子,利用波动率在历史分布中的极端位置识别反转机会。
    当短期波动率相对于中期波动率处于历史极端值时(高分位或低分位),
    预期波动率会向均值回归,同时结合价格位置识别反转信号。

参数:
    short_period: 12 (1小时) - 短期波动率周期
    long_period: 72 (6小时) - 长期波动率及历史分位计算周期

计算公式:
    1. short_vol = returns.rolling(short_period).std() - 短期已实现波动率
    2. long_vol = returns.rolling(long_period).std() - 长期已实现波动率
    3. vol_ratio = short_vol / long_vol - 波动率比值
    4. vol_percentile = vol_ratio在long_period内的百分位排名
    5. price_position = (close - close.rolling(long_period).min()) /
                       (close.rolling(long_period).max() - close.rolling(long_period).min())
    6. extreme_signal = abs(vol_percentile - 0.5) * 2 - 极端程度(0-1)
    7. factor = extreme_signal * (price_position - 0.5) - 波动极端+价格极端时信号最强

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率极值回归因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 12  # 1小时
    long_period = 72   # 6小时

    # 计算收益率
    returns = close.pct_change()

    # 短期和长期已实现波动率
    short_vol = returns.rolling(short_period).std()
    long_vol = returns.rolling(long_period).std()

    # 波动率比值
    vol_ratio = short_vol / long_vol.replace(0, np.nan)

    # 波动率比值的历史分位数 (0-1)
    vol_percentile = vol_ratio.rolling(long_period).rank(pct=True)

    # 价格在历史区间的相对位置 (0-1)
    rolling_max = close.rolling(long_period).max()
    rolling_min = close.rolling(long_period).min()
    price_range = rolling_max - rolling_min
    price_position = (close - rolling_min) / price_range.replace(0, np.nan)

    # 计算极端程度: 距离0.5越远越极端 (0-1)
    vol_extreme = np.abs(vol_percentile - 0.5) * 2

    # 结合波动率极端和价格位置
    # 高波动+高价格位置 -> 正向极端 (预期下跌)
    # 高波动+低价格位置 -> 负向极端 (预期上涨)
    # 组合信号: 波动极端时,价格位置决定方向
    factor = vol_extreme * (price_position - 0.5) * 2

    # 负向因子: 高价格位置时预期下跌(负收益),低价格位置时预期上涨(正收益)
    factor = -factor

    return factor
