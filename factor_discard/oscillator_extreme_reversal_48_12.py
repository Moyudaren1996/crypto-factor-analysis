"""
Oscillator指标 - Extreme Range Reversal (极值区间反转)

因子描述:
    极值区间反转因子,捕捉价格触及近期极值后的均值回归机会
    当价格在滚动窗口内处于极端分位数(>0.9或<0.1)时往往预示反转
    通过计算价格相对位置、动量强度和波动率调整识别过度延伸

参数:
    window: 48 (4小时,计算价格分位数的窗口)
    momentum: 12 (1小时,计算价格动量的周期)

计算公式:
    1. price_rank = close.rolling(window).rank(pct=True)  # 价格在窗口内的分位数位置
    2. extreme_signal = np.where(price_rank > 0.9, price_rank - 0.9,  # 上极值信号
                                 np.where(price_rank < 0.1, 0.1 - price_rank, 0))  # 下极值信号
    3. momentum = close.pct_change(momentum)  # 价格动量
    4. volatility = close.rolling(window).std() / close  # 相对波动率
    5. factor = -extreme_signal * abs(momentum) / (volatility + 1e-8)  # 极值×动量/波动率,取负值为反转信号

输出:
    因子值DataFrame,正值表示价格在低位预期反转上涨,负值表示价格在高位预期反转下跌

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2025-12-14
版本: v1.2
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算Extreme Range Reversal因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    close = data['close']

    # 定义参数
    window = 48      # 4小时
    momentum_period = 12  # 1小时

    # 1. 计算价格在滚动窗口内的分位数位置(0-1之间)
    price_rank = close.rolling(window, min_periods=1).rank(pct=True)

    # 2. 提取极值信号
    # 当price_rank > 0.9时,处于高位,信号为正(price_rank - 0.9)
    # 当price_rank < 0.1时,处于低位,信号为正(0.1 - price_rank)
    # 其他情况信号为0
    extreme_signal = np.where(
        price_rank > 0.9,
        price_rank - 0.9,  # 高位:0-0.1之间
        np.where(
            price_rank < 0.1,
            0.1 - price_rank,  # 低位:0-0.1之间
            0  # 非极值区域
        )
    )
    extreme_signal = pd.DataFrame(extreme_signal, index=close.index, columns=close.columns)

    # 3. 计算价格动量(绝对值,衡量变化强度)
    momentum = close.pct_change(momentum_period).abs()

    # 4. 计算相对波动率(标准差/价格)
    rolling_std = close.rolling(window, min_periods=1).std()
    volatility = rolling_std / close

    # 5. 组合因子:极值信号 × 动量强度 / 波动率
    # 取负值作为反转信号:
    # - 高位(price_rank>0.9)且动量大→正信号→取负→预期反转下跌(负收益)
    # - 低位(price_rank<0.1)且动量大→正信号→取负→预期反转上涨(正收益)但这里逻辑错了
    # 修正:低位应该产生正因子值(预期上涨),高位应该产生负因子值(预期下跌)
    # 所以对于低位(price_rank<0.1),应该取正值

    # 重新设计:extreme_signal_signed,低位为正,高位为负
    extreme_signal_signed = np.where(
        price_rank > 0.9,
        -(price_rank - 0.9),  # 高位:负信号
        np.where(
            price_rank < 0.1,
            (0.1 - price_rank),   # 低位:正信号
            0
        )
    )
    extreme_signal_signed = pd.DataFrame(extreme_signal_signed, index=close.index, columns=close.columns)

    # 用动量强度和波动率调整
    factor = extreme_signal_signed * momentum / (volatility + 1e-8)

    return factor
