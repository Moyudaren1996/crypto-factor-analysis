"""
Trend指标 - Slope Consistency (趋势斜率一致性因子)

因子描述:
    基于价格线性回归斜率和拟合优度(R²)来衡量趋势强度和稳定性。
    稳定的趋势表现为：价格沿着一个方向以相对稳定的速度移动。
    斜率代表趋势方向和速度，R²代表趋势的稳定程度。

    与RSI/TSI的本质区别：
    - RSI/TSI基于涨跌幅的相对强弱和平滑
    - 本因子基于线性回归的斜率和拟合优度
    - 关注的是趋势的"质量"而非单纯的涨跌

参数:
    period: 36 (3小时，用于计算回归)

计算公式:
    1. 对每个滚动窗口内的价格进行线性回归: price = a + b*t
    2. slope = b (回归斜率，标准化后)
    3. r_squared = 拟合优度
    4. factor = slope * sqrt(r_squared)  # 斜率用R²平方根加权

    当趋势稳定向上时：正斜率 + 高R² = 高正值
    当趋势稳定向下时：负斜率 + 高R² = 高负值
    当震荡无趋势时：任意斜率 + 低R² = 接近0

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2024-12-27
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Slope Consistency因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    period = 36  # 回归窗口 (3小时)

    # 使用向量化方法计算滚动线性回归
    # y = a + b*x, 其中 x = 0, 1, 2, ..., period-1

    # 预计算常量
    x = np.arange(period)
    x_mean = x.mean()
    x_var = ((x - x_mean) ** 2).sum()

    # 滚动计算
    def calc_slope_r2(y_series):
        """计算斜率和R²"""
        result = pd.Series(index=y_series.index, dtype=float)

        # 使用rolling窗口
        for i in range(period - 1, len(y_series)):
            y = y_series.iloc[i - period + 1:i + 1].values
            if np.isnan(y).any():
                result.iloc[i] = np.nan
                continue

            y_mean = y.mean()

            # 计算斜率 b = Cov(x,y) / Var(x)
            cov_xy = ((x - x_mean) * (y - y_mean)).sum()
            slope = cov_xy / x_var

            # 标准化斜率 (除以价格均值)
            slope_normalized = slope / y_mean * period

            # 计算R²
            y_pred = y_mean + slope * (x - x_mean)
            ss_res = ((y - y_pred) ** 2).sum()
            ss_tot = ((y - y_mean) ** 2).sum()

            if ss_tot == 0:
                r_squared = 0
            else:
                r_squared = 1 - ss_res / ss_tot
                r_squared = max(0, r_squared)  # 确保非负

            # 因子 = 斜率 * sqrt(R²)
            result.iloc[i] = slope_normalized * np.sqrt(r_squared)

        return result

    # 对每列应用计算
    factor = close.apply(calc_slope_r2)

    return factor
