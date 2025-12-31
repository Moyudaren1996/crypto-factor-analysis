"""
Momentum指标 - Volume Momentum Ratio (成交量动量比率)

因子描述:
    成交量动量比率因子，衡量价格动量与成交量动量的相对强度比值。
    核心思想：价格上涨时如果成交量支持不足（成交量动量落后于价格动量），
    可能表明上涨缺乏支撑；反之亦然。

    核心逻辑：
    1. 计算价格动量的标准化强度
    2. 计算成交量动量的标准化强度
    3. 计算两者的比值，衡量价格动量是否得到成交量支持
    4. 比值极端时表示价量分歧

参数:
    price_period: 18 (1.5小时，价格动量周期)
    vol_period: 36 (3小时，成交量平均周期)

计算公式:
    price_mom = (close - close.shift(price_period)) / close.shift(price_period)
    price_mom_zscore = (price_mom - price_mom.rolling(vol_period).mean()) / price_mom.rolling(vol_period).std()

    vol_change = volume / volume.rolling(vol_period).mean() - 1
    vol_zscore = (vol_change - vol_change.rolling(vol_period).mean()) / vol_change.rolling(vol_period).std()

    factor = price_mom_zscore - vol_zscore  # 价格强于成交量时为正

输出:
    因子值DataFrame，正值表示价格动量强于成交量动量（可能反转向下）

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
    计算成交量动量比率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    price_period = 18   # 1.5小时
    vol_period = 36     # 3小时
    norm_window = 72    # 6小时标准化窗口

    # 计算价格动量（收益率）
    price_mom = (close - close.shift(price_period)) / close.shift(price_period)

    # 计算价格动量的Z-score标准化
    price_mom_mean = price_mom.rolling(norm_window).mean()
    price_mom_std = price_mom.rolling(norm_window).std()
    price_mom_zscore = (price_mom - price_mom_mean) / (price_mom_std + 1e-8)

    # 计算成交量相对强度：当前成交量 / 平均成交量
    vol_ma = volume.rolling(vol_period).mean()
    vol_ratio = volume / (vol_ma + 1e-8)

    # 计算成交量的变化动量
    vol_mom = (vol_ratio - vol_ratio.shift(price_period))

    # 计算成交量动量的Z-score
    vol_mom_mean = vol_mom.rolling(norm_window).mean()
    vol_mom_std = vol_mom.rolling(norm_window).std()
    vol_zscore = (vol_mom - vol_mom_mean) / (vol_mom_std + 1e-8)

    # 最终因子：价格动量强度 - 成交量动量强度
    # 正值表示价格动量未得到成交量支持（量价背离，可能反转下跌）
    # 负值表示价格动量小于成交量动量（量价配合，可能继续）
    factor = price_mom_zscore - vol_zscore

    # 使用tanh压缩极端值
    factor = np.tanh(factor / 2)

    return factor
