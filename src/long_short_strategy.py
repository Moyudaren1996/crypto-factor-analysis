"""
多空策略模块
计算做多高因子组、做空低因子组的策略表现
"""

import pandas as pd
import numpy as np
import config


def calculate_long_short_strategy(group_returns_series: pd.DataFrame,
                                  n_groups: int = None) -> dict:
    """
    计算多空策略指标

    策略：做多Group N（因子值最高），做空Group 1（因子值最低）

    Args:
        group_returns_series: 各组收益率时间序列 (index=datetime, columns=group_ids)
        n_groups: 分组数量，默认使用config中的配置

    Returns:
        strategy_metrics: 字典包含
            - long_short_return: 多空组合平均收益率
            - sharpe_ratio: 年化Sharpe Ratio
            - max_drawdown: 最大回撤
            - cumulative_return: 累积收益率
    """
    if n_groups is None:
        n_groups = config.N_GROUPS

    print(f"\n计算多空策略 (做多Group{n_groups}, 做空Group1)...")

    # 多空组合收益 = 高因子组收益 - 低因子组收益
    long_short_returns = group_returns_series[n_groups] - group_returns_series[1]

    # 删除缺失值
    long_short_returns = long_short_returns.dropna()

    if len(long_short_returns) == 0:
        print("警告: 无有效数据")
        return {
            'long_short_return': 0,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'cumulative_return': 1
        }

    # 计算平均收益率
    mean_return = long_short_returns.mean()

    # 计算年化Sharpe Ratio
    # Sharpe = (年化收益率 - 无风险利率) / 年化波动率
    # 假设无风险利率为0
    periods_per_year = config.PERIODS_PER_YEAR
    annualized_return = mean_return * periods_per_year
    annualized_volatility = long_short_returns.std() * np.sqrt(periods_per_year)

    sharpe_ratio = annualized_return / annualized_volatility if annualized_volatility > 0 else 0

    # 计算最大回撤
    cumulative_returns = (1 + long_short_returns).cumprod()
    running_max = cumulative_returns.expanding().max()
    drawdown = (cumulative_returns - running_max) / running_max
    max_drawdown = drawdown.min()

    # 累积收益率
    total_cumulative_return = cumulative_returns.iloc[-1]

    print(f"多空平均收益率: {mean_return:.6f}")
    print(f"Sharpe Ratio: {sharpe_ratio:.4f}")
    print(f"最大回撤: {max_drawdown:.4f}")
    print(f"累积收益率: {total_cumulative_return:.4f}")

    return {
        'long_short_return': mean_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'cumulative_return': total_cumulative_return,
        'long_short_series': long_short_returns,
        'cumulative_series': cumulative_returns
    }


if __name__ == "__main__":
    # 测试多空策略
    import sys
    sys.path.append('..')
    from src.data_loader import load_data
    from src.return_calculator import calculate_forward_returns
    from src.group_analyzer import calculate_group_returns

    data = load_data()
    returns = calculate_forward_returns(data['close'])
    factor = data['close'].pct_change(10).loc[returns.index]

    group_results = calculate_group_returns(factor, returns)
    strategy_metrics = calculate_long_short_strategy(group_results['group_returns_series'])

    print("\n策略指标:")
    for key, value in strategy_metrics.items():
        if key not in ['long_short_series', 'cumulative_series']:
            print(f"{key}: {value}")
