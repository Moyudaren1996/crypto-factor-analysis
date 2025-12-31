"""
Momentum指标 - Price Acceleration (价格加速度)

因子描述:
    价格加速度因子,捕捉价格动量的加速或减速信号
    核心逻辑: 不是看价格变化(一阶导数),而是看价格变化的变化(二阶导数)
    正向加速(动量加强)预示趋势延续
    负向加速(动量减弱)预示趋势反转
    使用EMA平滑,减少噪音

参数:
    short_period: 3 (15分钟,短期动量)
    long_period: 12 (1小时,长期动量)
    smooth_period: 6 (30分钟,平滑)

计算公式:
    1. short_mom = (close - close[t-3]) / close[t-3]
       短期动量(15分钟)
    2. long_mom = (close - close[t-12]) / close[t-12]
       长期动量(1小时)
    3. mom_change = short_mom - short_mom[t-3]
       动量变化(加速度)
    4. acceleration = EMA(mom_change, 6)
       平滑后的加速度
    5. factor = acceleration * abs(long_mom)
       加速度加权: 加速度方向 × 趋势强度

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-07
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算价格加速度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 3  # 短期动量周期: 15分钟
    long_period = 12  # 长期动量周期: 1小时
    smooth_period = 6  # 平滑周期: 30分钟
    accel_period = 3  # 加速度计算周期: 15分钟

    # 1. 计算短期动量
    short_mom = (close - close.shift(short_period)) / close.shift(short_period)

    # 2. 计算长期动量(用于判断趋势强度)
    long_mom = (close - close.shift(long_period)) / close.shift(long_period)

    # 3. 计算动量变化(加速度)
    # 短期动量的变化 = 当前短期动量 - N期前短期动量
    mom_change = short_mom - short_mom.shift(accel_period)

    # 4. 平滑加速度,减少噪音
    acceleration = mom_change.ewm(span=smooth_period, adjust=False).mean()

    # 5. 加速度加权: 加速度方向 × 趋势绝对强度
    # 当趋势强且加速时,因子值大
    # 当趋势强但减速时,因子值小(可能反转)
    factor = acceleration * np.abs(long_mom)

    return factor
