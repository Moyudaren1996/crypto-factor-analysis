"""
Momentum指标 - Volatility Adjusted Momentum Reversal (波动率调整动量反转)

因子描述:
    基于波动率调整的动量反转因子。计算价格动量(收益率)与其波动率的比值(信息比率),
    然后计算该比值的变化率(加速度),捕捉动量强度变化的拐点。
    核心思想:当风险调整后的动量快速上升,表明市场过度追逐,后续倾向反转。

参数:
    momentum_period: 36 (3小时)
    vol_period: 12 (1小时)

计算公式:
    returns = close.pct_change()
    momentum = returns.ewm(span=momentum_period, adjust=False).mean()  # 动量
    volatility = returns.ewm(span=vol_period, adjust=False).std()  # 波动率
    risk_adj_momentum = momentum / (volatility + 1e-8)  # 风险调整动量(类似信息比率)
    factor = -risk_adj_momentum.diff(6)  # 6期变化率取负,加速上升→反转信号

输出:
    因子值DataFrame,数值越小表示风险调整动量加速越快,反转信号越强

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-13
版本: v1.3 (优化3)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率调整动量反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']

    momentum_period = 36
    vol_period = 12
    diff_period = 6

    # 计算收益率
    returns = close.pct_change()

    # 使用EWM计算动量(平滑收益率)
    momentum = returns.ewm(span=momentum_period, adjust=False).mean()

    # 使用EWM计算波动率
    volatility = returns.ewm(span=vol_period, adjust=False).std()

    # 计算风险调整后的动量(类似信息比率)
    # 分母加小常数避免除零
    risk_adj_momentum = momentum / (volatility + 1e-8)

    # 计算风险调整动量的变化率(加速度),取负值作为反转信号
    # 快速上升的风险调整动量→市场过度追逐→反转信号
    factor = -risk_adj_momentum.diff(diff_period)

    return factor
