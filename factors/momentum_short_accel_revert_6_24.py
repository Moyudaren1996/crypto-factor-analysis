"""
Momentum指标 - 短期动量加速反转

因子描述:
    短期动量加速反转因子，衡量价格动量的加速度特征。
    基于快速和中等速度的动量变化的差异识别动量过度的反转机会。
    当短期动量强度远超中期动量时，预示反转信号。

参数:
    short_period: 6 (30分钟)
    medium_period: 24 (2小时)

计算公式:
    ShortMom = (close - close[t-6]) / close[t-6]
    MediumMom = (close - close[t-24]) / close[t-24]
    MomAccel = ShortMom - MediumMom/4  (标准化中期动量)
    Factor = MomAccel标准化值

输出:
    因子值DataFrame，表示动量加速的极端程度

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算短期动量加速反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 6        # 6个5分钟K线 = 30分钟
    medium_period = 24      # 24个5分钟K线 = 2小时
    accel_window = 12       # 12个5分钟K线 = 1小时 (加速度窗口)

    # 计算短期动量
    short_mom = (close - close.shift(short_period)) / close.shift(short_period)

    # 计算中期动量
    medium_mom = (close - close.shift(medium_period)) / close.shift(medium_period)

    # 计算动量加速度 (短期相对于中期的超额部分)
    # 将中期动量标准化后再比较
    mom_accel = short_mom - medium_mom / 4.0

    # 计算加速度的移动平均和标准差进行标准化
    accel_ma = mom_accel.rolling(window=accel_window).mean()
    accel_std = mom_accel.rolling(window=accel_window).std()

    # 避免除以0的情况
    accel_std = accel_std.replace(0, np.nan)

    # 标准化的加速度
    mom_accel_normalized = (mom_accel - accel_ma) / accel_std

    # 返回因子值
    return mom_accel_normalized
