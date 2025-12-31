"""
Oscillator指标 - PVDA (Price-Volume Divergence Asymmetry)

因子描述:
    价量背离非对称因子,捕捉价格变化与成交量变化方向不一致的异常模式。
    核心逻辑:当价格上涨但成交量下降(或价格下跌但成交量上升)时,预测反转。
    基于市场微观结构理论,无量上涨或放量下跌往往预示趋势不可持续。

参数:
    short_period: 2 (超短期,10分钟)
    long_period: 6 (短期,30分钟)

计算公式:
    1. price_change = close - close.shift(2)  # 2期价格变化
    2. volume_change = volume - volume.shift(2)  # 2期成交量变化
    3. price_sign = np.sign(price_change)  # 价格变化方向
    4. volume_sign = np.sign(volume_change)  # 成交量变化方向
    5. divergence = price_sign - volume_sign  # 背离信号[-2,2]
    6. price_strength = abs(price_change) / (close.shift(2) + 1e-8)  # 价格变化强度
    7. volume_strength = abs(volume_change) / (volume.shift(2) + 1e-8)  # 成交量变化强度
    8. pvda = divergence * price_strength / (volume_strength + 0.1)  # 背离强度

    逻辑:divergence=2时(价格上涨+成交量下降),预测反转下跌
         divergence=-2时(价格下跌+成交量上升),预测反转上涨
         背离强度越大,反转预期越强

输出:
    因子值DataFrame,数值越大预测下跌反转,越小预测上涨反转

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-08
版本: v4.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算PVDA因子

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
    short_period = 2
    long_period = 6

    # 计算价格和成交量的变化
    price_change = close - close.shift(short_period)
    volume_change = volume - volume.shift(short_period)

    # 计算变化方向
    price_sign = np.sign(price_change)
    volume_sign = np.sign(volume_change)

    # 计算背离信号
    # divergence = 2: 价格上涨+成交量下降(看跌信号)
    # divergence = -2: 价格下跌+成交量上升(看涨信号)
    # divergence = 0: 同向变化(无背离)
    divergence = price_sign - volume_sign

    # 计算价格变化强度(百分比)
    price_strength = price_change.abs() / (close.shift(short_period) + 1e-8)

    # 计算成交量变化强度(百分比)
    volume_strength = volume_change.abs() / (volume.shift(short_period) + 1e-8)

    # 价量背离非对称因子
    # 当背离发生时,如果价格变化大但成交量变化小,反转信号更强
    pvda = divergence * price_strength / (volume_strength + 0.1)

    # 对因子值进行6期平滑,减少噪音
    pvda_smoothed = pvda.rolling(long_period).mean()

    return pvda_smoothed
