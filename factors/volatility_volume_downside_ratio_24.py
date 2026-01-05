"""
Volatility指标 - Volume Weighted Downside Ratio

因子描述:
    成交量加权的下行波动率比率。
    计算成交量加权的下行波动率（Semideviation）占总成交量加权波动率的比例。
    该指标结合了价格波动和成交量信息，衡量市场恐慌程度。
    当比率较高时，表示大成交量主要集中在下跌过程中（恐慌抛售），往往预示反转。

参数:
    period: 24 (2小时)

计算公式:
    Ret = ln(Close / Close_prev)
    Downside_Ret = min(Ret, 0)
    Weighted_Downside_Var = Sum(Downside_Ret^2 * Volume, N)
    Weighted_Total_Var = Sum(Ret^2 * Volume, N)
    Factor = Sqrt(Weighted_Downside_Var / Weighted_Total_Var)

输出:
    因子值DataFrame (0到1之间)

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2026-01-02
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量加权下行波动率比率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    volume = data['volume']
    
    # 定义参数
    period = 24  # 2小时

    # 计算对数收益率
    ret = np.log(close / close.shift(1))
    
    # 获取下行收益率
    downside_ret = ret.clip(upper=0)
    
    # 计算加权平方项
    # 使用fill_value=0处理volume可能的NaN，但在K线数据中通常不应有NaN volume
    weighted_downside_sq = (downside_ret ** 2) * volume
    weighted_total_sq = (ret ** 2) * volume
    
    # 计算Rolling Sum
    downside_ss = weighted_downside_sq.rolling(period).sum()
    total_ss = weighted_total_sq.rolling(period).sum()
    
    # 计算比率
    epsilon = 1e-10
    factor = np.sqrt(downside_ss / (total_ss + epsilon))
    
    return factor
