"""
Oscillator指标 - Extreme Volume Reversal (极端位置量价反转)

因子描述:
    结合价格极端位置与成交量异常识别反转机会
    核心逻辑:价格极端位置+成交量反向变化=反转信号
    - 高位+缩量=看跌反转(买盘枯竭)
    - 低位+放量=看涨反转(卖盘枯竭)
    
    区别于现有因子:
    - 不同于单纯价格因子(RSI/Stoch/Williams R)
    - 不同于单纯成交量因子(CMF/MFI/OBV)
    - 同时捕捉价格极端性+成交量异常性的交叉信号

参数:
    position_period: 24 (2小时,计算价格位置)
    volume_period: 3 (15分钟,成交量变化)

计算公式:
    1. price_position = (close - low_24) / (high_24 - low_24)  # 价格在24期高低区间的位置
    2. extreme_position = price_position - 0.5                  # 偏离中位的程度(-0.5到0.5)
    3. volume_change = (volume - volume.shift(3)) / volume.shift(3)  # 成交量变化率
    4. volume_anomaly = volume_change - volume_change.rolling(24).mean()  # 成交量异常
    5. factor = -extreme_position * volume_anomaly              # 反转信号

输出:
    因子值DataFrame
    正值表示预期上涨(低位放量或高位缩量)
    负值表示预期下跌(高位放量或低位缩量)

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-10
版本: v1.0 (优化2)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Extreme Volume Reversal因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']

    # 定义参数
    position_period = 24  # 价格位置周期(2小时)
    volume_period = 3     # 成交量变化周期(15分钟)

    # 1. 计算价格在高低区间的相对位置
    rolling_high = high.rolling(position_period).max()
    rolling_low = low.rolling(position_period).min()
    range_diff = rolling_high - rolling_low
    range_diff = range_diff.replace(0, np.nan)
    
    price_position = (close - rolling_low) / range_diff  # 0到1之间
    
    # 2. 计算偏离中位的极端程度
    extreme_position = price_position - 0.5  # -0.5(极端低位)到0.5(极端高位)

    # 3. 计算成交量变化率
    volume_change = (volume - volume.shift(volume_period)) / (volume.shift(volume_period) + 1e-8)

    # 4. 计算成交量异常(相对于均值的偏离)
    volume_ma = volume_change.rolling(position_period).mean()
    volume_anomaly = volume_change - volume_ma

    # 5. 计算反转信号:极端位置 × 成交量异常
    # 高位(positive extreme) × 缩量(negative anomaly) = 负值 → 取负后为正 → 看跌反转
    # 低位(negative extreme) × 放量(positive anomaly) = 负值 → 取负后为正 → 看涨反转
    factor = -extreme_position * volume_anomaly

    return factor
