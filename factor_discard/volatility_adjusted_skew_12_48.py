"""
Volatility指标 - AdjustedSkew (波动率调整偏度)

因子描述:
    波动率调整偏度因子,计算经波动率标准化后的收益率序列的偏度。

    核心逻辑:
    1. 计算每期收益率除以短期波动率得到标准化收益率(类似Sharpe序列)
    2. 对标准化收益率计算滚动偏度
    3. 正偏度表示极端正收益多于极端负收益,暗示过度乐观
    4. 负偏度表示极端负收益多于极端正收益,暗示过度悲观
    5. 极端偏度预示均值回归

    与现有因子的差异:
    - 不同于普通收益率偏度,这里使用波动率调整后的标准化收益
    - 捕捉的是"风险调整后"的收益分布不对称性

参数:
    vol_period: 12 (1小时波动率窗口)
    skew_period: 48 (4小时偏度窗口)

计算公式:
    returns = close.pct_change()
    vol = rolling_std(returns, vol_period)
    adjusted_return = returns / vol
    factor = -rolling_skew(adjusted_return, skew_period)

输出:
    因子值DataFrame,负向因子(做多低值组)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率调整偏度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 参数定义
    vol_period = 12      # 1小时
    skew_period = 48     # 4小时

    # 计算收益率
    returns = close.pct_change()

    # 计算滚动波动率
    vol = returns.rolling(vol_period).std()

    # 波动率调整收益率 (标准化收益)
    adjusted_return = returns / vol

    # 计算标准化收益的滚动偏度
    skew = adjusted_return.rolling(skew_period).skew()

    # 取负值: 正偏度(过度乐观)做空,负偏度(过度悲观)做多
    factor = -skew

    return factor
