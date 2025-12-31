"""
Oscillator指标 - BPRESSURE (Buy-Sell Pressure Asymmetry)

因子描述:
    买卖压力非对称震荡因子,基于Alpha101的买卖力量对比思想
    核心逻辑:
    1. 买压=收盘价相对日内低点的位置,反映买方力量
    2. 卖压=收盘价相对日内高点的位置,反映卖方力量
    3. 净压力=买压-卖压,反映多空力量对比
    4. 计算净压力的短期vs长期均值差异
    5. 用成交量加权强调有成交支持的压力变化

参数:
    short_period: 6 (30分钟)
    long_period: 24 (2小时)

计算公式:
    1. buy_pressure = (close - low) / (high - low + 1e-8) - 买方压力
    2. sell_pressure = (high - close) / (high - low + 1e-8) - 卖方压力
    3. net_pressure = buy_pressure - sell_pressure - 净压力
    4. volume_weight = volume / MA(volume, 24) - 成交量权重
    5. weighted_pressure = net_pressure * volume_weight - 加权压力
    6. short_ma = MA(weighted_pressure, 6) - 短期均值
    7. long_ma = MA(weighted_pressure, 24) - 长期均值
    8. factor = short_ma - long_ma - 压力变化

输出:
    因子值DataFrame,正值表示买压增强,负值表示卖压增强

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-07
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算买卖压力非对称震荡因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']

    # 定义参数
    short_period = 6   # 30分钟
    long_period = 24   # 2小时

    # 计算买卖压力
    # 买压:收盘价越接近高点,买压越大(0到0.5)
    buy_pressure = (close - low) / (high - low + 1e-8)

    # 卖压:收盘价越接近低点,卖压越大(0到0.5)
    sell_pressure = (high - close) / (high - low + 1e-8)

    # 净压力:买压减去卖压
    # 正值表示买方占优,负值表示卖方占优
    net_pressure = buy_pressure - sell_pressure

    # 成交量相对强度作为权重
    volume_ma = volume.rolling(long_period).mean()
    volume_weight = volume / (volume_ma + 1e-8)

    # 成交量加权的净压力
    weighted_pressure = net_pressure * volume_weight

    # 计算短期和长期均值
    short_ma = weighted_pressure.rolling(short_period).mean()
    long_ma = weighted_pressure.rolling(long_period).mean()

    # 压力变化:短期均值-长期均值
    # 正值表示买压相对增强,负值表示卖压相对增强
    factor = short_ma - long_ma

    return factor
