"""
Volatility指标 - CrossSectionalOutlier (波动率横截面离群度)

因子描述:
    波动率横截面离群度因子，利用币种间波动率的相对位置识别反转机会。

    核心逻辑：
    1. 对每个时间点，计算所有币种的Parkinson波动率
    2. 计算每个币种波动率在横截面上的Z-score(相对于市场中位数)
    3. 计算Z-score的时序变化趋势
    4. 当某币种波动率从极端位置开始回归时，价格可能也会反转

参数:
    vol_period: 24 (2小时)
    trend_period: 48 (4小时)

计算公式:
    1. parkinson_vol = 每个币种的Parkinson波动率
    2. cs_median = 横截面中位数
    3. cs_std = 横截面标准差
    4. cs_zscore = (vol - cs_median) / cs_std
    5. zscore_trend = 线性回归斜率(cs_zscore, trend_period)
    6. 当z-score极端但趋势反向时，预期反转

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率横截面离群度因子

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
    vol_period = 24    # 2小时
    trend_period = 48  # 4小时

    # 1. 计算Parkinson波动率
    log_hl = np.log(high / low)
    parkinson_vol = np.sqrt(log_hl.pow(2).rolling(vol_period).mean() / (4 * np.log(2)))

    # 2. 计算横截面统计量
    cs_median = parkinson_vol.median(axis=1)
    cs_std = parkinson_vol.std(axis=1)

    # 3. 计算每个币种的横截面Z-score
    cs_zscore = parkinson_vol.sub(cs_median, axis=0).div(cs_std + 1e-10, axis=0)

    # 4. 计算Z-score的时序趋势(使用差分近似)
    zscore_change = cs_zscore.diff(trend_period)

    # 5. 计算Z-score在历史范围内的分位数(时序)
    zscore_percentile = cs_zscore.rolling(trend_period * 2).rank(pct=True)

    # 6. 反转信号：
    # - Z-score极端(高或低分位)
    # - Z-score变化方向与当前位置相反(回归)
    extremity = 2 * (zscore_percentile - 0.5).abs()  # 0-1, 极端程度
    reverting = -np.sign(cs_zscore) * np.sign(zscore_change)  # 回归时为正

    # 7. 计算价格动量作为方向参考
    returns = close.pct_change(vol_period)

    # 8. 组合因子
    # 波动率从极端位置回归 + 价格动量反向
    factor = extremity * reverting * (-np.sign(returns))

    return factor
