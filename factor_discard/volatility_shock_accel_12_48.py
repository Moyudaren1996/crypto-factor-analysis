"""
Volatility指标 - Shock Acceleration (波动率冲击加速度)

因子描述:
    波动率冲击加速度因子,衡量真实波幅(TR)变化的二阶导数(加速度)。
    当波动率突然加速扩张时,通常预示着价格过度反应,存在反转机会。
    当波动率加速收缩时,市场进入盘整状态,可能积蓄动能。

    核心思想:
    1. 计算TR的一阶变化(速度) = TR短期均值 - TR长期均值
    2. 计算速度的变化(加速度) = 当前速度 - 过去速度
    3. 用历史百分位排名进行标准化
    4. 结合价格方向生成反转信号

参数:
    short_period: 12 (1小时) - 短期波动率窗口
    long_period: 48 (4小时) - 长期波动率窗口

计算公式:
    TR = max(high - low, abs(high - close.shift(1)), abs(low - close.shift(1)))
    TR_short = TR.rolling(short_period).mean()
    TR_long = TR.rolling(long_period).mean()
    vol_velocity = TR_short / TR_long - 1
    vol_accel = vol_velocity - vol_velocity.shift(short_period)
    accel_rank = vol_accel.rolling(long_period).rank(pct=True)
    price_direction = sign(close - close.shift(short_period))
    factor = -accel_rank * price_direction

输出:
    因子值DataFrame,负向因子(做多低值组)

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2024-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率冲击加速度因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    short_period = 12  # 1小时
    long_period = 48   # 4小时

    # 计算真实波幅 (True Range)
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=0).groupby(level=0).max()
    # 处理concat后的问题,用更简单的方式
    tr = np.maximum(np.maximum(tr1, tr2), tr3)

    # 计算短期和长期波动率均值
    tr_short = tr.rolling(short_period).mean()
    tr_long = tr.rolling(long_period).mean()

    # 计算波动率速度 (一阶变化)
    vol_velocity = tr_short / tr_long - 1

    # 计算波动率加速度 (二阶变化)
    vol_accel = vol_velocity - vol_velocity.shift(short_period)

    # 用滚动百分位排名进行标准化
    accel_rank = vol_accel.rolling(long_period).rank(pct=True)

    # 结合价格方向 (价格上涨时波动率加速扩张 -> 过度反应 -> 看跌)
    price_direction = np.sign(close - close.shift(short_period))

    # 因子值: 波动率加速扩张 + 价格上涨 -> 负值 (看跌)
    # 波动率加速收缩 + 价格下跌 -> 正值 (看涨)
    factor = -accel_rank * price_direction

    return factor
