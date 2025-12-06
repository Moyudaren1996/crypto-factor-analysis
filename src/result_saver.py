"""
结果保存模块
保存因子分析结果到文件
"""

import pandas as pd
import os
import shutil
import config


def save_results(factor_name: str,
                factor_values: pd.DataFrame,
                ic_metrics: dict,
                group_results: dict,
                strategy_metrics: dict,
                group_plot_path: str = None) -> None:
    """
    保存因子分析结果

    Args:
        factor_name: 因子名称
        factor_values: 因子值DataFrame
        ic_metrics: IC指标字典
        group_results: 分组分析结果字典
        strategy_metrics: 策略指标字典
        group_plot_path: 分组曲线图路径（临时文件）
    """
    print(f"\n保存因子分析结果: {factor_name}")

    # 确保results目录存在
    os.makedirs(config.RESULT_DIR, exist_ok=True)

    # 1. 更新统一的指标汇总文件 all_factors_metrics.csv
    all_metrics_path = os.path.join(config.RESULT_DIR, 'all_factors_metrics.csv')

    # 构建当前因子的指标行
    current_metrics = {
        '因子名称': factor_name,
        'IC均值': ic_metrics['ic_mean'],
        'Rank IC均值': ic_metrics['rank_ic_mean'],
        'ICIR': ic_metrics['icir'],
    }

    # 添加各组平均收益率
    for group_name, group_return in group_results['group_mean_returns'].items():
        current_metrics[f'{group_name}平均收益'] = group_return

    # 添加策略指标
    current_metrics['多空收益'] = strategy_metrics['long_short_return']
    current_metrics['Sharpe Ratio'] = strategy_metrics['sharpe_ratio']
    current_metrics['最大回撤'] = strategy_metrics['max_drawdown']
    current_metrics['累积收益率'] = strategy_metrics['cumulative_return']

    # 读取现有的汇总文件（如果存在）
    if os.path.exists(all_metrics_path):
        all_metrics_df = pd.read_csv(all_metrics_path, encoding='utf-8-sig')

        # 检查是否已有同名因子，如果有则删除旧记录
        if factor_name in all_metrics_df['因子名称'].values:
            print(f"  检测到同名因子，覆盖旧记录...")
            all_metrics_df = all_metrics_df[all_metrics_df['因子名称'] != factor_name]

        # 追加新记录
        new_row_df = pd.DataFrame([current_metrics])
        all_metrics_df = pd.concat([all_metrics_df, new_row_df], ignore_index=True)
    else:
        # 创建新的DataFrame
        all_metrics_df = pd.DataFrame([current_metrics])

    # 保存到CSV
    all_metrics_df.to_csv(all_metrics_path, index=False, encoding='utf-8-sig')
    print(f"  指标汇总已更新: {all_metrics_path}")

    # 2. 创建因子专属文件夹
    factor_dir = os.path.join(config.RESULT_DIR, factor_name)

    # 如果文件夹已存在，删除并重建（覆盖旧结果）
    if os.path.exists(factor_dir):
        shutil.rmtree(factor_dir)

    os.makedirs(factor_dir, exist_ok=True)

    # 3. 保存因子值
    factor_values_path = os.path.join(factor_dir, 'factor_values.csv')
    factor_values.to_csv(factor_values_path, encoding='utf-8-sig')
    print(f"  因子值已保存: {factor_values_path}")

    # 4. 复制分组曲线图
    if group_plot_path and os.path.exists(group_plot_path):
        plot_save_path = os.path.join(factor_dir, 'group_returns.png')
        shutil.copy(group_plot_path, plot_save_path)
        print(f"  分组曲线图已保存: {plot_save_path}")

        # 删除临时文件
        if os.path.exists(group_plot_path):
            os.remove(group_plot_path)

    print(f"\n所有结果已保存!")
    print(f"  - 因子数据: {factor_dir}")
    print(f"  - 指标汇总: {all_metrics_path}")


