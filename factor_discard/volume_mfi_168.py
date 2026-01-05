"""
Volume指标 - MFI (使用pandas_ta)

因子描述:
    使用pandas_ta库计算的MFI技术指标

参数:
    length: 168 (14小时)

输出:
    标准化因子值

数据依赖:
    - OHLCV数据

来源: rolling_backtest_5m_strategy_regression.py
创建日期: 2024-12-01
版本: v1.0
"""
import pandas as pd
import numpy as np
import pandas_ta as ta

def calculate(data):
    """
    计算MFI因子 (pandas_ta)

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    # 对每个币种分别计算因子
    results = {}

    for symbol in data['close'].columns:
        # 构建单个币种的DataFrame
        symbol_data = pd.DataFrame({
            'open': data['open'][symbol],
            'high': data['high'][symbol],
            'low': data['low'][symbol],
            'close': data['close'][symbol],
            'volume': data['volume'][symbol]
        })

        # 调用pandas_ta计算指标
        result = symbol_data.ta.mfi(length=168)

        # 处理返回结果
        if result is None:
            results[symbol] = pd.Series(np.nan, index=symbol_data.index)
            continue

        # 如果返回DataFrame，取第一列
        if isinstance(result, pd.DataFrame):
            result = result.iloc[:, 0]

        results[symbol] = result

    # 合并所有币种的结果
    factor_df = pd.DataFrame(results)

    return factor_df
