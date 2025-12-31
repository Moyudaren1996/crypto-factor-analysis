"""
Momentum指标 - Return Skewness Reversal (收益率偏度反转)

因子描述:
    基于收益率分布偏度的反转因子
    当短期收益率分布出现显著正偏(右偏,极端上涨)时,往往预示反转下跌
    当短期收益率分布出现显著负偏(左偏,极端下跌)时,往往预示反转上涨
    使用相对ATR标准化,控制不同币种波动率差异

参数:
    period: 24 (2小时,收益率偏度计算周期)
    norm_period: 72 (6小时,ATR标准化周期)

计算公式:
    1. returns = close.pct_change()  # 5分钟收益率
    2. skew = returns.rolling(24).skew()  # 24期收益率偏度
    3. atr = (high - low).rolling(72).mean() / close.rolling(72).mean()  # 相对ATR
    4. factor = -skew / (atr + 1e-8)  # 负号表示反转,用ATR标准化

输出:
    因子值DataFrame,正值表示负偏+低波动(预期反转上涨),负值表示正偏+低波动(预期反转下跌)

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-13
版本: v1.3
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算收益率偏度反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 参数设置
    skew_period = 24      # 2小时
    norm_period = 72      # 6小时

    # 1. 计算5分钟收益率
    returns = close.pct_change()

    # 2. 计算滚动窗口收益率偏度
    # 正偏度表示右偏(极端上涨),负偏度表示左偏(极端下跌)
    return_skew = returns.rolling(skew_period).skew()

    # 3. 计算相对ATR(日内波幅相对价格)作为波动率度量
    relative_atr = (high - low).rolling(norm_period).mean() / (close.rolling(norm_period).mean() + 1e-8)

    # 4. 计算最终因子:偏度除以ATR标准化,负号表示反转逻辑
    # 正偏度(极端上涨)→因子为负→预期反转下跌
    # 负偏度(极端下跌)→因子为正→预期反转上涨
    # ATR越大(波动大)信号强度越弱
    factor = -return_skew / (relative_atr + 1e-8)

    return factor
