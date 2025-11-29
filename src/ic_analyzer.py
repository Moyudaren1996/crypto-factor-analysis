"""
IC分析模块
计算IC (Information Coefficient) 相关指标
"""

import pandas as pd
import numpy as np
from scipy import stats


def calculate_ic_metrics(factor_values: pd.DataFrame,
                        forward_returns: pd.DataFrame) -> dict:
    """
    计算IC指标

    Args:
        factor_values: 因子值 (index=datetime, columns=symbols)
        forward_returns: 未来收益率 (index=datetime, columns=symbols)

    Returns:
        ic_metrics: 字典包含以下指标
            - ic_mean: IC均值
            - rank_ic_mean: Rank IC均值
            - icir: ICIR (IC Information Ratio)
            - ic_series: IC时间序列
            - rank_ic_series: Rank IC时间序列
    """
    print("\n计算IC指标...")

    # 对齐因子值和收益率的时间索引
    common_index = factor_values.index.intersection(forward_returns.index)
    factor_values = factor_values.loc[common_index]
    forward_returns = forward_returns.loc[common_index]

    # 存储每个时间点的IC
    ic_list = []
    rank_ic_list = []

    # 遍历每个时间截面，计算IC
    for timestamp in common_index:
        # 获取该时间点所有币种的因子值和收益率
        factor_t = factor_values.loc[timestamp]
        return_t = forward_returns.loc[timestamp]

        # 删除缺失值
        valid_mask = factor_t.notna() & return_t.notna()
        factor_t = factor_t[valid_mask]
        return_t = return_t[valid_mask]

        # 至少需要3个有效样本才能计算相关系数
        if len(factor_t) < 3:
            ic_list.append(np.nan)
            rank_ic_list.append(np.nan)
            continue

        # 计算Pearson相关系数 (IC)
        ic, _ = stats.pearsonr(factor_t, return_t)
        ic_list.append(ic)

        # 计算Spearman相关系数 (Rank IC)
        rank_ic, _ = stats.spearmanr(factor_t, return_t)
        rank_ic_list.append(rank_ic)

    # 转换为Series
    ic_series = pd.Series(ic_list, index=common_index)
    rank_ic_series = pd.Series(rank_ic_list, index=common_index)

    # 计算IC统计指标
    ic_mean = ic_series.mean()
    ic_std = ic_series.std()
    rank_ic_mean = rank_ic_series.mean()

    # 计算ICIR (IC Information Ratio)
    # ICIR = IC均值 / IC标准差
    icir = ic_mean / ic_std if ic_std > 0 else 0

    print(f"IC均值: {ic_mean:.4f}")
    print(f"Rank IC均值: {rank_ic_mean:.4f}")
    print(f"ICIR: {icir:.4f}")
    print(f"有效时间点: {ic_series.notna().sum()} / {len(ic_series)}")

    return {
        'ic_mean': ic_mean,
        'rank_ic_mean': rank_ic_mean,
        'icir': icir,
        'ic_series': ic_series,
        'rank_ic_series': rank_ic_series
    }


if __name__ == "__main__":
    # 测试IC计算
    import sys
    sys.path.append('..')
    from src.data_loader import load_data
    from src.return_calculator import calculate_forward_returns

    # 创建模拟因子数据
    data = load_data()
    returns = calculate_forward_returns(data['close'])

    # 使用收益率的滞后值作为模拟因子
    factor = data['close'].pct_change(10).loc[returns.index]

    ic_metrics = calculate_ic_metrics(factor, returns)
    print("\nIC指标:")
    for key, value in ic_metrics.items():
        if key not in ['ic_series', 'rank_ic_series']:
            print(f"{key}: {value}")
