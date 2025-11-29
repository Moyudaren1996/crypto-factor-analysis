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


if __name__ == "__main__":
    # 测试结果保存
    print("请在完整流程中测试结果保存功能")
