"""
Momentum指标 - MomentumExhaustion (动量耗竭反转因子)

因子描述:
    动量耗竭反转因子,基于动量的持续性和强度识别反转机会。
    当价格在短期内持续朝一个方向运动(高一致性)且动量较强时,
    容易出现动量耗竭和均值回归。

    取负号使因子变成反转信号:当持续上涨时做空,持续下跌时做多。

参数:
    period: 36 (3小时) - 计算窗口

计算公式:
    1. ret = close.pct_change() - 单周期收益率
    2. cum_ret = close / close.shift(period) - 1 - 累计收益率
    3. consistency = rolling_mean(sign(ret)) - 方向一致性
    4. intensity = abs(cum_ret) / rolling_std(ret) - 动量强度(收益/波动)
    5. raw = cum_ret * abs(consistency) * intensity
    6. factor = -raw - 取反作为反转信号

输出:
    因子值DataFrame,负向因子(做多低值组)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.1

废弃原因:
    P2 ICIR不达标(P1 IC=0.0230/ICIR=0.0845,P2 IC=0.0133/ICIR=0.0464<0.05)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算MomentumExhaustion因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    period = 36  # 3小时

    # 计算单周期收益率
    ret = close.pct_change()

    # 累计收益率
    cum_ret = close / close.shift(period) - 1

    # 方向一致性: 正收益比例 - 负收益比例
    ret_sign = np.sign(ret)
    consistency = ret_sign.rolling(window=period, min_periods=1).mean()

    # 动量强度: 累计收益 / 波动率
    volatility = ret.rolling(window=period, min_periods=1).std()
    intensity = cum_ret.abs() / volatility.replace(0, np.nan)

    # 综合信号: 累计收益 * 一致性绝对值 * 强度
    raw_signal = cum_ret * consistency.abs() * intensity

    # 取反作为反转信号: 强上涨趋势 -> 做空机会
    factor = -raw_signal

    return factor
