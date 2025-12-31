"""
Oscillator指标 - IVR (Intraday Volatility Reversion)

因子描述:
    日内波动相对强度反转因子,衡量价格在高低区间相对位置的波动性和极端程度。
    当价格持续处于极端位置(接近最高或最低)且成交量出现突变时,预示着反转机会。

    核心逻辑:
    1. 计算价格在N期高低区间的相对位置(0-1之间)
    2. 计算该相对位置的短期波动率,衡量位置变化的剧烈程度
    3. 计算位置偏离中性(0.5)的极端程度
    4. 用成交量变化率的波动性作为确认信号
    5. 组合为反转因子:高波动+极端位置+成交量突变 = 反转信号

参数:
    short_period: 3 (15分钟,短期波动观察窗口)
    long_period: 12 (1小时,长期高低价参考窗口)

计算公式:
    1. price_position = (close - low_12) / (high_12 - low_12)  # 价格相对位置
    2. position_std = Std(price_position, 3)  # 位置波动率
    3. extreme_level = |price_position - 0.5| * 2  # 极端程度(0-1)
    4. volume_volatility = Std(volume.pct_change(), 3)  # 成交量变化波动
    5. IVR = position_std * extreme_level * volume_volatility  # 组合因子(正值)
    6. reversion_signal = -IVR  # 反转信号(负值表示做空极端,正值表示做多极端)

输出:
    因子值DataFrame,数值越负表示反转做空信号越强,越正表示反转做多信号越强

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-08
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算日内波动相对强度反转因子

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
    short_period = 3   # 短期波动观察窗口(15分钟)
    long_period = 12   # 长期高低价参考窗口(1小时)

    # 1. 计算价格在long_period内的相对位置(0-1之间)
    rolling_high = high.rolling(long_period).max()
    rolling_low = low.rolling(long_period).min()
    price_range = rolling_high - rolling_low
    # 避免除零,当价格range为0时设为NaN
    price_range = price_range.replace(0, np.nan)
    price_position = (close - rolling_low) / price_range

    # 2. 计算相对位置的短期波动率
    position_std = price_position.rolling(short_period).std()

    # 3. 计算位置偏离中性(0.5)的极端程度(0-1之间)
    # 当价格position接近0或1时,extreme_level接近1
    extreme_level = (price_position - 0.5).abs() * 2

    # 4. 计算成交量变化率的波动性
    volume_pct_change = volume.pct_change()
    volume_volatility = volume_pct_change.rolling(short_period).std()

    # 5. 组合因子:位置波动 * 极端程度 * 成交量波动
    # 这个值越大,表示在极端位置的波动越剧烈,成交量变化越大
    ivr_signal = position_std * extreme_level * volume_volatility

    # 6. 反转信号:取负值,因为极端位置意味着反转机会
    # 但需要考虑方向:当price_position > 0.5时(价格偏高),反转向下,因子应为负
    # 当price_position < 0.5时(价格偏低),反转向上,因子应为正
    direction = np.sign(0.5 - price_position)  # 高位为负,低位为正
    reversion_signal = direction * ivr_signal

    return reversion_signal
