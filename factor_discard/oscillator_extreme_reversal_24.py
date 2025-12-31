"""
Oscillator指标 - 动量加速度反转因子

因子描述:
    基于价格动量的加速度(二阶导数)识别反转机会。
    当价格动量出现明显减速或加速变化时,往往预示趋势反转。
    核心逻辑：价格的涨跌加速度变负预示上升趋势减弱,
    加速度从负转正预示下降趋势反弹,捕捉动量转折点的反转信号。

参数:
    roc_period: 3 (15分钟)
    accel_period: 12 (60分钟)

计算公式:
    1. roc_3 = (close - close[t-3]) / close[t-3]
    2. roc_accel = roc_3的12期差分(加速度)
    3. factor = roc_accel * (1 - |roc_accel的相对排名 - 0.5| * 2)
       (加速度极端时信号最强,中性时信号最弱)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算动量加速度反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    roc_period = 3
    accel_period = 12

    # 1. 计算短期ROC (3期动量)
    roc = close.pct_change(roc_period)

    # 2. 计算ROC的变化率(加速度)
    roc_accel = roc.diff(accel_period)

    # 3. 计算加速度的相对强度排名
    accel_rank = roc_accel.rolling(accel_period).rank(pct=True)

    # 4. 组合因子：
    # 加速度极端时(排名接近0或1)权重高
    # 加速度为0(中性)时权重低
    extremeness = 1 - np.abs(accel_rank - 0.5) * 2  # 取值0-1，极端为1，中性为0
    factor = roc_accel * extremeness

    return factor
