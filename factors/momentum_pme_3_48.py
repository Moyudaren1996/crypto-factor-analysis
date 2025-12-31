"""
Momentum指标 - PME (Price Momentum Extrema)

因子描述:
    价格动量极值反转因子。基于当前价格动量在历史范围内的相对位置识别极值。
    计算N期内价格变化(收益率)的最大最小值范围，然后计算当前收益率在这个范围内的百分位排名。
    当排名接近100%时表示动量极端上升，预示反转下跌；
    当排名接近0%时表示动量极端下跌，预示反转上涨。

参数:
    momentum_period: 3 (15分钟，计算当前收益率)
    lookback_period: 48 (4小时，历史范围窗口)

计算公式:
    momentum = (close - close[t-3]) / close[t-3]
    momentum_max = momentum的48期最大值
    momentum_min = momentum的48期最小值
    momentum_rank = (momentum - momentum_min) / (momentum_max - momentum_min)
    PME = -2 * (momentum_rank - 0.5)  # 中心化至[-1, 1]，极端值->反转信号

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算PME (Price Momentum Extrema)因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    momentum_period = 3
    lookback_period = 48

    # 计算短期收益率（动量）
    momentum = close.pct_change(momentum_period)

    # 计算历史范围（48期内的最大最小值）
    momentum_max = momentum.rolling(lookback_period).max()
    momentum_min = momentum.rolling(lookback_period).min()

    # 避免分母为0
    momentum_range = momentum_max - momentum_min
    momentum_range = momentum_range.replace(0, np.nan)

    # 计算百分位排名（动量在历史范围内的相对位置）
    momentum_rank = (momentum - momentum_min) / momentum_range

    # 反转逻辑：极端值（接近0或1）-> 反转信号
    # 当rank接近1时（极端上升）-> 负信号（看跌反转）
    # 当rank接近0时（极端下跌）-> 正信号（看涨反转）
    pme = -2 * (momentum_rank - 0.5)

    # 使用EWM平滑以增加稳定性
    pme = pme.ewm(span=6, adjust=False).mean()

    return pme
