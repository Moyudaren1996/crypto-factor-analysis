"""
Volatility指标 - Downside Adjusted Momentum

因子描述:
    基于下行波动率调整的动量因子 (类似Sortino Ratio思路)。
    计算N期动量除以N期下行波动率(Downside Deviation)。
    该因子奖励平稳上涨(低下行波动)的资产，惩罚平稳下跌的资产。
    相比普通动量，它更看重"稳健性"。

参数:
    period: 24 (2小时)

计算公式:
    r = returns
    r_down = min(r, 0)
    DD = sqrt(Mean(r_down^2, 24))
    Momentum = Close / Close.shift(24) - 1
    Factor = Momentum / (DD + epsilon)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-01-02
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Downside Adjusted Momentum因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    period = 24

    # 计算收益率
    returns = close.pct_change()

    # 计算下行波动率 (Downside Deviation)
    # 只有负收益参与计算，正收益视为0
    r_down = np.minimum(returns, 0)
    r_down_sq = r_down ** 2
    
    # 滚动计算下行均方
    # 注意：这里使用mean而不是sum，保持量纲一致性
    down_ms = r_down_sq.rolling(period).mean()
    dd = np.sqrt(down_ms)

    # 计算动量
    momentum = close / close.shift(period) - 1

    # 计算因子
    # 添加极小值防止除零
    epsilon = 1e-8
    factor = momentum / (dd + epsilon)
    
    # 替换可能产生的无限值
    factor = factor.replace([np.inf, -np.inf], np.nan)

    return factor
