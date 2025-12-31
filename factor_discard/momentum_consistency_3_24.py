"""
Momentum指标 - MomConsistency (动量一致性因子)

因子描述:
    动量一致性因子，衡量价格动量方向的一致性程度。核心思想是：
    - 当价格在多个短周期内持续朝同一方向移动（一致性高），趋势更可能延续
    - 当价格在多个短周期内方向反复变化（一致性低），市场处于震荡状态

    本因子计算短期价格变化方向的滚动符号一致性，捕捉趋势的稳定性。

参数:
    step_period: 3 (15分钟, 计算单步动量的周期)
    window_period: 24 (2小时, 计算一致性的滚动窗口)

计算公式:
    1. step_mom = close - close[t-step_period]  # 单步动量
    2. mom_sign = sign(step_mom)  # 动量方向 (+1/-1/0)
    3. consistency = rolling_mean(mom_sign, window_period)  # 方向一致性 (-1到+1)
    4. factor = consistency * abs(consistency)  # 强化极端值

输出:
    因子值DataFrame, 正值表示持续上涨趋势，负值表示持续下跌趋势

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算MomConsistency因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    step_period = 3    # 15分钟
    window_period = 24 # 2小时

    # Step 1: 计算单步动量
    step_mom = close - close.shift(step_period)

    # Step 2: 获取动量方向 (+1/-1/0)
    mom_sign = np.sign(step_mom)

    # Step 3: 计算方向一致性 (滚动窗口内的平均符号)
    # 值域为 -1 到 +1
    # 接近 +1 表示持续上涨，接近 -1 表示持续下跌，接近 0 表示震荡
    consistency = mom_sign.rolling(window_period).mean()

    # Step 4: 强化极端值（非线性变换）
    # 使用 x * |x| 来保持符号但强化极端值
    factor = consistency * consistency.abs()

    return factor
