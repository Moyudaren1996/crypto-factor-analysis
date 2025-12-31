"""
Volatility指标 - Cross Momentum (波动率截面动量)

因子描述:
    波动率截面动量因子，利用横截面上波动率排名的变化来预测收益率。
    核心思想是：当一个币种的波动率排名从低快速上升到高时，往往意味着
    该币种正在经历异常波动，这种状态通常不可持续，存在反转机会。
    计算当前波动率横截面排名与历史平均排名的偏离度。

参数:
    vol_period: 12 (1小时，用于计算已实现波动率)
    rank_period: 48 (4小时，用于计算排名均值)

计算公式:
    1. returns = close.pct_change()
    2. rv = rolling_std(returns, vol_period)  # 已实现波动率
    3. cs_rank = rv.rank(axis=1, pct=True)  # 横截面排名
    4. rank_mean = rolling_mean(cs_rank, rank_period)  # 排名历史均值
    5. rank_deviation = cs_rank - rank_mean  # 排名偏离度
    6. factor = -rank_deviation  # 取负（高排名偏离意味着波动率异常升高，预期下跌反转）

输出:
    因子值DataFrame，正值表示波动率排名低于历史均值（低波动异象），
    负值表示波动率排名高于历史均值（高波动反转）

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2024-12-29
版本: v1.3 (优化版本3)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率截面动量因子

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
    vol_period = 12   # 1小时
    rank_period = 48  # 4小时

    # 使用Parkinson波动率（基于高低价，更稳健）
    log_hl = np.log(high / low)
    parkinson_vol = log_hl.rolling(window=vol_period).mean()

    # 横截面排名（每个时间点对所有币种排名）
    cs_rank = parkinson_vol.rank(axis=1, pct=True)

    # 排名的历史均值（该币种的典型波动率排名）
    rank_mean = cs_rank.rolling(window=rank_period).mean()

    # 排名的历史标准差
    rank_std = cs_rank.rolling(window=rank_period).std()

    # 排名偏离度（Z-score标准化）
    epsilon = 1e-10
    rank_zscore = (cs_rank - rank_mean) / (rank_std + epsilon)

    # 取负值：波动率排名上升（变得更波动）预示反转下跌
    factor = -rank_zscore

    return factor
