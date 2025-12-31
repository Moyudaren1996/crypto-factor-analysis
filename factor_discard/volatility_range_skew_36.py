"""
Volatility指标 - Intrabar Range Skewness

因子描述:
    日内波幅偏度因子,捕捉波动率的非对称性变化。
    计算每根K线的(close-open)/(high-low)比率,反映K线内部价格运动方向。
    当这个比率接近1时,说明收盘价接近最高价(看涨K线);
    接近-1时,收盘价接近最低价(看跌K线);接近0时无方向性。
    计算该比率的滚动偏度,捕捉近期K线模式的非对称性。
    当偏度极端(正或负)时,预示动量可能延续或反转。

参数:
    period: 36 (3小时滚动窗口)

计算公式:
    range_position = (close - open) / (high - low)  # 范围[-1, 1]
    factor = rolling_skew(range_position, period)

输出:
    因子值DataFrame,价格在日内波幅中位置的偏度

数据依赖:
    - open: 开盘价 (必需)
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
    计算Intrabar Range Skewness因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    open_price = data['open']
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    period = 36  # 3小时

    # 计算日内波幅
    hl_range = high - low

    # 避免除零:当high=low时,设置为NaN
    hl_range = hl_range.replace(0, np.nan)

    # 计算收盘价在开盘到收盘区间的相对位置
    # 这反映了K线是上涨还是下跌,以及幅度
    range_position = (close - open_price) / hl_range

    # 计算滚动偏度
    factor = range_position.rolling(period).skew()

    return factor
