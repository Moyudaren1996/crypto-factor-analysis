"""
Volatility指标 - Mean Reversion Signal (波动率均值回归信号因子)

因子描述:
    基于波动率均值回归特性设计的纯波动率因子。核心逻辑：
    1. 波动率处于极端高位时，市场风险增加，未来收益率往往较低
    2. 波动率处于极端低位时，市场可能积蓄能量，未来可能出现大波动
    3. 结合波动率的变化方向（加速/减速）来判断时机

    与其他因子的差异：
    - 不使用价格位置信息（避免与RSI等高相关）
    - 专注于波动率的极端状态和变化方向
    - 使用Parkinson波动率（更精确）和收益率波动率的组合

参数:
    short_period: 12 (1小时，用于计算短期波动率和变化率)
    long_period: 72 (6小时，用于计算长期均值和分位)

计算公式:
    1. parkinson_vol = sqrt(sum((ln(high/low))^2) / (4*ln(2)*period))
    2. ret_vol = 收益率的滚动标准差
    3. combined_vol = (parkinson_vol + ret_vol) / 2  # 综合波动率
    4. vol_zscore = (combined_vol - mean) / std  # Z-score标准化
    5. vol_momentum = combined_vol.pct_change(short)  # 波动率动量
    6. vol_rank = vol_zscore在历史上的分位排名
    7. factor = vol_rank * sign(vol_momentum)
       - 高波动+波动率上升 -> 正值 -> 做空
       - 高波动+波动率下降 -> 负值 -> 做多（波动率回归）
       - 低波动+波动率上升 -> 正值 -> 做空（波动率扩张）
       - 低波动+波动率下降 -> 负值 -> 做多

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np


def calculate(data):
    """
    计算波动率均值回归信号因子

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
    short_period = 12  # 1小时
    long_period = 72   # 6小时

    # 计算收益率
    returns = close.pct_change()

    # 计算Parkinson波动率
    log_hl = np.log(high / low)
    log_hl_sq = log_hl ** 2
    parkinson_vol = np.sqrt(log_hl_sq.rolling(short_period).mean() / (4 * np.log(2)))

    # 计算收益率波动率
    ret_vol = returns.rolling(short_period).std()

    # 综合波动率（两种波动率的平均）
    combined_vol = (parkinson_vol + ret_vol) / 2

    # 计算波动率的Z-score（相对于长期均值的偏离）
    vol_mean = combined_vol.rolling(long_period).mean()
    vol_std = combined_vol.rolling(long_period).std()
    vol_zscore = (combined_vol - vol_mean) / vol_std

    # 波动率动量（变化方向）
    vol_momentum = combined_vol.pct_change(short_period)

    # 将Z-score转换为分位排名 (0-1)
    vol_rank = vol_zscore.rolling(long_period).rank(pct=True)
    # 中心化到 -0.5 到 0.5
    vol_rank_centered = vol_rank - 0.5

    # 因子构造：
    # - 高波动(rank>0) + 波动率上升(momentum>0) -> 正值 -> 做空信号
    # - 高波动(rank>0) + 波动率下降(momentum<0) -> 负值 -> 做多信号（回归）
    # - 低波动(rank<0) + 波动率上升(momentum>0) -> 负值 -> 做多信号（预期突破后回归）
    # - 低波动(rank<0) + 波动率下降(momentum<0) -> 正值 -> 做空信号
    factor = vol_rank_centered * np.sign(vol_momentum)

    # 取负使因子为负向（做多低值组）
    factor = -factor

    return factor
