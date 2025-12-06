"""
Momentum指标 - Price-Volume Acceleration (PVAccel)

因子描述:
    价格动量强度与成交量支撑度的背离指标,使用EMA平滑提升稳定性
    通过对比价格ROC与成交量变化率,捕捉价量背离信号
    正值表示价格涨幅超过成交量涨幅(可能衰竭),负值表示价格跌幅超过成交量跌幅(可能反弹)

参数:
    period: 12 (1小时)

计算公式:
    price_roc = (close - close[t-period]) / close[t-period] * 100
    volume_ratio = volume / EMA(volume, period)  # 成交量相对均值

    # EMA平滑提升稳定性
    price_roc_ema = EMA(price_roc, period)
    volume_ratio_ema = EMA(volume_ratio, period)

    # 滚动标准化
    price_norm = (price_roc_ema - Mean(price_roc_ema, period)) / Std(price_roc_ema, period)
    volume_norm = (volume_ratio_ema - Mean(volume_ratio_ema, period)) / Std(volume_ratio_ema, period)

    PVAccel = price_norm - volume_norm

输出:
    因子值DataFrame,价格动量与成交量相对强度的背离度

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-06
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Price-Volume Acceleration因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    volume = data['volume']
    period = 12

    # 计算价格变化率
    price_roc = (close - close.shift(period)) / close.shift(period) * 100

    # 计算成交量相对均值
    volume_ema = volume.ewm(span=period, adjust=False).mean()
    volume_ratio = volume / volume_ema

    # EMA平滑
    price_roc_ema = price_roc.ewm(span=period, adjust=False).mean()
    volume_ratio_ema = volume_ratio.ewm(span=period, adjust=False).mean()

    # 滚动标准化
    price_mean = price_roc_ema.rolling(period).mean()
    price_std = price_roc_ema.rolling(period).std()
    price_norm = (price_roc_ema - price_mean) / price_std

    volume_mean = volume_ratio_ema.rolling(period).mean()
    volume_std = volume_ratio_ema.rolling(period).std()
    volume_norm = (volume_ratio_ema - volume_mean) / volume_std

    # 计算背离因子
    factor = price_norm - volume_norm

    return factor
