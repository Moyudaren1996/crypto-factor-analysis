"""
Volatility指标 - VolCrossRank (波动率截面排名)

因子描述:
    波动率截面排名因子，计算每个币种的波动率在所有币种中的相对排名。
    基于低波动率异象(Low Volatility Anomaly)的思想：低波动率资产
    往往能获得更高的风险调整后收益。

    计算逻辑：
    1. 计算每个币种的已实现波动率(收益率滚动标准差)
    2. 在每个时间点，对所有币种的波动率进行横截面排名
    3. 将排名转换为百分位数(0-1范围)
    4. 低波动率币种排名靠前(低分位)，高波动率币种排名靠后(高分位)

    低波动率(低排名)的币种可能有更好的表现。

参数:
    vol_period: 36 (3小时，波动率计算周期)

计算公式:
    1. returns = close.pct_change()
    2. realized_vol = rolling_std(returns, vol_period)
    3. factor = cross_sectional_rank(realized_vol, pct=True)

输出:
    因子值DataFrame，为波动率的横截面百分位排名(0-1)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0

废弃原因: P1达标(IC=-0.0156/ICIR=-0.0505), P2 ICIR不达标(IC=-0.0125/ICIR=-0.0404<0.05),
         最高相关性25.55%(与trend_sma_600)。尝试过Parkinson波动率比率(IC太低P1=-0.0037/P2=-0.0003)、
         波动率加速度(IC太低P1=-0.0034/P2=-0.0001)、True Range波动率排名48周期(IC太低P1=0.0034/P2=-0.0007)
         均不达标。
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算VolCrossRank因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    vol_period = 36   # 波动率计算周期 (3小时)

    # 计算收益率
    returns = close.pct_change()

    # 计算已实现波动率 (滚动标准差)
    realized_vol = returns.rolling(vol_period).std()

    # 计算横截面百分位排名 (每个时间点对所有币种排名)
    factor = realized_vol.rank(axis=1, pct=True)

    return factor
