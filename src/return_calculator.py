"""
收益计算模块
计算未来N期的收益率
"""

import pandas as pd
import config


def calculate_forward_returns(close_prices: pd.DataFrame,
                              periods: int = None) -> pd.DataFrame:
    """
    计算未来N期收益率

    Args:
        close_prices: 收盘价DataFrame (index=datetime, columns=symbols)
        periods: 前向周期数，默认使用config中的配置

    Returns:
        forward_returns: 未来N期收益率 (index=datetime, columns=symbols)
                        公式: (close_t+N - close_t) / close_t
    """
    if periods is None:
        periods = config.FORWARD_PERIODS

    print(f"计算未来 {periods} 期收益率...")

    # 计算前向收益率
    # shift(-periods) 将未来的价格移到当前行
    forward_returns = (close_prices.shift(-periods) - close_prices) / close_prices

    # 删除最后N行（没有未来收益的行）
    forward_returns = forward_returns.iloc[:-periods]

    print(f"收益率计算完成，形状: {forward_returns.shape}")

    return forward_returns


if __name__ == "__main__":
    # 测试收益计算
    import sys
    sys.path.append('..')
    from src.data_loader import load_data

    data = load_data()
    returns = calculate_forward_returns(data['close'])

    print("\n收益率预览:")
    print(returns.head())
    print("\n收益率统计:")
    print(returns.describe())
