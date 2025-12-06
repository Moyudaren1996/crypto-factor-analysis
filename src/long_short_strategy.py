"""
多空策略模块
计算做多高因子组、做空低因子组的策略表现
"""

import pandas as pd
import numpy as np
import config


def calculate_long_short_strategy(group_returns_series: pd.DataFrame,
                                  ic_mean: float = None,
                                  n_groups: int = None) -> dict:
    """
    计算多空策略指标

    策略：根据IC符号自动调整多空方向
    - IC > 0: 做多高因子组（Group N），做空低因子组（Group 1）
    - IC < 0: 做多低因子组（Group 1），做空高因子组（Group N）

    Args:
        group_returns_series: 各组收益率时间序列 (index=datetime, columns=group_ids)
        ic_mean: IC均值，用于判断多空方向。如果为None，则根据组间收益差自动判断
        n_groups: 分组数量，默认使用config中的配置

    Returns:
        strategy_metrics: 字典包含
            - long_short_return: 多空组合平均收益率（调整后，始终为正向策略收益）
            - sharpe_ratio: 年化Sharpe Ratio
            - max_drawdown: 最大回撤
            - cumulative_return: 累积收益率
    """
    if n_groups is None:
        n_groups = config.N_GROUPS

    # 判断多空方向
    # 方法1：如果提供了IC值，根据IC符号判断
    # 方法2：如果未提供IC，根据组间平均收益判断
    if ic_mean is not None:
        should_reverse = ic_mean < 0
    else:
        # 如果高因子组平均收益 < 低因子组，说明需要反转
        should_reverse = group_returns_series[n_groups].mean() < group_returns_series[1].mean()

    if should_reverse:
        print(f"\n计算多空策略 (IC<0, 做多Group1, 做空Group{n_groups})...")
        # IC为负：做多低因子组，做空高因子组
        long_short_returns = group_returns_series[1] - group_returns_series[n_groups]
    else:
        print(f"\n计算多空策略 (IC>0, 做多Group{n_groups}, 做空Group1)...")
        # IC为正：做多高因子组，做空低因子组
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
    #
    # 重要提示：此Sharpe Ratio是理论最大值（Backtest Overfitting）
    # 问题：
    # 1. 假设每5分钟重新分组并交易，一年交易105,120次（不现实）
    # 2. 未考虑交易成本（双边0.1-0.2%手续费 + 滑点）
    # 3. 未考虑信号延迟和执行延迟
    # 4. 样本内过拟合（在同一数据集上计算因子和回测）
    #
    # 实际可实现的Sharpe约为此值的 10-30%
    #
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
