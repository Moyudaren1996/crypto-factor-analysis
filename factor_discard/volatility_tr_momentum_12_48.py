"""
Volatility指标 - TRMomentum (真实波幅动量因子)

因子描述:
    真实波幅动量因子,基于TR(True Range)的短期动量变化来预测反转。
    核心思想:
    - TR快速增加后通常会均值回归
    - TR的短期相对于长期的比值反映波动率状态
    - 结合TR变化的方向性(上涨/下跌时TR)来增强信号

    这个因子直接使用TR的相对变化,避免复杂的变换。

参数:
    short_period: 12 (1小时)
    long_period: 48 (4小时)

计算公式:
    1. TR = max(high-low, |high-prev_close|, |low-prev_close|)
    2. 短期TR均值: tr_short = rolling_mean(TR, short_period)
    3. 长期TR均值: tr_long = rolling_mean(TR, long_period)
    4. TR比率: tr_ratio = tr_short / tr_long
    5. 价格变化方向: price_direction = sign(close - close.shift(short_period))
    6. 结合方向的TR比率: directed_tr = tr_ratio * price_direction
    7. 历史百分位排名: factor = -rolling_rank(directed_tr, long_period)
       (TR比率高+上涨 -> 因子为负 -> 预示下跌反转)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算真实波幅动量因子

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
    short_period = 12   # 1小时
    long_period = 48    # 4小时
    rank_period = 72    # 6小时排名窗口

    # 计算True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = tr1.combine(tr2, np.maximum).combine(tr3, np.maximum)

    # 短期和长期TR均值
    tr_short = tr.rolling(short_period).mean()
    tr_long = tr.rolling(long_period).mean()

    # TR比率 (短期相对长期)
    tr_ratio = tr_short / tr_long

    # 价格变化方向
    price_change = close - close.shift(short_period)
    price_direction = np.sign(price_change)

    # 结合方向的TR比率
    # 上涨时TR高 -> 正值(较大), 下跌时TR高 -> 负值(绝对值较大)
    directed_tr = tr_ratio * price_direction

    # 转换为历史百分位排名
    def rank_pct(x):
        return x.rank(pct=True)

    factor_rank = directed_tr.rolling(rank_period).apply(lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False)

    # 取负值: 极端正值(上涨+高TR) -> 预示下跌反转
    factor = -factor_rank

    return factor
