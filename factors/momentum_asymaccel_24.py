"""
Momentum指标 - Asymmetric Acceleration Reversal (非对称加速度反转)

因子描述:
    基于价格加速度非对称性的反转因子。分别计算上涨和下跌时的价格加速度,
    当上涨加速度远大于下跌加速度时,暗示市场过度乐观,后续倾向反转。
    核心思想:市场上涨加速但下跌缺乏加速度时,反弹动能不可持续。

参数:
    period: 24 (2小时)

计算公式:
    returns = close.pct_change()
    acceleration = returns.diff()  # 收益率的变化率(加速度)
    up_accel = acceleration.where(acceleration > 0, 0).rolling(period).mean()
    down_accel = acceleration.where(acceleration < 0, 0).abs().rolling(period).mean()
    factor = -(up_accel / (down_accel + 1e-8))  # 取负值,非对称性越高→反转信号越强

输出:
    因子值DataFrame,数值越小表示上涨加速度相对过高,反转信号越强

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-13
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算非对称加速度反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    period = 24

    # 计算收益率
    returns = close.pct_change()

    # 计算加速度(收益率的变化率)
    acceleration = returns.diff()

    # 分别计算上涨和下跌时的加速度均值
    up_accel = acceleration.where(acceleration > 0, 0).rolling(window=period).mean()
    down_accel = acceleration.where(acceleration < 0, 0).abs().rolling(window=period).mean()

    # 计算非对称性比率,取负值作为反转信号
    # 分母加小常数避免除零
    factor = -(up_accel / (down_accel + 1e-8))

    return factor
