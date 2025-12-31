"""
Trend指标 - Price-Volatility Synergy (价格波动率协同)

因子描述:
    衡量价格突破与波动率扩张的协同效应,识别真实趋势延续信号
    当价格创新高且波动率同步放大时,趋势延续概率高
    当价格突破但波动率萎缩时,可能是假突破

参数:
    long_period: 48 (4小时) - 用于判断价格位置
    short_period: 12 (1小时) - 用于波动率变化

计算公式:
    1. 价格相对位置: price_rank = (close - rolling_min) / (rolling_max - rolling_min)
    2. 当前波动率: vol_now = rolling_std(returns, short)
    3. 历史波动率: vol_past = rolling_std(returns, long)
    4. 波动率扩张率: vol_expansion = vol_now / vol_past - 1
    5. 协同因子: synergy = price_rank * vol_expansion

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-07
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算价格波动率协同因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    long_period = 48
    short_period = 12

    # 计算价格在长周期内的相对位置(0-1之间)
    rolling_max = close.rolling(window=long_period).max()
    rolling_min = close.rolling(window=long_period).min()
    price_rank = (close - rolling_min) / (rolling_max - rolling_min + 1e-8)

    # 计算收益率
    returns = close.pct_change()

    # 计算短期和长期波动率
    vol_short = returns.rolling(window=short_period).std()
    vol_long = returns.rolling(window=long_period).std()

    # 计算波动率扩张率(短期相对长期的变化)
    vol_expansion = (vol_short / (vol_long + 1e-8)) - 1

    # 价格位置与波动率扩张的乘积
    # 正值:高位+波动率扩张(趋势延续)或低位+波动率收缩(反转机会)
    # 负值:高位+波动率收缩(假突破)或低位+波动率扩张(下跌加速)
    synergy = price_rank * vol_expansion

    # 标准化处理
    factor = synergy.rolling(window=long_period).apply(
        lambda x: (x.iloc[-1] - x.mean()) / (x.std() + 1e-8),
        raw=False
    )

    return factor
