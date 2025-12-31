"""
Momentum指标 - 动量加速反转因子 (Momentum Acceleration Reversal)

因子描述:
    捕捉动量变化的加速度,当价格动量突然加速时识别反转机会。
    核心思想：短期动量的加速度(二阶导数)过大时,往往预示着过度反应,
    随后可能出现反转。

    计算方法：
    1. 计算价格的短期收益率变化(一阶导数)
    2. 计算收益率变化的变化(二阶导数,即加速度)
    3. 当加速度极端时(突然加速上涨/下跌),取反向信号
    4. 用短期波动率标准化

参数:
    mom_period: 12 (1小时，动量计算周期)
    accel_period: 6 (30分钟，加速度计算周期)
    vol_period: 48 (4小时，波动率标准化周期)

计算公式:
    momentum = close.pct_change(mom_period)  # 收益率
    accel = momentum.diff(accel_period)  # 动量变化（加速度）
    vol = close.pct_change().rolling(vol_period).std()  # 波动率
    factor = -accel / vol  # 取反作为反转信号

输出:
    因子值DataFrame，正值预期上涨，负值预期下跌

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算动量加速反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    mom_period = 12    # 1小时
    accel_period = 6   # 30分钟
    vol_period = 48    # 4小时

    # 计算收益率（一阶导数）
    momentum = close.pct_change(mom_period)

    # 计算动量的变化（二阶导数，即加速度）
    acceleration = momentum.diff(accel_period)

    # 计算短期波动率用于标准化
    returns = close.pct_change()
    volatility = returns.rolling(vol_period).std()

    # 取反作为反转信号：当加速度大时（突然加速上涨），预期回调
    factor = -acceleration / volatility.replace(0, np.nan)

    return factor
