"""
Momentum指标 - 动量连续性强度因子 (Momentum Streak Intensity)

因子描述:
    结合收益率方向的连续性和强度来识别动量状态。
    当收益率方向持续一致且强度较大时，可能出现趋势延续或过度反应后的反转。

    核心逻辑：
    1. 计算收益率符号的累计连续数(streak)
    2. 计算累计收益强度相对于ATR的比值
    3. 连续性×强度比 = 动量惯性指标
    4. 用历史分位数识别极端值

参数:
    return_period: 3 (15分钟收益率周期)
    streak_period: 24 (2小时，统计连续性的窗口)
    atr_period: 48 (4小时，ATR窗口)

计算公式:
    1. returns = close / close.shift(return_period) - 1
    2. sign_returns = sign(returns)
    3. streak = 累计连续同向次数(正负分开统计)
    4. cum_returns = 滚动窗口内累计收益
    5. atr = 滚动窗口内真实波幅均值
    6. intensity = cum_returns / atr
    7. factor = streak * intensity 的时序标准化

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-28
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算动量连续性强度因子

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
    return_period = 3   # 15分钟
    streak_period = 24  # 2小时
    atr_period = 48     # 4小时
    epsilon = 1e-8

    # 计算短期收益率
    returns = close / close.shift(return_period) - 1

    # 计算收益方向
    sign_returns = np.sign(returns)

    # 计算方向变化点
    sign_change = (sign_returns != sign_returns.shift(1)).astype(int)

    # 计算streak组ID(每次方向变化时递增)
    streak_group = sign_change.cumsum()

    # 计算每个streak组内的累计次数
    def calc_streak(df):
        # 对每列独立计算
        result = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
        for col in df.columns:
            groups = streak_group[col]
            counts = groups.groupby(groups).cumcount() + 1
            result[col] = counts.values * sign_returns[col].values  # 带方向的连续次数
        return result

    streak = calc_streak(sign_returns)

    # 计算ATR
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=0).groupby(level=0).max()
    # 正确计算TR
    tr = tr1.where(tr1 > tr2, tr2).where(tr1.where(tr1 > tr2, tr2) > tr3, tr3)
    atr = tr.rolling(atr_period).mean()

    # 计算累计收益(滚动窗口)
    cum_returns = returns.rolling(streak_period).sum()

    # 计算强度比 = 累计收益 / ATR
    intensity = cum_returns / (atr + epsilon)

    # 计算动量惯性 = streak * intensity
    # streak带方向，intensity带方向，乘积反映动量惯性强度
    momentum_inertia = streak * intensity.abs()

    # 用时序Z-score标准化
    inertia_mean = momentum_inertia.rolling(atr_period * 2).mean()
    inertia_std = momentum_inertia.rolling(atr_period * 2).std()
    z_score = (momentum_inertia - inertia_mean) / (inertia_std + epsilon)

    # 负向因子：极端高值预示反转
    factor = -z_score

    return factor
