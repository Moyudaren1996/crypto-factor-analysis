"""
Volatility指标 - Volatility Asymmetry Momentum (波动率非对称动量)

因子描述:
    波动率非对称动量因子,基于上涨波动与下跌波动的差异变化捕捉反转机会。

    核心逻辑:
    1. 分别计算上涨收益的波动贡献和下跌收益的波动贡献
    2. 计算二者之差(非对称性): upside_var - downside_var
    3. 跟踪非对称性的动量变化,而非绝对水平
    4. 当非对称性动量急剧变化时,往往预示着市场情绪转换

    与现有因子的区别:
    - 不使用价格位置(避免与RSI/Stoch相关)
    - 基于波动率结构变化而非波动率水平
    - 关注上下行波动的相对变化趋势

参数:
    vol_period: 24 (2小时, 计算波动率)
    mom_period: 48 (4小时, 计算动量变化)

计算公式:
    1. up_returns = max(returns, 0)^2 - 上涨收益方差贡献
    2. down_returns = min(returns, 0)^2 - 下跌收益方差贡献
    3. up_vol = rolling_sum(up_returns, vol_period) - 上涨波动
    4. down_vol = rolling_sum(down_returns, vol_period) - 下跌波动
    5. asym = (up_vol - down_vol) / (up_vol + down_vol) - 非对称性(-1到1)
    6. factor = asym - asym.shift(mom_period) - 非对称性动量变化

输出:
    因子值DataFrame, 正值表示上涨波动相对增强(可能预示反转下跌),
    负值表示下跌波动相对增强(可能预示反转上涨)

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-29
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率非对称动量因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    close = data['close']

    # 定义参数
    vol_period = 24    # 2小时计算波动率窗口
    mom_period = 48    # 4小时计算动量变化

    # 计算收益率
    returns = close.pct_change()

    # 分离上涨和下跌收益的方差贡献
    up_returns_sq = np.where(returns > 0, returns ** 2, 0)
    down_returns_sq = np.where(returns < 0, returns ** 2, 0)

    # 转换为DataFrame
    up_returns_sq = pd.DataFrame(up_returns_sq, index=returns.index, columns=returns.columns)
    down_returns_sq = pd.DataFrame(down_returns_sq, index=returns.index, columns=returns.columns)

    # 计算滚动上涨/下跌波动
    up_vol = up_returns_sq.rolling(vol_period).sum()
    down_vol = down_returns_sq.rolling(vol_period).sum()

    # 计算波动率非对称性 (范围约-1到1)
    total_vol = up_vol + down_vol
    asym = (up_vol - down_vol) / total_vol.replace(0, np.nan)

    # 计算非对称性的动量变化
    asym_momentum = asym - asym.shift(mom_period)

    # 因子: 非对称性动量变化 * -1 (反转逻辑)
    # 当上涨波动突然增强(asym_momentum > 0)时,预期反转下跌,因子为负
    factor = -asym_momentum

    return factor
