"""
价格指标 - High-Low Spread Ratio

因子描述:
    高低价差比率指标,通过计算日内波动幅度(High-Low)相对于价格的比率变化,
    来识别市场波动性与价格趋势的背离关系。
    当价格上涨但波动率下降时,可能预示趋势减弱;
    当价格下跌但波动率上升时,可能预示恐慌性抛售后的反转机会。

参数:
    period: 72 (6小时) - 计算波动率变化的回顾周期
    smooth: 12 (1小时) - 平滑窗口

计算公式:
    1. hl_spread = (high - low) / close  # 标准化的高低价差(相对价格)
    2. spread_change = hl_spread / hl_spread.shift(period) - 1  # 波动率变化
    3. price_change = close / close.shift(period) - 1  # 价格变化
    4. factor_raw = spread_change - price_change  # 波动率变化与价格变化的差异
    5. factor = factor_raw.rolling(smooth).mean()  # 平滑处理

    输出含义:
    - factor > 0: 波动率增速 > 价格增速,市场不确定性增加
    - factor < 0: 波动率增速 < 价格增速,趋势确立且波动收敛

输出:
    因子值DataFrame

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-07
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算High-Low Spread Ratio因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    period = 72      # 6小时
    smooth = 12      # 1小时

    # 计算标准化的高低价差(相对于收盘价)
    hl_spread = (high - low) / close

    # 计算波动率变化率
    spread_change = hl_spread / hl_spread.shift(period) - 1

    # 计算价格变化率
    price_change = close / close.shift(period) - 1

    # 计算波动率与价格变化的背离
    factor_raw = spread_change - price_change

    # 平滑处理
    factor = factor_raw.rolling(smooth).mean()

    return factor
