"""
Oscillator指标 - 高低价位置反转震荡器 (High-Low Position Reversal)

因子描述:
    基于Alpha101中日内价格结构的思想,计算收盘价在日内高低价区间的相对位置变化
    核心逻辑:当价格持续处于高位(接近high)后突然回落,或持续处于低位(接近low)后突然反弹
    捕捉价格在高低区间的极端位置反转信号,适合高频crypto市场的反转交易

参数:
    short_period: 6 (30分钟,位置计算周期)
    long_period: 24 (2小时,趋势判断周期)

计算公式:
    1. position = (close - low) / (high - low + 1e-8)  # 当前位置[0,1]
    2. avg_position = ts_mean(position, short_period)  # 短期平均位置
    3. position_change = position - avg_position  # 位置变化
    4. price_trend = (close - ts_mean(close, long_period)) / ts_mean(close, long_period)
    5. factor = -position_change * sign(price_trend)  # 反转信号:位置变化反向×趋势符号

输出:
    因子值DataFrame
    正值:价格处于低位且开始反弹(做多信号)
    负值:价格处于高位且开始回落(做空信号)

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-07
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算高低价位置反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    short_period = 6   # 位置计算周期(30分钟)
    long_period = 24   # 趋势判断周期(2小时)

    # 计算收盘价在high-low区间的相对位置
    hl_range = high - low
    position = (close - low) / (hl_range + 1e-8)  # 避免除零

    # 计算短期平均位置
    avg_position = position.rolling(short_period).mean()

    # 位置变化:当前位置 - 短期平均位置
    position_change = position - avg_position

    # 计算价格相对于长期均值的偏离
    price_mean = close.rolling(long_period).mean()
    price_deviation = (close - price_mean) / (price_mean + 1e-8)

    # 反转因子:位置突然下降(负position_change)且价格在高位(正deviation)→负值(看跌)
    #          位置突然上升(正position_change)且价格在低位(负deviation)→正值(看涨)
    factor = -position_change * np.sign(price_deviation)

    # 用价格波动率标准化增强信号
    volatility = close.pct_change().rolling(long_period).std()
    factor = factor / (volatility + 1e-8)

    return factor
