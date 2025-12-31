"""
Momentum指标 - OSRS (Over-Sold Reversion Strength)

因子描述:
    超卖反转强度因子,捕捉短期急跌后的反弹机会
    结合价格在近期区间的相对位置、短期跌幅强度和波动率标准化
    因子值越大表示超卖程度越高,反转概率越大(预期未来上涨)

参数:
    period: 24 (2小时)

计算公式:
    1. price_position = (close - min(24)) / (max(24) - min(24))  # 价格在24期区间的相对位置,0表示最低点,1表示最高点
    2. return_strength = (close - close[t-6]) / close[t-6]  # 6期(30分钟)收益率
    3. volatility = std(return, 24)  # 24期收益率标准差
    4. osrs = -(1 - price_position) * abs(return_strength) / (volatility + 1e-6)  # 组合信号

    逻辑:
    - (1 - price_position)越大表示价格越接近低点(超卖)
    - return_strength负值且绝对值大表示急跌
    - 除以波动率标准化,避免高波币种主导
    - 取负号使得超卖时因子值为正,符合反转预期

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-10
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算OSRS因子

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
    period = 24  # 2小时窗口
    return_period = 6  # 30分钟收益率

    # 1. 计算价格在区间内的相对位置
    rolling_min = low.rolling(period).min()
    rolling_max = high.rolling(period).max()
    price_range = rolling_max - rolling_min
    price_position = (close - rolling_min) / (price_range + 1e-8)  # 避免除零

    # 2. 计算短期收益率强度
    return_strength = close.pct_change(return_period)

    # 3. 计算波动率
    returns = close.pct_change()
    volatility = returns.rolling(period).std()

    # 4. 组合超卖反转强度
    # (1 - price_position)表示距离高点的程度,越接近0(低点)该值越大
    # 当价格在低位且急跌时,因子值为正且较大,预示反转
    oversold_degree = 1 - price_position
    osrs = -oversold_degree * return_strength / (volatility + 1e-6)

    return osrs
