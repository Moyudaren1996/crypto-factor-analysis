"""
Trend指标 - Vortex Indicator (涡旋指标)

因子描述:
    涡旋指标，用于识别趋势的开始和方向

参数:
    length: 3 (15分钟)

计算公式:
    VM+ = |high - low.shift(1)|
    VM- = |low - high.shift(1)|
    TR = max(high-low, |high-close.shift(1)|, |low-close.shift(1)|)
    VIP = Sum(VM+, length) / Sum(TR, length)
    VIM = Sum(VM-, length) / Sum(TR, length)
    输出VIP (正向涡旋)

输出:
    因子值DataFrame (VIP)

数据依赖:
    - high, low, close

创建日期: 2024-12-01
版本: v2.0 (纯pandas实现)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Vortex Indicator因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值 (VIP)
    """
    high = data['high']
    low = data['low']
    close = data['close']

    length = 3

    # 计算VM+ 和 VM-
    vm_plus = (high - low.shift(1)).abs()
    vm_minus = (low - high.shift(1)).abs()

    # 计算True Range
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    tr = pd.DataFrame(np.maximum(np.maximum(tr1.values, tr2.values), tr3.values),
                       index=close.index, columns=close.columns)

    # 计算VIP和VIM
    sum_vm_plus = vm_plus.rolling(window=length).sum()
    sum_vm_minus = vm_minus.rolling(window=length).sum()
    sum_tr = tr.rolling(window=length).sum()

    vip = sum_vm_plus / sum_tr

    return vip
