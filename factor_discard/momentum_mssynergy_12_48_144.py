"""
Momentum指标 - Multi-Scale Momentum Synergy (多尺度动量协同)

因子描述:
    衡量多个时间尺度动量的协同程度。当短期、中期动量方向一致且强度都较高时，
    表示各时间尺度的市场参与者达成共识，趋势延续的概率更大。
    因子值越高表示多尺度动量协同越强。

参数:
    short_period: 12 (1小时短期动量)
    medium_period: 48 (4小时中期动量)
    long_period: 144 (12小时长期动量)

计算公式:
    1. 计算三个时间尺度的ROC
    2. 计算每个ROC的符号和强度
    3. 协同分数 = sign(short) * sign(medium) * sign(long) * min(abs(short), abs(medium), abs(long))
    4. 输出经过平滑的协同分数

输出:
    因子值DataFrame，正值表示多头协同，负值表示空头协同

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算多尺度动量协同因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 12   # 1小时
    medium_period = 48  # 4小时
    long_period = 144   # 12小时
    smooth_period = 6   # 平滑周期

    # 计算三个时间尺度的ROC
    roc_short = (close - close.shift(short_period)) / close.shift(short_period)
    roc_medium = (close - close.shift(medium_period)) / close.shift(medium_period)
    roc_long = (close - close.shift(long_period)) / close.shift(long_period)

    # 计算符号
    sign_short = np.sign(roc_short)
    sign_medium = np.sign(roc_medium)
    sign_long = np.sign(roc_long)

    # 计算方向一致性（当三个方向一致时为1或-1，否则接近0）
    direction_synergy = sign_short * sign_medium * sign_long

    # 计算最小强度（取三者绝对值最小的那个，作为瓶颈强度）
    abs_short = roc_short.abs()
    abs_medium = roc_medium.abs()
    abs_long = roc_long.abs()

    # 使用DataFrame的min方法
    min_strength = pd.concat([abs_short, abs_medium, abs_long], axis=1).min(axis=1)
    # 重塑为原始形状
    min_strength = pd.DataFrame(
        np.tile(min_strength.values.reshape(-1, 1), (1, close.shape[1])),
        index=close.index,
        columns=close.columns
    )

    # 协同分数 = 方向一致性 * 最小强度
    synergy_score = direction_synergy * min_strength

    # 平滑处理
    factor = synergy_score.ewm(span=smooth_period, adjust=False).mean()

    return factor
