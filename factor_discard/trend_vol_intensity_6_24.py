"""
Trend指标 - Volume Trend Intensity (成交量趋势强度因子)

因子描述:
    基于成交量变化的趋势强度因子。
    核心逻辑：趋势延续需要成交量支持。当价格运动方向与
    成交量变化方向一致时（价涨量增或价跌量缩），趋势更可能延续。

    与现有因子的关键差异：
    - 现有CMF/MFI：基于价格位置加权成交量
    - 现有PVO：成交量动量
    - 本因子：价格方向与成交量变化的协同关系

参数:
    short_period: 6 (30分钟)
    long_period: 24 (2小时)
    vol_period: 12 (1小时)

计算公式:
    1. 计算价格方向（短期均线趋势）
    2. 计算成交量变化率
    3. 计算价格方向与成交量变化的协同度
    4. 协同度高 = 趋势健康，可跟随

输出:
    因子值DataFrame，正值表示上涨趋势有量能支持

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-27
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量趋势强度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    volume = data['volume']
    high = data['high']
    low = data['low']

    # 参数定义
    short_period = 6
    long_period = 24
    vol_period = 12
    lookback = 48

    # 1. 计算价格趋势方向（使用高低价中点的EMA变化）
    mid_price = (high + low) / 2
    ema_short = mid_price.ewm(span=short_period, adjust=False).mean()
    ema_long = mid_price.ewm(span=long_period, adjust=False).mean()

    # 价格趋势：短期EMA相对长期EMA的位置
    price_trend = (ema_short - ema_long) / ema_long * 100

    # 2. 计算成交量变化率
    vol_ma = volume.rolling(vol_period).mean()
    vol_change = (volume - vol_ma) / vol_ma

    # 成交量变化的方向（放量or缩量）
    vol_direction = vol_change.rolling(short_period).mean()

    # 3. 计算价格-成交量协同度
    # 理想情况：上涨趋势+放量，或下跌趋势+缩量
    price_sign = np.sign(price_trend)
    vol_sign = np.sign(vol_direction)

    # 协同度：两者符号相同时为1，否则为0
    synergy = (price_sign == vol_sign).astype(float)

    # 4. 计算趋势强度的变化速度
    trend_speed = price_trend - price_trend.shift(short_period)
    trend_speed_norm = trend_speed / trend_speed.rolling(lookback).std().replace(0, np.nan)

    # 5. 综合因子计算
    # 基础信号：趋势方向 * 趋势速度 * 协同度权重
    base_signal = price_sign * trend_speed_norm.abs() * (0.5 + synergy * 0.5)

    # 6. 成交量异动加成
    vol_anomaly = vol_change.rolling(short_period).mean()
    vol_anomaly_norm = vol_anomaly / vol_anomaly.rolling(lookback).std().replace(0, np.nan)

    # 成交量异常放大时，放大信号
    vol_multiplier = 1 + vol_anomaly_norm.clip(-1, 1) * 0.3

    factor = base_signal * vol_multiplier

    # 7. 平滑处理
    factor = factor.ewm(span=6, adjust=False).mean()

    # 限制极端值
    factor = factor.clip(-5, 5)

    # 填充缺失值
    factor = factor.fillna(0)

    return factor
