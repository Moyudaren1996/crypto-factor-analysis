"""
Momentum指标 - VolWeightedSkew (成交量加权偏度动量)

因子描述:
    成交量加权偏度动量因子,通过计算成交量加权收益率的滚动偏度来识别
    动量的分布特征变化。当成交量加权收益率呈现负偏度(大幅下跌伴随高成交量)
    时,预示潜在反弹机会;正偏度(大幅上涨伴随高成交量)时,预示潜在回调。

    核心逻辑:
    1. 计算每个周期的收益率
    2. 用相对成交量(成交量/MA成交量)加权收益率
    3. 计算加权收益率的滚动偏度
    4. 偏度反映了收益率分布的不对称性
    5. 结合横截面排名来增强信号

参数:
    return_period: 6 (30分钟收益率周期)
    vol_ma_period: 12 (1小时成交量均值周期)
    skew_period: 48 (4小时偏度计算窗口)

计算公式:
    ret = close / close.shift(return_period) - 1
    vol_ratio = volume / volume.rolling(vol_ma_period).mean()
    weighted_ret = ret * vol_ratio
    factor = weighted_ret.rolling(skew_period).skew()

输出:
    因子值DataFrame,正偏度表示上涨动量可能耗竭(潜在反转下跌),
    负偏度表示下跌动量可能耗竭(潜在反转上涨)

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算VolWeightedSkew因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    return_period = 6    # 30分钟收益率周期
    vol_ma_period = 12   # 1小时成交量均值周期
    skew_period = 48     # 4小时偏度计算窗口

    # 计算收益率
    ret = close / close.shift(return_period) - 1

    # 计算相对成交量强度
    vol_ma = volume.rolling(vol_ma_period).mean()
    vol_ratio = volume / vol_ma.replace(0, np.nan)

    # 计算成交量加权收益率
    weighted_ret = ret * vol_ratio

    # 计算滚动偏度
    factor = weighted_ret.rolling(skew_period).skew()

    return factor
