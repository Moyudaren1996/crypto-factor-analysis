"""
Momentum指标 - VOLCONFIRM (Volume Confirmed Reversal)

因子描述:
    成交量确认的多周期动量反转因子,基于Alpha101反转策略改进
    核心逻辑:
    1. 短期反转:短期(3期)收益率的反转信号
    2. 中期趋势:中期(12期)价格趋势作为过滤
    3. 成交量确认:只有成交量放大的反转才可靠
    4. 波动率调整:高波动时降低信号权重
    5. 截面标准化:排名转换到[0,1]区间

参数:
    short_period: 3 (15分钟,短期反转)
    medium_period: 12 (1小时,中期趋势)

计算公式:
    1. short_ret = close / close.shift(3) - 1 - 短期收益率
    2. medium_ret = close / close.shift(12) - 1 - 中期收益率
    3. reversal = -short_ret - 短期反转信号(收益率取负)
    4. volume_ratio = volume / volume.rolling(12).mean() - 成交量相对强度
    5. volume_confirm = reversal * volume_ratio - 成交量确认的反转
    6. trend_filter = Sign(medium_ret) - 中期趋势方向
    7. atr = ATR(3) / close - 相对波动率
    8. vol_adj = 1 / (1 + atr) - 波动率衰减权重
    9. factor = Rank((volume_confirm * trend_filter * vol_adj)) - 最终因子

输出:
    因子值DataFrame,值域为[0, 1],越大表示反转信号越强

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - volume: 成交量 (必需)

创建日期: 2025-12-07
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算成交量确认的多周期动量反转因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    close = data['close']
    high = data['high']
    low = data['low']
    volume = data['volume']

    # 定义参数
    short_period = 3   # 15分钟
    medium_period = 12  # 1小时

    # 1. 计算短期和中期收益率
    short_return = close / close.shift(short_period) - 1
    medium_return = close / close.shift(medium_period) - 1

    # 2. 短期反转信号(收益率取负,涨多了看跌,跌多了看涨)
    reversal_signal = -short_return

    # 3. 成交量相对强度
    volume_ma = volume.rolling(medium_period).mean()
    volume_ratio = volume / volume_ma

    # 4. 成交量确认的反转信号
    # 只有在成交量放大时,反转信号才有效
    volume_confirmed = reversal_signal * volume_ratio

    # 5. 中期趋势过滤
    # 只在顺应中期趋势方向的反转才采纳
    trend_direction = np.sign(medium_return)

    # 6. 计算ATR作为波动率度量
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()

    # 为每个币种计算真实波动幅度
    if isinstance(close, pd.DataFrame):
        true_range = pd.DataFrame(index=close.index, columns=close.columns)
        atr = pd.DataFrame(index=close.index, columns=close.columns)

        for col in close.columns:
            tr1_col = high[col] - low[col]
            tr2_col = (high[col] - close[col].shift(1)).abs()
            tr3_col = (low[col] - close[col].shift(1)).abs()
            tr_col = pd.concat([tr1_col, tr2_col, tr3_col], axis=1).max(axis=1)
            atr[col] = tr_col.rolling(short_period).mean()

        # 相对波动率(ATR / 价格)
        relative_volatility = atr / close
    else:
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(short_period).mean()
        relative_volatility = atr / close

    # 7. 波动率衰减权重(高波动时降权)
    volatility_weight = 1.0 / (1.0 + relative_volatility)

    # 8. 综合信号
    combined_signal = volume_confirmed * trend_direction * volatility_weight

    # 9. 截面排名标准化
    factor = combined_signal.rank(axis=1, pct=True)

    return factor
