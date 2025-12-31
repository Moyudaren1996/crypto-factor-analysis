"""
Volatility指标 - Range Volatility Dispersion (波幅波动率离散因子)

因子描述:
    衡量高低波幅波动率与收盘价波动率之间的离散程度。

    核心逻辑:
    1. 使用Parkinson波动率(基于高低价)和标准收益率波动率
    2. 当这两种波动率差异增大时,表明市场结构发生变化
    3. 差异扩大且Parkinson>收益率波动率,表明日内波动增加但收盘持平(震荡)
    4. 差异扩大且Parkinson<收益率波动率,表明跳空/缺口行情

参数:
    period: 48 (4小时)
    lookback: 96 (8小时历史分位)

计算公式:
    1. parkinson_vol = sqrt(rolling_mean((log(high/low))^2, period) / (4*ln2))
    2. close_vol = rolling_std(log(close/prev_close), period)
    3. vol_dispersion = (parkinson_vol - close_vol) / (parkinson_vol + close_vol)
    4. factor = rolling_rank(vol_dispersion, lookback, pct=True) - 0.5

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
    计算Range Volatility Dispersion因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 参数
    period = 48    # 4小时
    lookback = 96  # 8小时

    # Parkinson波动率 (基于高低价)
    log_hl = np.log(high / low)
    parkinson_var = (log_hl ** 2).rolling(period).mean() / (4 * np.log(2))
    parkinson_vol = np.sqrt(parkinson_var)

    # 标准收益率波动率 (基于收盘价)
    log_return = np.log(close / close.shift(1))
    close_vol = log_return.rolling(period).std()

    # 波动率离散度 (归一化)
    vol_dispersion = (parkinson_vol - close_vol) / (parkinson_vol + close_vol + 1e-10)

    # 转换为历史百分位并中心化
    factor = vol_dispersion.rolling(lookback).rank(pct=True) - 0.5

    # 当离散度高(Parkinson>close_vol)且处于历史高位时,预期继续震荡,反转信号
    # 因子值高表示日内波动大但收盘持平,可能有反转

    return factor
