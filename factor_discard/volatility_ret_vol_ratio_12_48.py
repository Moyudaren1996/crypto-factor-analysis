"""
Volatility指标 - Return Volatility Ratio (收益波动率比率因子)

因子描述:
    收益波动率比率因子，衡量价格收益率与波动率的关系。
    核心思想：当收益率相对波动率过高时（收益率超出波动率预期），
    意味着价格变动缺乏波动率支持，容易出现均值回归。

    计算方式：用累积收益率除以同期已实现波动率，
    再转换为历史百分位排名，识别极端收益率/波动率比值的反转机会。

参数:
    short_period: 12 (1小时收益计算窗口)
    vol_period: 48 (4小时波动率计算窗口)

计算公式:
    1. 计算累积收益率: cum_ret = close.pct_change().rolling(short_period).sum()
    2. 计算已实现波动率: rv = returns.rolling(vol_period).std() * sqrt(vol_period)
    3. 计算收益波动率比: ret_vol_ratio = cum_ret / rv
    4. 计算历史百分位排名: rank = ret_vol_ratio.rolling(vol_period).rank(pct=True)
    5. 转换为因子值: factor = -(rank - 0.5) * 2
    排名接近1时因子为负（做空），排名接近0时因子为正（做多）

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
    计算收益波动率比率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 12   # 1小时
    vol_period = 48     # 4小时

    # 计算收益率
    returns = close.pct_change()

    # 计算累积收益率
    cum_returns = returns.rolling(short_period).sum()

    # 计算已实现波动率（年化）
    rv = returns.rolling(vol_period).std() * np.sqrt(vol_period)

    # 计算收益波动率比
    ret_vol_ratio = cum_returns / rv

    # 计算历史百分位排名
    rank = ret_vol_ratio.rolling(vol_period).rank(pct=True)

    # 转换为因子值: 高排名为负（做空），低排名为正（做多）
    factor = -(rank - 0.5) * 2

    return factor
