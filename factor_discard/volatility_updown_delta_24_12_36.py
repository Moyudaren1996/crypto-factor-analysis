"""
Volatility指标 - UpDownDelta (上下行波动率变化差因子)

因子描述:
    衡量上行波动率与下行波动率各自变化趋势的差异。
    - 上行波动率：正收益率的平方和（衡量上涨幅度）
    - 下行波动率：负收益率的平方和（衡量下跌幅度）

    本因子计算两者变化速度的差异：
    当上行波动率增速超过下行波动率增速时，因子值为正；
    反之为负。这捕捉了市场风险偏好的动态变化。

参数:
    calc_period: 24 (2小时) - 波动率计算窗口
    diff_period: 12 (1小时) - 变化率计算窗口
    smooth_period: 36 (3小时) - 平滑窗口

计算公式:
    up_vol = 正收益率平方的滚动和
    down_vol = 负收益率平方的滚动和
    up_change = (up_vol - up_vol.shift(diff)) / up_vol.shift(diff)
    down_change = (down_vol - down_vol.shift(diff)) / down_vol.shift(diff)
    delta = up_change - down_change
    factor = delta.rolling(smooth).mean()

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
    计算UpDownDelta因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    calc_period = 24    # 2小时 - 波动率计算窗口
    diff_period = 12    # 1小时 - 变化率计算窗口
    smooth_period = 36  # 3小时 - 平滑窗口

    # 计算收益率
    returns = close.pct_change()

    # 分离正负收益
    pos_returns = returns.clip(lower=0)
    neg_returns = returns.clip(upper=0)

    # 上行波动率：正收益率平方的滚动和
    up_vol = (pos_returns ** 2).rolling(window=calc_period, min_periods=int(calc_period/2)).sum()

    # 下行波动率：负收益率平方的滚动和
    down_vol = (neg_returns ** 2).rolling(window=calc_period, min_periods=int(calc_period/2)).sum()

    # 计算各自的变化率
    up_vol_prev = up_vol.shift(diff_period)
    down_vol_prev = down_vol.shift(diff_period)

    up_change = (up_vol - up_vol_prev) / (up_vol_prev + 1e-10)
    down_change = (down_vol - down_vol_prev) / (down_vol_prev + 1e-10)

    # 上下行波动率变化速度的差异
    delta = up_change - down_change

    # 平滑处理
    factor = delta.rolling(window=smooth_period, min_periods=int(smooth_period/2)).mean()

    # 截断极端值
    factor = factor.clip(-3, 3)

    return factor
