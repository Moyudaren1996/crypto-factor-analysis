"""
Momentum指标 - Volume Weighted Trend (成交量加权趋势动量)

因子描述:
    成交量加权趋势动量因子,通过计算收益率序列的线性回归斜率来衡量动量趋势
    使用成交量作为权重,高成交量时的价格变化对趋势判断更重要
    当斜率为正且成交量支持时,表明上涨趋势稳固;反之则表明下跌趋势

参数:
    period: 24 (2小时)

计算公式:
    returns = close.pct_change()
    relative_volume = volume / volume.rolling(period).mean()
    weighted_returns = returns * relative_volume

    使用滚动窗口计算加权收益率的线性回归斜率:
    slope = rolling_linear_regression_slope(weighted_returns, period)

    factor = slope * sqrt(period)  # 标准化斜率

输出:
    因子值DataFrame,正值表示上涨趋势,负值表示下跌趋势

数据依赖:
    - close: 收盘价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-28
版本: v3.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量加权趋势动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']
    volume = data['volume']

    # 定义参数
    period = 24  # 2小时

    # 计算收益率
    returns = close.pct_change()

    # 计算相对成交量强度
    vol_ma = volume.rolling(period).mean()
    relative_volume = volume / (vol_ma + 1e-10)
    relative_volume = relative_volume.clip(0.1, 10)  # 限制极值

    # 计算成交量加权收益率
    weighted_returns = returns * np.sqrt(relative_volume)

    # 计算滚动线性回归斜率
    # 使用向量化方法: slope = cov(x, y) / var(x)
    # 其中 x 是时间序列 [0, 1, 2, ..., period-1]
    # y 是 weighted_returns

    # 对于固定窗口，x的统计量是常数
    # mean(x) = (period-1)/2
    # var(x) = (period^2 - 1) / 12

    x_mean = (period - 1) / 2
    x_var = (period ** 2 - 1) / 12

    # 计算滚动均值
    y_mean = weighted_returns.rolling(period).mean()

    # 计算 cov(x, y) = E[x*y] - E[x]*E[y]
    # E[x*y] 需要用权重来计算
    # 使用简化方法：直接计算斜率

    def calc_slope(arr):
        if len(arr) < period or np.isnan(arr).any():
            return np.nan
        x = np.arange(len(arr))
        try:
            slope = np.polyfit(x, arr, 1)[0]
            return slope
        except:
            return np.nan

    # 使用rolling apply计算斜率
    slope = weighted_returns.rolling(period).apply(
        lambda y: np.polyfit(np.arange(len(y)), y, 1)[0] if len(y) == period and not np.isnan(y).any() else np.nan,
        raw=True
    )

    # 标准化斜率
    factor = slope * np.sqrt(period)

    return factor
