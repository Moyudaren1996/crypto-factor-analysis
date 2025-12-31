"""
Momentum指标 - CumulativeStrength (动量累积强度因子)

因子描述:
    衡量多时间尺度动量的累积强度和一致性。
    计算3个时间尺度（短/中/长期）的收益率，
    然后计算它们的符号一致性和强度加权和。
    当短中长期动量方向一致且强度都较大时，趋势强；
    当方向不一致或强度减弱时，趋势弱。

    与RSI不同的是，这里直接使用收益率而非涨跌幅比率，
    且关注的是多尺度动量的叠加效应而非超买超卖。

参数:
    short_period: 6 (30分钟) - 短期动量周期
    mid_period: 24 (2小时) - 中期动量周期
    long_period: 72 (6小时) - 长期动量周期

计算公式:
    1. ret_short = close.pct_change(short_period)
    2. ret_mid = close.pct_change(mid_period)
    3. ret_long = close.pct_change(long_period)
    4. consistency = sign(ret_short) + sign(ret_mid) + sign(ret_long)  # 范围[-3, 3]
    5. strength = |ret_short| + |ret_mid| + |ret_long|
    6. factor = consistency * strength  # 一致性 × 强度

输出:
    因子值DataFrame，正值表示上涨趋势强，负值表示下跌趋势强

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.3 - 第3次优化
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算CumulativeStrength因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 6     # 30分钟
    mid_period = 24      # 2小时
    long_period = 72     # 6小时

    # 计算三个时间尺度的收益率
    ret_short = close.pct_change(short_period)
    ret_mid = close.pct_change(mid_period)
    ret_long = close.pct_change(long_period)

    # 计算方向一致性（-3到3之间）
    sign_short = np.sign(ret_short)
    sign_mid = np.sign(ret_mid)
    sign_long = np.sign(ret_long)
    consistency = sign_short + sign_mid + sign_long

    # 计算综合强度
    strength = ret_short.abs() + ret_mid.abs() + ret_long.abs()

    # 综合因子：一致性 × 强度
    # 当三个周期方向一致时（consistency=±3），因子值最大
    # 当方向不一致时（consistency接近0），因子值小
    factor = consistency * strength

    return factor
