"""
Volatility指标 - Efficiency Momentum (效率动量)

因子描述:
    结合价格运动效率(Kaufman Efficiency Ratio)和动量指标。
    计算效率比率(ER)的Z-score，并将其与动量(ROC)相乘。
    逻辑：
    - 当效率显著高于历史均值(Z_ER > 0)时，视为强趋势，跟随动量方向(Trend Following)。
    - 当效率显著低于历史均值(Z_ER < 0)时，视为震荡/噪音，反向交易动量(Mean Reversion)。

参数:
    period_mom: 24 (动量和效率计算周期，约2小时)
    period_norm: 96 (效率标准化周期，约8小时)

计算公式:
    ER = Abs(Close_t - Close_{t-24}) / Sum(Abs(Close_i - Close_{i-1})) for i in t-23 to t
    Z_ER = (ER - Mean(ER, 96)) / Std(ER, 96)
    ROC = (Close_t - Close_{t-24}) / Close_{t-24}
    Factor = ROC * Z_ER

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2024-05-22
版本: v1.1
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算效率动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    
    # 参数设置
    period_mom = 24
    period_norm = 96
    
    # 1. 计算动量 (ROC)
    momentum = (close - close.shift(period_mom)) / close.shift(period_mom)
    
    # 2. 计算效率比率 (Efficiency Ratio)
    # 净位移 (Net Change)
    net_change = (close - close.shift(period_mom)).abs()
    
    # 总路径长度 (Total Path Length)
    # sum of absolute period-to-period changes over the window
    path_length = close.diff().abs().rolling(period_mom).sum()
    
    # 处理分母为0的情况
    efficiency_ratio = net_change / path_length.replace(0, np.nan)
    
    # 3. 计算效率比率的Z-score
    er_mean = efficiency_ratio.rolling(period_norm).mean()
    er_std = efficiency_ratio.rolling(period_norm).std()
    
    # Z-score standardization
    er_z = (efficiency_ratio - er_mean) / er_std
    
    # 4. 组合因子
    factor = momentum * er_z
    
    return factor
