"""
Momentum指标 - VolumePriceMomentumDiv (成交量价格动量背离)

因子描述:
    成交量价格动量背离因子，衡量价格动量与成交量动量的背离程度。
    基于以下逻辑：
    1. 健康的趋势应该有价格和成交量的一致性
    2. 价格上涨但成交量萎缩，可能是假突破
    3. 价格下跌但成交量放大，可能是恐慌抛售（底部）

    本因子计算价格动量排名与成交量动量排名的差异，
    用横截面排名来消除量纲差异，增强跨币种可比性。

参数:
    momentum_period: 12 (1小时，动量计算周期)
    rank_period: 48 (4小时，滚动排名窗口)

计算公式:
    1. price_mom = pct_change(close, momentum_period)
    2. vol_mom = pct_change(volume, momentum_period)
    3. price_rank = rolling_rank(price_mom, rank_period) / rank_period
    4. vol_rank = rolling_rank(vol_mom, rank_period) / rank_period
    5. factor = price_rank - vol_rank  # 背离度

输出:
    因子值DataFrame，正值表示价格动量强于成交量动量

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算VolumePriceMomentumDiv因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    momentum_period = 12   # 动量计算周期 (1小时)
    rank_period = 48       # 滚动排名窗口 (4小时)

    # 计算价格动量
    price_mom = close.pct_change(momentum_period)

    # 计算成交量动量
    vol_mom = volume.pct_change(momentum_period)

    # 计算滚动时间序列内的百分位排名
    # 使用rank(pct=True)在时间序列上获取相对位置
    price_rank = price_mom.rolling(rank_period).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )

    vol_rank = vol_mom.rolling(rank_period).apply(
        lambda x: pd.Series(x).rank(pct=True).iloc[-1], raw=False
    )

    # 计算背离度：价格动量排名 - 成交量动量排名
    # 正值：价格强于成交量支持（可能反转）
    # 负值：成交量强于价格（趋势延续或底部）
    divergence = price_rank - vol_rank

    return divergence
