"""
Momentum指标 - Energy Decay (动量能量衰减)

因子描述:
    动量能量衰减因子，衡量累积动量能量的衰减速度。
    核心逻辑：
    1. 计算滚动窗口内的累积绝对收益率作为"动量能量"
    2. 计算当前净收益率与累积能量的比值作为"能量效率"
    3. 当能量效率下降（大量能量消耗但价格净变化小）时，表明趋势可能疲劳
    4. 结合价格方向和能量效率变化，识别反转信号

    假设：当动量消耗大量能量（波动）但价格净变化较小时，趋势动能衰竭，存在反转机会

参数:
    short_period: 18 (1.5小时)
    long_period: 72 (6小时)

计算公式:
    1. abs_ret = |pct_change(1)|
    2. total_energy = rolling_sum(abs_ret, short_period)  (累计能量)
    3. net_move = |close - close.shift(short_period)| / close.shift(short_period)  (净位移)
    4. efficiency = net_move / (total_energy + epsilon)  (能量效率)
    5. eff_change = efficiency - efficiency.shift(6)  (效率变化)
    6. direction = sign(close - close.shift(short_period))  (方向)
    7. factor = -direction * efficiency_zscore  (方向×效率异常程度，取反做反转)

输出:
    因子值DataFrame，负向因子

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算动量能量衰减因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    short_period = 18  # 1.5小时
    long_period = 72   # 6小时
    epsilon = 1e-10

    # 1. 计算单周期绝对收益率
    single_ret = close.pct_change().abs()

    # 2. 累积动量能量 (短期)
    total_energy = single_ret.rolling(short_period).sum()

    # 3. 净位移 (短期价格变化)
    net_move = (close - close.shift(short_period)).abs() / close.shift(short_period)

    # 4. 能量效率 = 净位移 / 总能量
    efficiency = net_move / (total_energy + epsilon)

    # 5. 效率的Z-score标准化 (相对于长期)
    eff_mean = efficiency.rolling(long_period).mean()
    eff_std = efficiency.rolling(long_period).std()
    eff_zscore = (efficiency - eff_mean) / (eff_std + epsilon)

    # 6. 方向 (当前相对于short_period前)
    direction = np.sign(close - close.shift(short_period))

    # 7. 最终因子: 高效率(趋势强劲) + 正方向 -> 正值
    # 取反做反转: 高值(趋势强劲)做空，低值(趋势疲劳)做多
    factor = -direction * eff_zscore

    return factor
