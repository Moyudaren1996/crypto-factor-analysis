"""
Momentum指标 - 动量反转力度因子 (Momentum Reversal Strength)

因子描述:
    动量反转力度因子，衡量价格从极端位置反弹或回落的力度。

    核心逻辑：
    1. 计算价格在近期高低区间的相对位置(类似Williams %R)
    2. 计算这个位置的变化速度(位置的一阶导数)
    3. 当位置变化速度极端时(快速从低点反弹或从高点下跌)
    4. 用动量强度标准化后识别反转信号

    与现有因子的区别：
    - Stoch/Williams%R只关注当前位置
    - 本因子关注位置变化的速度和动量

参数:
    hl_period: 24 (2小时，高低价窗口)
    change_period: 6 (30分钟，位置变化周期)
    smooth_period: 12 (1小时，平滑窗口)

计算公式:
    1. highest = high.rolling(hl_period).max()
    2. lowest = low.rolling(hl_period).min()
    3. position = (close - lowest) / (highest - lowest)
    4. position_change = position - position.shift(change_period)
    5. change_ma = position_change.rolling(smooth_period).mean()
    6. change_std = position_change.rolling(smooth_period * 3).std()
    7. factor = change_ma / change_std (标准化的位置变化速度)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算动量反转力度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    hl_period = 24        # 2小时，高低价窗口
    change_period = 6     # 30分钟，位置变化周期
    smooth_period = 12    # 1小时，平滑窗口
    epsilon = 1e-8

    # 计算滚动最高价和最低价
    highest = high.rolling(hl_period).max()
    lowest = low.rolling(hl_period).min()

    # 计算价格在高低区间的相对位置 (0-1范围)
    hl_range = highest - lowest
    hl_range = hl_range.replace(0, np.nan)
    position = (close - lowest) / (hl_range + epsilon)

    # 计算位置变化速度
    position_change = position - position.shift(change_period)

    # 平滑处理
    change_ma = position_change.rolling(smooth_period).mean()

    # 计算位置变化的波动率
    change_std = position_change.rolling(smooth_period * 3).std()
    change_std = change_std.replace(0, np.nan)

    # 标准化的位置变化速度 (Z-score形式)
    z_score = change_ma / (change_std + epsilon)

    # 转换为时序百分位排名，减少极端值
    factor = z_score.rolling(hl_period * 2).rank(pct=True)

    # 中心化到[-0.5, 0.5]
    factor = factor - 0.5

    # 负向因子：快速上涨(高z_score)后可能反转向下
    factor = -factor

    return factor
