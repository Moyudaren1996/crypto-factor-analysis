"""
Momentum指标 - Intraday Range Momentum (日内波动动量因子)

因子描述:
    日内波动动量因子，衡量日内高低价振幅相对于收盘价位置的动态变化。
    不同于传统动量因子仅关注收盘价，本因子利用高低价信息：

    核心思想：
    - 计算收盘价在当期高低区间的相对位置(类似Stoch的%K)
    - 然后衡量这个位置的短期动量变化
    - 结合高低价振幅的趋势变化

    当高低区间位置向上移动且振幅扩大时，表明上涨趋势在加强

参数:
    short_period: 12 (1小时，12个5分钟K线)
    long_period: 48 (4小时，48个5分钟K线)

计算公式:
    range_position = (close - low) / (high - low)  # 收盘价在高低区间的位置
    range_pct = (high - low) / close  # 高低价振幅百分比

    # 位置动量
    position_momentum = range_position.rolling(N).mean() - range_position.rolling(N*4).mean()

    # 振幅趋势
    range_trend = range_pct / range_pct.rolling(N*4).mean() - 1

    # 综合因子
    factor = position_momentum * (1 + range_trend)

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-27
版本: v1.1
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Intraday Range Momentum因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数 - 调整为更短的周期以增强信号
    short_period = 12  # 1小时
    long_period = 48   # 4小时

    # 计算高低价区间
    hl_range = high - low
    hl_range_safe = hl_range.replace(0, np.nan)

    # 收盘价在高低区间的相对位置 [0, 1]
    range_position = (close - low) / hl_range_safe

    # 高低价振幅百分比
    range_pct = hl_range / close

    # 位置动量: 短期均值 - 长期均值
    short_position_ma = range_position.rolling(short_period, min_periods=short_period//2).mean()
    long_position_ma = range_position.rolling(long_period, min_periods=long_period//2).mean()
    position_momentum = short_position_ma - long_position_ma

    # 振幅趋势: 当前振幅相对于长期均值的比例
    range_pct_ma = range_pct.rolling(long_period, min_periods=long_period//2).mean()
    range_pct_ma_safe = range_pct_ma.replace(0, np.nan)
    range_trend = range_pct / range_pct_ma_safe - 1

    # 限制振幅趋势的极端值
    range_trend = range_trend.clip(-2, 2)

    # 综合因子: 位置动量 * (1 + 振幅趋势的符号调整)
    # 使用更强的信号增强
    factor = position_momentum * (1 + 0.5 * range_trend)

    return factor
