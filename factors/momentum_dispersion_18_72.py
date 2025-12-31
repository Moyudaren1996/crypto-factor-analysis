"""
Momentum指标 - MomentumDispersion (动量离散度)

因子描述:
    动量离散度因子，衡量个币种动量相对于市场整体动量的离散程度。
    不同于传统的价格偏离或RSI类因子，本因子关注的是动量在横截面上的
    相对分布特征。计算步骤：
    1. 计算每个币种的短期动量
    2. 计算市场平均动量（所有币种的均值）
    3. 计算个币种动量偏离市场平均的程度
    4. 用滚动窗口内的动量波动标准化

    当某币种动量显著偏离市场整体动量时，可能存在反转机会。

参数:
    momentum_period: 18 (1.5小时，动量计算周期)
    std_period: 72 (6小时，标准化窗口)

计算公式:
    1. individual_momentum = pct_change(close, momentum_period)
    2. market_momentum = cross_sectional_mean(individual_momentum)
    3. momentum_deviation = individual_momentum - market_momentum
    4. momentum_vol = rolling_std(individual_momentum, std_period)
    5. factor = momentum_deviation / momentum_vol

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算MomentumDispersion因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    momentum_period = 18   # 动量计算周期 (1.5小时)
    std_period = 72        # 标准化窗口 (6小时)

    # 计算个币种动量
    individual_momentum = close.pct_change(momentum_period)

    # 计算市场平均动量 (横截面均值)
    market_momentum = individual_momentum.mean(axis=1)

    # 计算动量偏离 (个币种动量 - 市场平均动量)
    momentum_deviation = individual_momentum.sub(market_momentum, axis=0)

    # 计算动量波动率 (滚动标准差)
    momentum_vol = individual_momentum.rolling(std_period).std()
    momentum_vol = momentum_vol.replace(0, np.nan)

    # 标准化的动量偏离度
    factor = momentum_deviation / momentum_vol

    return factor
