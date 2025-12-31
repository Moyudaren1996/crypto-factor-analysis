"""
波动率指标 - Volatility Term Structure (波动率期限结构)

因子描述:
    波动率期限结构因子，衡量极短期波动率与中期波动率的比值变化。

    核心假设：
    1. 波动率期限结构（短期/中期比值）反映市场紧张程度
    2. 短期波动率急剧上升相对中期（陡峭化）往往预示价格反转
    3. 短期波动率相对中期平缓化可能预示趋势延续
    4. 结合横截面排名可识别相对异常

    计算逻辑：
    1. 计算极短期Parkinson波动率（6周期=30分钟）
    2. 计算中期Parkinson波动率（36周期=3小时）
    3. 计算比值并做时序Z-score标准化
    4. 结合价格收益方向形成因子

参数:
    short_period: 6 (30分钟)
    long_period: 36 (3小时)
    zscore_window: 72 (6小时)

计算公式:
    1. vol_short = rolling_std(log(high/low), short_period)
    2. vol_long = rolling_std(log(high/low), long_period)
    3. term_ratio = vol_short / vol_long
    4. term_z = (term_ratio - rolling_mean) / rolling_std
    5. returns = close / close.shift(short_period) - 1
    6. factor = -term_z * sign(returns)  # 高短期波动率+上涨 = 反转信号

输出:
    因子值DataFrame

数据依赖:
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
    计算Volatility Term Structure因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    short_period = 6     # 30分钟
    long_period = 36     # 3小时
    zscore_window = 72   # 6小时

    # 计算Parkinson波动率 (基于高低价的波动率估计)
    log_hl = np.log(high / low.replace(0, np.nan))

    # 短期波动率
    vol_short = log_hl.rolling(short_period).std()

    # 中期波动率
    vol_long = log_hl.rolling(long_period).std()

    # 计算期限结构比值
    term_ratio = vol_short / vol_long.replace(0, np.nan)

    # Z-score标准化
    term_mean = term_ratio.rolling(zscore_window).mean()
    term_std = term_ratio.rolling(zscore_window).std()
    term_z = (term_ratio - term_mean) / term_std.replace(0, np.nan)

    # 计算短期收益方向
    returns = close / close.shift(short_period) - 1
    ret_sign = np.sign(returns)

    # 因子：高短期波动率比+上涨方向 = 预示反转 (取负)
    # 低短期波动率比+下跌方向 = 预示反转 (取负)
    factor = -term_z * ret_sign

    return factor
