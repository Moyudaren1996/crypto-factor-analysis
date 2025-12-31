"""
Momentum指标 - RAD (Return Acceleration Dispersion)

因子描述:
    收益率加速度离散因子,通过计算价格收益率的二阶导数(加速度)并用收益率波动性标准化,
    捕捉价格运动的非可持续性。当收益率加速度过大时,预示动量衰竭即将反转。

    核心逻辑:
    1. 计算短期收益率(6期)的变化率(加速度)
    2. 用收益率的滚动标准差标准化,识别异常加速
    3. 取负值:正加速度(加速上涨)预示反转下跌,负加速度(加速下跌)预示反转上涨

    与现有因子的差异:
    - 不同于RSI/Williams(不基于价格在区间的位置)
    - 不同于单纯的ROC(ROC是一阶导数,这是二阶导数)
    - 核心创新:收益率加速度的标准化,捕捉动量衰竭

参数:
    return_period: 6 (30分钟收益率)
    std_period: 24 (2小时标准差窗口)

计算公式:
    1. returns = (close - close.shift(6)) / close.shift(6)    # 6期收益率
    2. acceleration = returns - returns.shift(6)               # 收益率加速度
    3. returns_std = returns.rolling(24).std()                 # 收益率波动性
    4. factor = -(acceleration / (returns_std + 1e-6))         # 标准化加速度,取负值

    解释:
    - acceleration > 0表示收益率在增加(加速上涨或减速下跌)
    - acceleration < 0表示收益率在减少(减速上涨或加速下跌)
    - 通过标准化消除不同币种波动率差异
    - 取负值:加速上涨(acceleration>0)预示反转下跌,因子值为负(看跌)
    - 加速下跌(acceleration<0)预示反转上涨,因子值为正(看涨)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-15
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算RAD因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    # 定义参数
    return_period = 6   # 收益率周期(30分钟)
    std_period = 24     # 标准差窗口(2小时)

    # 1. 计算收益率
    returns = (close - close.shift(return_period)) / close.shift(return_period)

    # 2. 计算收益率的加速度(收益率的变化率)
    acceleration = returns - returns.shift(return_period)

    # 3. 计算收益率的滚动标准差(用于标准化)
    returns_std = returns.rolling(std_period).std()

    # 4. 标准化加速度
    normalized_accel = acceleration / (returns_std + 1e-6)

    # 5. 取负值作为反转因子
    # 正加速度(加速上涨)预示反转下跌,取负后为负值(看跌)
    # 负加速度(加速下跌)预示反转上涨,取负后为正值(看涨)
    factor = -normalized_accel

    return factor
