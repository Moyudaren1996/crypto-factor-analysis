"""
Momentum指标 - Path Efficiency Momentum (路径效率动量因子)

因子描述:
    路径效率动量因子，衡量价格运动的效率和方向性强度。

    核心思想：
    - 直线距离 vs 实际路径：从A点到B点，直线距离与实际走过的路径之比
    - 如果价格从100涨到110，直线距离是10
    - 但如果中间经历了多次上下波动，实际路径可能是50
    - 效率 = 10/50 = 0.2，低效率意味着趋势不稳定

    应用于动量：
    - 高效率的动量更可能持续（趋势延续）
    - 低效率但方向不变的动量可能反转（震荡后的突破）

    本因子计算：
    - 短周期(24期)的路径效率和动量方向
    - 与长周期(96期)效率的比较
    - 效率突然提升时表明趋势可能形成

参数:
    short_period: 24 (2小时)
    long_period: 96 (8小时)

计算公式:
    # 净移动距离
    net_move = close - close.shift(N)

    # 累计移动路径（每根K线的绝对变化之和）
    abs_path = abs(close.diff()).rolling(N).sum()

    # 路径效率 [-1, 1]
    path_efficiency = net_move / abs_path

    # 短期效率 vs 长期效率的差异
    efficiency_momentum = short_efficiency - long_efficiency

    # 结合价格动量方向
    factor = efficiency_momentum * sign(short_move)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Path Efficiency Momentum因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 24  # 2小时
    long_period = 96   # 8小时

    # 计算每根K线的价格变化绝对值
    price_change = close.diff()
    abs_change = price_change.abs()

    # 短周期路径效率
    short_net_move = close - close.shift(short_period)
    short_abs_path = abs_change.rolling(short_period, min_periods=short_period//2).sum()
    short_abs_path_safe = short_abs_path.replace(0, np.nan)
    short_efficiency = short_net_move / short_abs_path_safe

    # 长周期路径效率
    long_net_move = close - close.shift(long_period)
    long_abs_path = abs_change.rolling(long_period, min_periods=long_period//2).sum()
    long_abs_path_safe = long_abs_path.replace(0, np.nan)
    long_efficiency = long_net_move / long_abs_path_safe

    # 效率变化动量：短期效率 - 长期效率
    # 当短期效率显著高于长期效率时，表明趋势正在形成
    efficiency_momentum = short_efficiency - long_efficiency

    # 结合短期价格动量的方向
    # 效率提升且方向为正 -> 正值（看涨）
    # 效率提升且方向为负 -> 负值（看跌）
    price_direction = np.sign(short_net_move)

    # 综合因子
    factor = efficiency_momentum * price_direction.abs()  # 使用abs确保方向一致性

    # 也可以直接使用efficiency_momentum，因为它已经包含方向信息
    # 这里选择直接返回efficiency_momentum
    factor = efficiency_momentum

    return factor
