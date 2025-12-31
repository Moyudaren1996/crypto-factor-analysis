"""
波动率指标 - 突破质量因子

因子描述:
    衡量价格突破的质量,结合价格相对位置和波动率水平
    当价格接近区间高点且波动率低时,说明突破质量高(上涨有序)
    当价格接近区间低点且波动率低时,说明下跌有序(可能反转)
    核心思想:低波动突破比高波动突破更可靠

参数:
    position_period: 24 (2小时,计算价格在区间内的位置)
    vol_period: 6 (30分钟,计算短期波动率)

计算公式:
    1. 计算价格在N期高低区间的相对位置 (0-1之间)
    2. 计算短期波动率(收益率标准差)
    3. 计算波动率的相对水平(当前vs历史均值的比值)
    4. 突破质量 = 价格位置 / 波动率相对水平
    5. 标准化处理

输出:
    因子值DataFrame,正值表示高质量上涨突破,负值表示高质量下跌

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-08
版本: v2.0 (最优版本)
废弃原因: 经过3次优化后均未达标,最优版本P1 IC=0.0197/ICIR=0.0962接近但未达标,P2 IC=0.0167/ICIR=0.0765未达标,
         双时间段均未同时满足IC绝对值>0.02且ICIR绝对值>0.1的要求,且与oscillator_rsi_6相关性高达58.64%接近70%阈值,
         本质上与RSI系列因子较为相似(都计算价格在区间内的相对位置),无法提供足够独立的信息增量
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算突破质量因子

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
    position_period = 24  # 2小时
    vol_period = 6  # 30分钟

    # 计算价格在区间内的位置 (类似威廉指标,但范围是0-1)
    rolling_high = high.rolling(position_period).max()
    rolling_low = low.rolling(position_period).min()
    price_range = rolling_high - rolling_low

    # 避免除零
    price_range = price_range.replace(0, np.nan)

    # 价格位置: 0表示在区间底部, 1表示在区间顶部
    price_position = (close - rolling_low) / price_range

    # 计算短期波动率
    returns = close.pct_change()
    short_vol = returns.rolling(vol_period).std()

    # 计算波动率的历史平均水平(用较长周期)
    vol_mean = short_vol.rolling(position_period * 3).mean()

    # 避免除零
    vol_mean = vol_mean.replace(0, np.nan)

    # 波动率相对水平: >1表示当前波动率高于平均, <1表示低于平均
    vol_relative = short_vol / vol_mean

    # 避免除零
    vol_relative = vol_relative.replace(0, np.nan)

    # 突破质量 = 价格位置 / 波动率相对水平
    # 价格位置高(接近区间顶部) + 波动率低(相对水平<1) = 高质量上涨突破(值大)
    # 价格位置低(接近区间底部) + 波动率低 = 高质量下跌(值小)
    breakout_quality = price_position / vol_relative

    # 对因子值进行z-score标准化(使用滚动窗口)
    factor_mean = breakout_quality.rolling(position_period * 5).mean()
    factor_std = breakout_quality.rolling(position_period * 5).std()

    # 避免除零
    factor_std = factor_std.replace(0, np.nan)

    factor = (breakout_quality - factor_mean) / factor_std

    return factor
