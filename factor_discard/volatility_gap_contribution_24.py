"""
Volatility类因子 - Gap Contribution

因子描述:
    计算隔夜/K线间跳空波动对总波动的贡献占比。
    Sum(Gap^2) / Sum(Ret^2)
    
    Gap = Open - Close_prev
    Ret = Close - Close_prev
    
    原理：
    衡量由于不连续跳空引起的价格变动占总变动的比例。
    高Gap占比意味着价格主要通过跳空变动（低流动性或消息驱动）。
    低Gap占比意味着价格主要在盘中连续变动。

参数:
    period: 24 (2小时)

计算公式:
    Gap_t = log(Open_t / Close_{t-1})
    Ret_t = log(Close_t / Close_{t-1})
    Factor = Sum(Gap_t^2, 24) / Sum(Ret_t^2, 24)

输出:
    因子值DataFrame (0 to 1)

数据依赖:
    - open: 开盘价 (必需)
    - close: 收盘价 (必需)

创建日期: 2026-01-02
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Gap贡献度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    open_price = data['open']
    close = data['close']
    
    period = 24

    # Gap: Open / Prev Close
    gap = np.log(open_price / close.shift(1))
    
    # Total Return: Close / Prev Close
    ret = np.log(close / close.shift(1))
    
    # Squared
    gap_sq = gap ** 2
    ret_sq = ret ** 2
    
    # Rolling Sum
    gap_sum = gap_sq.rolling(window=period).sum()
    ret_sum = ret_sq.rolling(window=period).sum()
    
    # Ratio
    # Handle div by zero
    ret_sum = ret_sum.replace(0, np.nan)
    
    factor = gap_sum / ret_sum

    return factor
