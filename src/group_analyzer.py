"""
分组分析模块
按因子值分组并计算各组收益
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import config


def calculate_group_returns(factor_values: pd.DataFrame,
                           forward_returns: pd.DataFrame,
                           n_groups: int = None) -> dict:
    """
    按因子值分组并计算收益

    Args:
        factor_values: 因子值 (index=datetime, columns=symbols)
        forward_returns: 未来收益率 (index=datetime, columns=symbols)
        n_groups: 分组数量，默认使用config中的配置

    Returns:
        group_results: 字典包含
            - group_mean_returns: 各组平均收益率 (dict)
            - group_cumulative_returns: 各组累积收益曲线 (DataFrame)
    """
    if n_groups is None:
        n_groups = config.N_GROUPS

    print(f"\n按因子值分成 {n_groups} 组...")

    # 对齐因子值和收益率
    common_index = factor_values.index.intersection(forward_returns.index)
    factor_values = factor_values.loc[common_index]
    forward_returns = forward_returns.loc[common_index]

    # 存储每组的收益率时间序列
    group_returns_dict = {i: [] for i in range(1, n_groups + 1)}

    # 遍历每个时间点
    for timestamp in common_index:
        factor_t = factor_values.loc[timestamp]
        return_t = forward_returns.loc[timestamp]

        # 删除缺失值
        valid_mask = factor_t.notna() & return_t.notna()
        factor_t = factor_t[valid_mask]
        return_t = return_t[valid_mask]

        if len(factor_t) < n_groups:
            # 如果样本数少于分组数，所有组都记录NaN
            for i in range(1, n_groups + 1):
                group_returns_dict[i].append(np.nan)
            continue

        # 按因子值分组（使用quantile）
        # Group 1: 因子值最低, Group N: 因子值最高
        factor_t_series = pd.Series(factor_t.values, index=factor_t.index)
        labels = pd.qcut(factor_t_series.rank(method='first'),
                        q=n_groups,
                        labels=range(1, n_groups + 1),
                        duplicates='drop')

        # 计算每组的平均收益率
        for group_id in range(1, n_groups + 1):
            group_symbols = labels[labels == group_id].index
            if len(group_symbols) > 0:
                group_return = return_t[group_symbols].mean()
                group_returns_dict[group_id].append(group_return)
            else:
                group_returns_dict[group_id].append(np.nan)

    # 转换为DataFrame
    group_returns_df = pd.DataFrame(group_returns_dict, index=common_index)

    # 计算各组平均收益率
    group_mean_returns = {}
    for group_id in range(1, n_groups + 1):
        mean_return = group_returns_df[group_id].mean()
        group_mean_returns[f'Group{group_id}'] = mean_return
        print(f"Group {group_id} 平均收益率: {mean_return:.6f}")

    # 计算累积收益曲线
    group_cumulative_returns = (1 + group_returns_df).cumprod()

    return {
        'group_mean_returns': group_mean_returns,
        'group_returns_series': group_returns_df,
        'group_cumulative_returns': group_cumulative_returns
    }


def plot_group_returns(group_cumulative_returns: pd.DataFrame,
                      save_path: str = None) -> None:
    """
    绘制分组累积收益曲线

    Args:
        group_cumulative_returns: 各组累积收益 (index=datetime, columns=group_ids)
        save_path: 图片保存路径，如果为None则不保存
    """
    print("\n绘制分组收益曲线...")

    plt.figure(figsize=(12, 6))

    # 绘制每组的曲线
    for col in group_cumulative_returns.columns:
        plt.plot(group_cumulative_returns.index,
                group_cumulative_returns[col],
                label=f'Group {col}',
                linewidth=2)

    plt.xlabel('Time', fontsize=12)
    plt.ylabel('Cumulative Return', fontsize=12)
    plt.title('Group Cumulative Returns', fontsize=14, fontweight='bold')
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"图片已保存至: {save_path}")

    plt.close()


if __name__ == "__main__":
    # 测试分组分析
    import sys
    sys.path.append('..')
    from src.data_loader import load_data
    from src.return_calculator import calculate_forward_returns

    data = load_data()
    returns = calculate_forward_returns(data['close'])
    factor = data['close'].pct_change(10).loc[returns.index]

    group_results = calculate_group_returns(factor, returns)
    print("\n各组平均收益率:")
    for group, ret in group_results['group_mean_returns'].items():
        print(f"{group}: {ret:.6f}")

    plot_group_returns(group_results['group_cumulative_returns'], 'test_group_returns.png')
