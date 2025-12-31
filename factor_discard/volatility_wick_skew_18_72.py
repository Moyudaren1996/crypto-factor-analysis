"""
Volatility指标 - Intraday Volatility Skew (日内波动率偏度因子)

因子描述:
    日内波动率偏度因子,通过分析K线形态计算上行与下行波动的非对称性。

    核心逻辑:
    1. 计算上影线波动(high - max(open, close)): 代表上行遇阻力量
    2. 计算下影线波动(min(open, close) - low): 代表下行支撑力量
    3. 计算两者的比值偏度,识别市场买卖力量的不平衡
    4. 当上行力量 >> 下行力量时,价格可能已在高位受阻,有下跌风险
    5. 当下行力量 >> 上行力量时,价格可能已在低位获支撑,有上涨机会

    理论基础:
    - K线形态包含重要的微观结构信息
    - 上影线代表做空力量,下影线代表做多力量
    - 持续的力量不平衡往往预示反转

参数:
    short_period: 18 (1.5小时,短期偏度)
    long_period: 72 (6小时,偏度的历史标准化)

计算公式:
    1. upper_wick = high - max(open, close)  # 上影线
    2. lower_wick = min(open, close) - low   # 下影线
    3. wick_ratio = upper_wick / (upper_wick + lower_wick + epsilon)  # 上影线占比
    4. wick_skew = wick_ratio.rolling(short_period).mean() - 0.5  # 偏度 (0.5为中性)
    5. skew_zscore = Z-score标准化
    6. factor = -skew_zscore  # 上影线多(正偏度) → 做空; 下影线多 → 做多

输出:
    因子值DataFrame

数据依赖:
    - open: 开盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算日内波动率偏度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    open_price = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    short_period = 18   # 1.5小时
    long_period = 72    # 6小时

    # 1. 计算K线实体的上下边界
    body_high = pd.DataFrame(
        np.maximum(open_price.values, close.values),
        index=close.index,
        columns=close.columns
    )
    body_low = pd.DataFrame(
        np.minimum(open_price.values, close.values),
        index=close.index,
        columns=close.columns
    )

    # 2. 计算上影线和下影线
    upper_wick = high - body_high  # 上影线长度
    lower_wick = body_low - low    # 下影线长度

    # 3. 计算总影线和上影线占比
    total_wick = upper_wick + lower_wick
    epsilon = 1e-10  # 避免除零
    wick_ratio = upper_wick / (total_wick + epsilon)

    # 4. 计算短期偏度 (相对于0.5中性值)
    wick_skew = wick_ratio.rolling(short_period).mean() - 0.5

    # 5. Z-score标准化
    skew_mean = wick_skew.rolling(long_period).mean()
    skew_std = wick_skew.rolling(long_period).std()
    skew_zscore = (wick_skew - skew_mean) / (skew_std + epsilon)

    # 6. 因子: 负向
    # 上影线占比高(skew_zscore > 0) → 上方阻力大 → 做空(负因子值)
    # 下影线占比高(skew_zscore < 0) → 下方支撑强 → 做多(正因子值)
    factor = -skew_zscore

    return factor
