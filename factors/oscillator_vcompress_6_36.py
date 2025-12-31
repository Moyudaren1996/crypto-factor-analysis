"""
Oscillator指标 - Volatility Compression Reversal (波动率收缩反转)

因子描述:
    波动率收缩反转因子优化版,基于技术分析中"波动率收缩后必有扩张"的原理。
    通过更严格的波动率收缩识别(10%分位数)和更短的周期(36)提高信号质量。

    核心逻辑:
    1. 识别波动率极度收缩时期(短期ATR/长期ATR < 10%分位数,更严格)
    2. 在收缩期,价格相对均线的位置反映市场情绪偏向
    3. 波动率收缩+价格偏上 → 假突破向上,预示下跌反转
       波动率收缩+价格偏下 → 假突破向下,预示上涨反转

    优化点:
    - 波动率收缩阈值从20%降至10%,只在极度收缩时产生信号
    - 周期从48缩短至36,提高响应速度

参数:
    short_period: 6 (30分钟,捕捉短期波动率)
    long_period: 36 (3小时,衡量长期波动率基准,优化后缩短)

计算公式:
    1. short_atr = ATR(6)  # 真实波动幅度短期均值
    2. long_atr = ATR(36)  # 真实波动幅度长期均值(优化:从48缩短至36)
    3. vol_ratio = short_atr / long_atr  # 波动率比值

    4. vol_compressed = (vol_ratio < rolling_quantile(vol_ratio, 36, 0.1))
       识别波动率收缩(优化:比值低于10%分位数,更严格)

    5. price_position = (close - SMA(36)) / SMA(36)
       价格相对均线的位置

    6. factor = -price_position * vol_compressed
       波动率收缩时,价格偏上给负值(预示下跌),价格偏下给正值(预示上涨)

输出:
    因子值DataFrame,正值表示看涨反转,负值表示看跌反转

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-14
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率收缩反转因子(优化版)

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    short_period = 6
    long_period = 36  # 优化: 从48缩短至36

    # 1. 计算True Range (TR)
    prev_close = close.shift(1)

    # 为每个币种单独计算TR
    tr_df = pd.DataFrame(index=close.index, columns=close.columns)
    for col in close.columns:
        h_l = high[col] - low[col]
        h_pc = (high[col] - prev_close[col]).abs()
        l_pc = (low[col] - prev_close[col]).abs()
        tr_df[col] = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)

    tr = tr_df

    # 2. 计算短期和长期ATR
    short_atr = tr.rolling(short_period).mean()
    long_atr = tr.rolling(long_period).mean()

    # 3. 计算波动率比值
    vol_ratio = short_atr / long_atr

    # 4. 识别波动率收缩(比值 < 10%分位数,优化:从20%降至10%)
    vol_threshold = vol_ratio.rolling(long_period).quantile(0.1)  # 优化: 从0.2降至0.1
    vol_compressed = (vol_ratio < vol_threshold).astype(float)

    # 5. 计算价格相对均线位置
    sma = close.rolling(long_period).mean()
    price_position = (close - sma) / sma

    # 6. 计算反转因子
    factor = -price_position * vol_compressed

    return factor
