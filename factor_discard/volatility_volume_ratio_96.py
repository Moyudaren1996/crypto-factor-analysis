"""
Volatility指标 - Volume Conditioned Volatility Ratio (成交量条件波动率比率)

因子描述:
    VCVR 衡量高成交量时的波动率与低成交量时的波动率之比。
    HighVol_Std = 只有成交量高于均值时的收益率标准差
    LowVol_Std = 只有成交量低于均值时的收益率标准差
    Ratio = HighVol_Std / LowVol_Std
    
    逻辑:
    如果价格波动主要发生在成交量放大的时候（Ratio > 1），说明市场活跃度与价格变动同步，趋势可能更有效或动量更强。
    如果价格波动主要发生在成交量低迷的时候（Ratio < 1），可能暗示流动性枯竭或操纵，价格变动不可靠。
    该因子可能捕捉到"Smart Volatility"（聪明钱带来的波动）。

参数:
    period: 96 (8小时)

计算公式:
    1. Volume Mean = Rolling Mean(Volume, N)
    2. Returns = Close.pct_change()
    3. Ret_HighVol = Returns where Volume > Volume Mean, else NaN
    4. Ret_LowVol = Returns where Volume <= Volume Mean, else NaN
    5. Std_HighVol = Rolling Std(Ret_HighVol, N)
    6. Std_LowVol = Rolling Std(Ret_LowVol, N)
    7. Ratio = Std_HighVol / Std_LowVol

输出:
    因子值DataFrame

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
    计算 Volume Conditioned Volatility Ratio 因子

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
    period = 96
    min_periods = period // 4  # 允许一定缺失，至少要有1/4的数据点

    # 1. 计算滚动成交量均值
    vol_mean = volume.rolling(period).mean()

    # 2. 计算收益率
    returns = close.pct_change()

    # 3. 分离高量和低量收益率
    # 使用 mask/where
    # high_vol_mask: volume > vol_mean
    high_vol_mask = volume > vol_mean
    
    # 收益率序列，不满足条件的设为NaN
    ret_high_vol = returns.where(high_vol_mask)
    ret_low_vol = returns.where(~high_vol_mask)

    # 4. 计算滚动标准差
    # 注意：rolling().std() 会忽略NaN，只要窗口内非NaN数量 >= min_periods
    std_high_vol = ret_high_vol.rolling(period, min_periods=min_periods).std()
    std_low_vol = ret_low_vol.rolling(period, min_periods=min_periods).std()

    # 5. 计算比率
    # 处理分母为0的情况 (极少见，但需防范)
    epsilon = 1e-10
    ratio = std_high_vol / (std_low_vol + epsilon)

    return ratio