def save_results_two_periods(factor_name: str,
                            factor_values_p1: pd.DataFrame,
                            factor_values_p2: pd.DataFrame,
                            ic_metrics_p1: dict,
                            ic_metrics_p2: dict,
                            group_results_p1: dict,
                            group_results_p2: dict,
                            strategy_metrics_p1: dict,
                            strategy_metrics_p2: dict,
                            plot_p1_path: str = None,
                            plot_p2_path: str = None) -> None:
    """
    保存两个时段的因子分析结果

    Args:
        factor_name: 因子名称
        factor_values_p1: Period 1的因子值
        factor_values_p2: Period 2的因子值
        ic_metrics_p1: Period 1的IC指标
        ic_metrics_p2: Period 2的IC指标
        group_results_p1: Period 1的分组结果
        group_results_p2: Period 2的分组结果
        strategy_metrics_p1: Period 1的策略指标
        strategy_metrics_p2: Period 2的策略指标
        plot_p1_path: Period 1的分组曲线图路径（临时文件）
        plot_p2_path: Period 2的分组曲线图路径（临时文件）
    """
    print(f"\n保存两时段分析结果: {factor_name}")

    # 确保results目录存在
    os.makedirs(config.RESULT_DIR, exist_ok=True)

    # 更新统一的指标汇总文件
    all_metrics_path = os.path.join(config.RESULT_DIR, 'all_factors_metrics.csv')

    # 构建当前因子的指标行（包含两个时段）
    current_metrics = {
        '因子名称': factor_name,

        # Period 1 指标
        'IC均值_P1': ic_metrics_p1['ic_mean'],
        'Rank_IC均值_P1': ic_metrics_p1['rank_ic_mean'],
        'ICIR_P1': ic_metrics_p1['icir'],
        'Group1平均收益_P1': group_results_p1['group_mean_returns']['Group1'],
        'Group2平均收益_P1': group_results_p1['group_mean_returns']['Group2'],
        'Group3平均收益_P1': group_results_p1['group_mean_returns']['Group3'],
        'Group4平均收益_P1': group_results_p1['group_mean_returns']['Group4'],
        'Group5平均收益_P1': group_results_p1['group_mean_returns']['Group5'],
        '多空收益_P1': strategy_metrics_p1['long_short_return'],
        'Sharpe_Ratio_P1': strategy_metrics_p1['sharpe_ratio'],
        '最大回撤_P1': strategy_metrics_p1['max_drawdown'],
        '累积收益率_P1': strategy_metrics_p1['cumulative_return'],

        # Period 2 指标
        'IC均值_P2': ic_metrics_p2['ic_mean'],
        'Rank_IC均值_P2': ic_metrics_p2['rank_ic_mean'],
        'ICIR_P2': ic_metrics_p2['icir'],
        'Group1平均收益_P2': group_results_p2['group_mean_returns']['Group1'],
        'Group2平均收益_P2': group_results_p2['group_mean_returns']['Group2'],
        'Group3平均收益_P2': group_results_p2['group_mean_returns']['Group3'],
        'Group4平均收益_P2': group_results_p2['group_mean_returns']['Group4'],
        'Group5平均收益_P2': group_results_p2['group_mean_returns']['Group5'],
        '多空收益_P2': strategy_metrics_p2['long_short_return'],
        'Sharpe_Ratio_P2': strategy_metrics_p2['sharpe_ratio'],
        '最大回撤_P2': strategy_metrics_p2['max_drawdown'],
        '累积收益率_P2': strategy_metrics_p2['cumulative_return'],
    }

    # 读取现有的汇总文件（如果存在）
    if os.path.exists(all_metrics_path):
        all_metrics_df = pd.read_csv(all_metrics_path, encoding='utf-8-sig')

        # 检查是否是旧格式数据（只有IC均值列，没有IC均值_P1列）
        # 如果是旧格式或混合格式，只保留新格式的数据
        if 'IC均值' in all_metrics_df.columns and 'IC均值_P1' not in all_metrics_df.columns:
            print(f"  检测到旧格式数据，清空并使用新格式...")
            all_metrics_df = pd.DataFrame([current_metrics])
        elif 'IC均值' in all_metrics_df.columns and 'IC均值_P1' in all_metrics_df.columns:
            # 混合格式：删除所有旧格式的行（IC均值有值但IC均值_P1为空）
            print(f"  检测到混合格式数据，清理旧格式行...")
            all_metrics_df = all_metrics_df[all_metrics_df['IC均值_P1'].notna()]

            # 检查是否已有同名因子，如果有则删除旧记录
            if factor_name in all_metrics_df['因子名称'].values:
                print(f"  检测到同名因子，覆盖旧记录...")
                all_metrics_df = all_metrics_df[all_metrics_df['因子名称'] != factor_name]

            # 追加新记录
            new_row_df = pd.DataFrame([current_metrics])
            all_metrics_df = pd.concat([all_metrics_df, new_row_df], ignore_index=True)
        else:
            # 纯新格式：检查同名并追加
            if factor_name in all_metrics_df['因子名称'].values:
                print(f"  检测到同名因子，覆盖旧记录...")
                all_metrics_df = all_metrics_df[all_metrics_df['因子名称'] != factor_name]

            new_row_df = pd.DataFrame([current_metrics])
            all_metrics_df = pd.concat([all_metrics_df, new_row_df], ignore_index=True)
    else:
        # 创建新的DataFrame
        all_metrics_df = pd.DataFrame([current_metrics])

    # 保存到CSV
    all_metrics_df.to_csv(all_metrics_path, index=False, encoding='utf-8-sig')
    print(f"  指标汇总已更新: {all_metrics_path}")
    print(f"  Period 1 IC: {ic_metrics_p1['ic_mean']:.6f}")
    print(f"  Period 2 IC: {ic_metrics_p2['ic_mean']:.6f}")
    print(f"  IC衰减: {(ic_metrics_p2['ic_mean'] - ic_metrics_p1['ic_mean']):.6f}")

    # 创建因子专属文件夹并保存图片
    factor_dir = os.path.join(config.RESULT_DIR, factor_name)

    # 如果文件夹已存在，删除并重建（覆盖旧结果）
    if os.path.exists(factor_dir):
        shutil.rmtree(factor_dir)

    os.makedirs(factor_dir, exist_ok=True)

    # 复制 Period 1 的分组曲线图
    if plot_p1_path and os.path.exists(plot_p1_path):
        plot_p1_save_path = os.path.join(factor_dir, 'group_returns_period1.png')
        shutil.copy(plot_p1_path, plot_p1_save_path)
        print(f"  Period 1 分组曲线图已保存: {plot_p1_save_path}")

        # 删除临时文件
        if os.path.exists(plot_p1_path):
            os.remove(plot_p1_path)

    # 复制 Period 2 的分组曲线图
    if plot_p2_path and os.path.exists(plot_p2_path):
        plot_p2_save_path = os.path.join(factor_dir, 'group_returns_period2.png')
        shutil.copy(plot_p2_path, plot_p2_save_path)
        print(f"  Period 2 分组曲线图已保存: {plot_p2_save_path}")

        # 删除临时文件
        if os.path.exists(plot_p2_path):
            os.remove(plot_p2_path)

    # 保存 Period 1 的因子值
    factor_values_p1_path = os.path.join(factor_dir, 'factor_values_period1.csv')
    factor_values_p1.to_csv(factor_values_p1_path, encoding='utf-8-sig')
    print(f"  Period 1 因子值已保存: {factor_values_p1_path}")

    # 保存 Period 2 的因子值
    factor_values_p2_path = os.path.join(factor_dir, 'factor_values_period2.csv')
    factor_values_p2.to_csv(factor_values_p2_path, encoding='utf-8-sig')
    print(f"  Period 2 因子值已保存: {factor_values_p2_path}")

    print(f"\n所有结果已保存!")
    print(f"  - 因子文件夹: {factor_dir}")
    print(f"  - 指标汇总: {all_metrics_path}")


if __name__ == "__main__":
    # 测试结果保存
    print("请在完整流程中测试结果保存功能")
