"""
Oscillator指标 - Volume Confirmed Momentum Reversion

因子描述:
    成交量确认的动量反转因子,通过成交量异常来确认价格反转信号。
    核心逻辑:当价格动量达到极值但成交量萎缩时，预示反转。
    即价格继续运动但量能不足，这是力量衰减的信号。

参数:
    momentum_period: 12 (1小时,用于计算动量)
    volume_period: 24 (2小时,用于计算成交量异常)

计算公式:
    1. momentum = ROC(close, 12)  # 12期动量
    2. momentum_ma = SMA(momentum, 24)  # 动量均线(基准)
    3. extreme_momentum = momentum > 2std或 momentum < -2std  # 极端动量
    4. volume_rate = volume / SMA(volume, 24)  # 成交量相对强度
    5. low_volume = volume_rate < 0.8  # 成交量萎缩
    6. reversal_signal = -momentum * extreme_momentum * low_volume  # 反转信号

输出:
    因子值DataFrame,反映动量极值但成交量不足的反转机会

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-27
版本: v1.2
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量确认的动量反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    volume = data['volume']

    # 定义参数
    momentum_period = 12  # 动量计算周期(1小时)
    volume_period = 24    # 成交量基准窗口(2小时)
    std_period = 24       # 标准差计算窗口(2小时)

    # 1. 计算短期动量(变化率)
    momentum = (close - close.shift(momentum_period)) / close.shift(momentum_period) * 100

    # 2. 计算动量的中期均线(基准)和标准差
    momentum_ma = momentum.rolling(std_period).mean()
    momentum_std = momentum.rolling(std_period).std()

    # 3. 识别动量的极端程度
    # 动量相对于其均线超过2倍标准差
    momentum_zscore = (momentum - momentum_ma) / (momentum_std + 1e-8)
    is_extreme_momentum = momentum_zscore.abs() > 2

    # 4. 计算成交量相对强度
    volume_ma = volume.rolling(volume_period).mean()
    volume_ratio = volume / (volume_ma + 1e-8)

    # 5. 识别成交量萎缩(相对强度<0.8,即低于80%的平均值)
    is_low_volume = volume_ratio < 0.8

    # 6. 反转信号的构造
    # 当动量为正极值(上涨过度)且成交量低时，预示下跌反转(负信号)
    # 当动量为负极值(下跌过度)且成交量低时，预示上涨反转(正信号)

    # 动量极值方向
    momentum_direction = np.sign(momentum)  # +1表示上涨动量，-1表示下跌动量

    # 反转信号=反向的极值动量*确认条件
    # 极端动量+成交量萎缩 = 强反转信号
    reversal_signal = -momentum_direction * momentum.abs() * is_extreme_momentum.astype(float) * is_low_volume.astype(float)

    return reversal_signal
