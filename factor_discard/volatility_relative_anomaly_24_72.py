"""
Volatility指标 - 相对波动率异常因子 (Relative Volatility Anomaly)

因子描述:
    基于纯波动率结构的横截面因子，完全独立于价格趋势方向。
    核心思想：单个币种的波动率相对于市场整体波动率的异常程度。

    当某币种波动率显著低于市场平均时(低波动率异象)，往往预示后续
    存在补涨或波动率回归的机会；当波动率显著高于市场平均时，
    后续可能面临波动率收缩和收益回调。

    关键创新：
    1. 只使用波动率信息，不使用价格方向信息
    2. 横截面标准化，捕捉相对波动率位置
    3. 结合时序波动率变化率，增加时序维度

参数:
    vol_period: 24 (2小时计算已实现波动率)
    rank_period: 72 (6小时用于时序排名)

计算公式:
    1. 计算每个币种的已实现波动率: rv = rolling_std(returns, vol_period)
    2. 计算截面中位数: rv_median = rv.median(axis=1)
    3. 计算截面MAD: rv_mad = |rv - rv_median|.median(axis=1)
    4. 横截面标准化: rv_z = (rv - rv_median) / rv_mad
    5. 计算波动率变化率: vol_change = rv.pct_change(6)
    6. 时序排名: vol_change_rank = rolling_rank(vol_change, rank_period)
    7. 最终因子: factor = -rv_z * (1 - vol_change_rank)
       (低波动率 + 波动率在下降 → 正值，预示上涨)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-29
版本: v1.3 (第三次优化 - 完全不同的逻辑)
"""
import pandas as pd
import numpy as np


def calculate(data):
    """
    计算相对波动率异常因子

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
    vol_period = 24     # 2小时计算波动率
    rank_period = 72    # 6小时用于时序排名
    change_period = 6   # 30分钟变化周期

    # 方法1: 使用Parkinson波动率 (基于高低价，更稳定)
    hl_ratio = np.log(high / low)
    parkinson_factor = 1.0 / (4 * np.log(2))
    rv = np.sqrt(parkinson_factor * (hl_ratio ** 2).rolling(window=vol_period).mean())

    # 方法2: 补充使用收益率波动率
    returns = close.pct_change()
    rv_ret = returns.rolling(window=vol_period).std()

    # 综合波动率 (两者平均)
    rv_combined = (rv + rv_ret) / 2

    # ========== 横截面标准化 ==========
    # 计算每个时间点的截面中位数
    rv_median = rv_combined.median(axis=1)

    # 计算MAD (Median Absolute Deviation) 作为稳健的离散度估计
    rv_deviation = rv_combined.sub(rv_median, axis=0).abs()
    rv_mad = rv_deviation.median(axis=1)

    # 横截面Z-score (使用MAD标准化)
    rv_z = rv_combined.sub(rv_median, axis=0).div(rv_mad, axis=0)

    # ========== 波动率变化率 (时序维度) ==========
    vol_change = rv_combined.pct_change(change_period)

    # 对波动率变化率进行时序排名 (0-1之间)
    vol_change_rank = vol_change.rolling(window=rank_period).rank(pct=True)

    # ========== 核心因子逻辑 ==========
    # 低波动率异象: 低波动率的币种往往后续有更好的风险调整收益
    # 因子 = -横截面波动率Z-score × (1 - 波动率变化率排名)
    #
    # 解释:
    # - rv_z > 0: 波动率高于市场平均 → 负因子值
    # - rv_z < 0: 波动率低于市场平均 → 正因子值
    # - vol_change_rank接近1: 波动率在上升 → 降低因子强度
    # - vol_change_rank接近0: 波动率在下降 → 增加因子强度

    vol_change_adj = 1.5 - vol_change_rank  # 转换为0.5-1.5的乘数
    factor = -rv_z * vol_change_adj

    # 限制极端值
    factor = factor.clip(-4, 4)

    return factor
