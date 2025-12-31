"""
Volatility指标 - High-Low Ratio Momentum (高低价比率动量因子)

因子描述:
    高低价比率动量因子,基于日内波动幅度(high/low)的变化趋势来衡量波动率变化。
    不同于ATR,这里使用high/low比率来衡量相对波动,然后计算其动量。
    当high/low比率持续扩大时,市场波动在增加,通常伴随趋势;
    当比率减小时,市场波动在收缩,可能预示盘整或反转。
    结合成交量权重,高成交量时的波动率信号更有意义。

参数:
    smooth_period: 6 (30分钟, 平滑周期)
    momentum_period: 24 (2小时, 动量周期)
    vol_period: 48 (4小时, 成交量参考周期)

计算公式:
    1. hl_ratio = high / low - 1  高低价比率(波动幅度)
    2. hl_smooth = EMA(hl_ratio, smooth_period)  平滑后的比率
    3. hl_momentum = hl_smooth / hl_smooth.shift(momentum_period) - 1  比率动量
    4. vol_weight = volume / volume.rolling(vol_period).mean()  相对成交量
    5. factor = hl_momentum * vol_weight  成交量加权的波动率动量

输出:
    因子值DataFrame,正值表示波动率扩张,负值表示波动率收缩

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-29
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算高低价比率动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    high = data['high']
    low = data['low']
    volume = data['volume']

    # 定义参数
    smooth_period = 6     # 30分钟
    momentum_period = 24  # 2小时
    vol_period = 48       # 4小时

    # 计算高低价比率 (日内波动幅度)
    hl_ratio = high / low - 1

    # 平滑处理
    hl_smooth = hl_ratio.ewm(span=smooth_period, adjust=False).mean()

    # 计算比率的动量 (波动率变化趋势)
    hl_momentum = hl_smooth / hl_smooth.shift(momentum_period) - 1

    # 计算相对成交量 (成交量权重)
    vol_weight = volume / volume.rolling(vol_period).mean()

    # 限制成交量权重的极端值
    vol_weight = vol_weight.clip(0.5, 2.0)

    # 成交量加权的波动率动量
    factor = hl_momentum * vol_weight

    return factor
