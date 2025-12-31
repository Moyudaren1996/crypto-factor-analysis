"""
Volatility指标 - Squeeze Ratio (波动率压缩比率)

因子描述:
    波动率压缩释放比率因子，衡量当前波动率相对于近期波动率的压缩程度，
    并结合价格动量方向识别突破机会。当波动率极度压缩且价格有明确方向时，
    预示着可能的趋势性突破。

    核心逻辑：
    1. 计算短期真实波幅(TR)与长期真实波幅的比率
    2. 将比率转换为历史百分位排名，识别极端压缩状态
    3. 结合价格方向（收益率符号）调整因子方向
    4. 低比率（压缩）+ 正动量 = 负因子值（预期反转下跌）
    5. 低比率（压缩）+ 负动量 = 正因子值（预期反转上涨）

参数:
    short_period: 12 (1小时) - 短期波动率窗口
    long_period: 48 (4小时) - 长期波动率窗口

计算公式:
    TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
    short_vol = TR.rolling(short_period).mean()
    long_vol = TR.rolling(long_period).mean()
    vol_ratio = short_vol / long_vol
    squeeze_percentile = vol_ratio.rolling(long_period).rank(pct=True)
    price_direction = sign(close - close.shift(short_period))
    factor = -squeeze_percentile * price_direction

输出:
    因子值DataFrame，负值预期下跌，正值预期上涨

数据依赖:
    - close: 收盘价 (必需)
    - high: 最高价 (必需)
    - low: 最低价 (必需)

创建日期: 2025-12-30
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算波动率压缩比率因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    high = data['high']
    low = data['low']

    # 定义参数
    short_period = 12  # 1小时
    long_period = 48   # 4小时

    # 计算真实波幅 True Range
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    true_range = pd.concat([tr1, tr2, tr3], axis=0).groupby(level=0).max()
    # 重新对齐到原始DataFrame结构
    true_range = tr1.copy()
    for col in true_range.columns:
        true_range[col] = np.maximum(np.maximum(tr1[col], tr2[col]), tr3[col])

    # 计算短期和长期波动率（TR的移动平均）
    short_vol = true_range.rolling(short_period).mean()
    long_vol = true_range.rolling(long_period).mean()

    # 计算波动率比率
    vol_ratio = short_vol / long_vol

    # 将比率转换为历史百分位排名（时序排名）
    squeeze_percentile = vol_ratio.rolling(long_period).rank(pct=True)

    # 计算价格方向（短期动量符号）
    price_direction = np.sign(close - close.shift(short_period))

    # 因子计算：压缩程度 * 价格方向的反向
    # 当波动率压缩（低百分位）且价格上涨时，预期反转下跌（负因子值）
    # 当波动率压缩（低百分位）且价格下跌时，预期反转上涨（正因子值）
    factor = -squeeze_percentile * price_direction

    return factor
