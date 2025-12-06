"""
单因子分析脚本 - 分析intermediate文件夹中的第一个因子

使用方法:
  python3 single_factor_analysis.py

功能:
  - 分析intermediate文件夹中的第一个因子文件
  - 计算两时段分析结果(Period 1样本内 + Period 2样本外)
  - 与results文件夹中的所有因子计算相关性
  - 输出结果保存在intermediate文件夹
  - 每次运行覆盖之前的结果
"""
import os
import sys
import pandas as pd
import numpy as np

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_data
from src.return_calculator import calculate_forward_returns
from src.factor_calculator import calculate_factor
from src.ic_analyzer import calculate_ic_metrics
from src.group_analyzer import calculate_group_returns, plot_group_returns
from src.long_short_strategy import calculate_long_short_strategy
import config


def find_top_correlated_factors(factor_values_p1, factor_values_p2, results_dir='results', top_n=5):
    """
    找出与当前因子相关性最高的已有因子

    Args:
        factor_values_p1: Period 1的因子值
        factor_values_p2: Period 2的因子值
        results_dir: results目录路径
        top_n: 返回前N个最相关的因子

    Returns:
        list: [(因子名称, 相关系数), ...]
    """
    print(f"\n计算与已有因子的相关性...")

    correlations = []

    # 遍历results目录下的所有因子文件夹
    if not os.path.exists(results_dir):
        print(f"  警告: results目录不存在，跳过相关性计算")
        return []

    factor_folders = [f for f in os.listdir(results_dir)
                     if os.path.isdir(os.path.join(results_dir, f))]

    if not factor_folders:
        print(f"  警告: results目录中没有因子文件夹，跳过相关性计算")
        return []

    print(f"  找到 {len(factor_folders)} 个已有因子")

    for factor_name in factor_folders:
        factor_dir = os.path.join(results_dir, factor_name)

        # 读取Period 1因子值
        p1_file = os.path.join(factor_dir, 'factor_values_period1.csv')
        p2_file = os.path.join(factor_dir, 'factor_values_period2.csv')

        if not os.path.exists(p1_file) or not os.path.exists(p2_file):
            continue

        try:
            # 读取已有因子值
            existing_p1 = pd.read_csv(p1_file, index_col=0, parse_dates=True)
            existing_p2 = pd.read_csv(p2_file, index_col=0, parse_dates=True)

            # 对齐索引
            common_index_p1 = factor_values_p1.index.intersection(existing_p1.index)
            common_index_p2 = factor_values_p2.index.intersection(existing_p2.index)

            if len(common_index_p1) == 0 or len(common_index_p2) == 0:
                continue

            # 展平为一维数组
            current_p1_flat = factor_values_p1.loc[common_index_p1].values.flatten()
            existing_p1_flat = existing_p1.loc[common_index_p1].values.flatten()

            current_p2_flat = factor_values_p2.loc[common_index_p2].values.flatten()
            existing_p2_flat = existing_p2.loc[common_index_p2].values.flatten()

            # 删除NaN值
            valid_mask_p1 = ~(np.isnan(current_p1_flat) | np.isnan(existing_p1_flat))
            valid_mask_p2 = ~(np.isnan(current_p2_flat) | np.isnan(existing_p2_flat))

            if valid_mask_p1.sum() < 10 or valid_mask_p2.sum() < 10:
                continue

            # 计算相关系数(两个时段的平均)
            corr_p1 = np.corrcoef(current_p1_flat[valid_mask_p1],
                                 existing_p1_flat[valid_mask_p1])[0, 1]
            corr_p2 = np.corrcoef(current_p2_flat[valid_mask_p2],
                                 existing_p2_flat[valid_mask_p2])[0, 1]

            avg_corr = (abs(corr_p1) + abs(corr_p2)) / 2

            correlations.append((factor_name, avg_corr, corr_p1, corr_p2))

        except Exception as e:
            print(f"  警告: 计算与 {factor_name} 的相关性时出错: {str(e)}")
            continue

    # 按平均相关系数排序
    correlations.sort(key=lambda x: x[1], reverse=True)

    # 返回前N个
    top_corr = correlations[:top_n]

    print(f"\n  相关性最高的 {len(top_corr)} 个因子:")
    for factor_name, avg_corr, corr_p1, corr_p2 in top_corr:
        print(f"    {factor_name}: 平均相关性={avg_corr:.4f} (P1={corr_p1:.4f}, P2={corr_p2:.4f})")

    return top_corr


def save_single_factor_results(factor_name, factor_values_p1, factor_values_p2,
                               ic_metrics_p1, ic_metrics_p2,
                               group_results_p1, group_results_p2,
                               strategy_metrics_p1, strategy_metrics_p2,
                               plot_p1_path, plot_p2_path,
                               top_correlated, output_dir='intermediate'):
    """
    保存单因子分析结果到intermediate文件夹

    Args:
        factor_name: 因子名称
        factor_values_p1, factor_values_p2: 因子值
        ic_metrics_p1, ic_metrics_p2: IC指标
        group_results_p1, group_results_p2: 分组结果
        strategy_metrics_p1, strategy_metrics_p2: 策略指标
        plot_p1_path, plot_p2_path: 图片路径
        top_correlated: 相关性最高的因子列表
        output_dir: 输出目录
    """
    print(f"\n保存单因子分析结果到 {output_dir} 文件夹...")

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 1. 保存Markdown结果文件
    md_path = os.path.join(output_dir, 'single_factor_result.md')

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# 单因子分析结果: {factor_name}\n\n")

        f.write("## Period 1 指标 (样本内: 2024-07-19 到 2024-10-18)\n\n")
        f.write(f"- **IC均值**: {ic_metrics_p1['ic_mean']:.6f}\n")
        f.write(f"- **Rank IC均值**: {ic_metrics_p1['rank_ic_mean']:.6f}\n")
        f.write(f"- **ICIR**: {ic_metrics_p1['icir']:.6f}\n")
        f.write(f"- **Group1平均收益**: {group_results_p1['group_mean_returns']['Group1']:.6e}\n")
        f.write(f"- **Group2平均收益**: {group_results_p1['group_mean_returns']['Group2']:.6e}\n")
        f.write(f"- **Group3平均收益**: {group_results_p1['group_mean_returns']['Group3']:.6e}\n")
        f.write(f"- **Group4平均收益**: {group_results_p1['group_mean_returns']['Group4']:.6e}\n")
        f.write(f"- **Group5平均收益**: {group_results_p1['group_mean_returns']['Group5']:.6e}\n")
        f.write(f"- **多空收益**: {strategy_metrics_p1['long_short_return']:.6e}\n")
        f.write(f"- **Sharpe Ratio**: {strategy_metrics_p1['sharpe_ratio']:.2f}\n")
        f.write(f"- **最大回撤**: {strategy_metrics_p1['max_drawdown']:.6f}\n")
        f.write(f"- **累积收益率**: {strategy_metrics_p1['cumulative_return']:.6f}\n\n")

        f.write("## Period 2 指标 (样本外: 2024-10-19 到 2025-01-18)\n\n")
        f.write(f"- **IC均值**: {ic_metrics_p2['ic_mean']:.6f}\n")
        f.write(f"- **Rank IC均值**: {ic_metrics_p2['rank_ic_mean']:.6f}\n")
        f.write(f"- **ICIR**: {ic_metrics_p2['icir']:.6f}\n")
        f.write(f"- **Group1平均收益**: {group_results_p2['group_mean_returns']['Group1']:.6e}\n")
        f.write(f"- **Group2平均收益**: {group_results_p2['group_mean_returns']['Group2']:.6e}\n")
        f.write(f"- **Group3平均收益**: {group_results_p2['group_mean_returns']['Group3']:.6e}\n")
        f.write(f"- **Group4平均收益**: {group_results_p2['group_mean_returns']['Group4']:.6e}\n")
        f.write(f"- **Group5平均收益**: {group_results_p2['group_mean_returns']['Group5']:.6e}\n")
        f.write(f"- **多空收益**: {strategy_metrics_p2['long_short_return']:.6e}\n")
        f.write(f"- **Sharpe Ratio**: {strategy_metrics_p2['sharpe_ratio']:.2f}\n")
        f.write(f"- **最大回撤**: {strategy_metrics_p2['max_drawdown']:.6f}\n")
        f.write(f"- **累积收益率**: {strategy_metrics_p2['cumulative_return']:.6f}\n\n")

        f.write("## IC衰减分析\n\n")
        ic_decay = ic_metrics_p2['ic_mean'] - ic_metrics_p1['ic_mean']
        f.write(f"- **IC衰减**: {ic_decay:.6f}\n")
        if ic_metrics_p1['ic_mean'] != 0:
            ic_decay_rate = ic_decay / abs(ic_metrics_p1['ic_mean']) * 100
            f.write(f"- **IC衰减率**: {ic_decay_rate:.2f}%\n\n")

        f.write("## 相关性最高的5个因子\n\n")
        if top_correlated:
            f.write("| 因子名称 | 平均相关性 | Period 1相关性 | Period 2相关性 |\n")
            f.write("|---------|-----------|---------------|---------------|\n")
            for factor_name, avg_corr, corr_p1, corr_p2 in top_correlated:
                f.write(f"| {factor_name} | {avg_corr:.4f} | {corr_p1:.4f} | {corr_p2:.4f} |\n")
        else:
            f.write("*未找到已有因子进行相关性比较*\n")

    print(f"  ✓ Markdown结果已保存: {md_path}")

    # 2. 保存因子值
    factor_p1_path = os.path.join(output_dir, 'single_factor_values_period1.csv')
    factor_values_p1.to_csv(factor_p1_path, encoding='utf-8-sig')
    print(f"  ✓ Period 1因子值已保存: {factor_p1_path}")

    factor_p2_path = os.path.join(output_dir, 'single_factor_values_period2.csv')
    factor_values_p2.to_csv(factor_p2_path, encoding='utf-8-sig')
    print(f"  ✓ Period 2因子值已保存: {factor_p2_path}")

    # 3. 复制图片
    import shutil

    if plot_p1_path and os.path.exists(plot_p1_path):
        plot_p1_save = os.path.join(output_dir, 'single_factor_group_returns_period1.png')
        shutil.copy(plot_p1_path, plot_p1_save)
        print(f"  ✓ Period 1分组曲线图已保存: {plot_p1_save}")
        os.remove(plot_p1_path)

    if plot_p2_path and os.path.exists(plot_p2_path):
        plot_p2_save = os.path.join(output_dir, 'single_factor_group_returns_period2.png')
        shutil.copy(plot_p2_path, plot_p2_save)
        print(f"  ✓ Period 2分组曲线图已保存: {plot_p2_save}")
        os.remove(plot_p2_path)

    print(f"\n所有结果已保存到 {output_dir} 文件夹!")


def main():
    """主函数"""

    print("=" * 100)
    print("单因子分析 - intermediate文件夹")
    print("=" * 100)

    # 检查intermediate文件夹
    intermediate_dir = 'intermediate'
    if not os.path.exists(intermediate_dir):
        print(f"❌ 错误: intermediate文件夹不存在")
        sys.exit(1)

    # 查找第一个因子文件
    factor_files = [f for f in os.listdir(intermediate_dir)
                   if f.endswith('.py') and not f.startswith('__')]

    if not factor_files:
        print(f"❌ 错误: intermediate文件夹中没有找到因子文件(.py)")
        sys.exit(1)

    factor_files.sort()
    factor_file = factor_files[0]
    factor_path = os.path.abspath(os.path.join(intermediate_dir, factor_file))

    print(f"分析因子: {factor_file}")
    print(f"因子路径: {factor_path}")
    print("=" * 100)

    # ========================================
    # 加载 Period 1 数据
    # ========================================
    print("\n【步骤 1/5】加载 Period 1 数据（样本内）...")
    print("-" * 100)

    original_start = config.START_DATE
    original_end = config.END_DATE
    config.START_DATE = config.PERIOD1_START
    config.END_DATE = config.PERIOD1_END

    data_p1 = load_data()
    forward_returns_p1 = calculate_forward_returns(data_p1['close'])

    print(f"✓ Period 1 数据加载完成！形状: {data_p1['close'].shape}")

    # ========================================
    # 加载 Period 2 数据
    # ========================================
    print("\n【步骤 2/5】加载 Period 2 数据（样本外）...")
    print("-" * 100)

    config.START_DATE = config.PERIOD2_START
    config.END_DATE = config.PERIOD2_END

    data_p2 = load_data()
    forward_returns_p2 = calculate_forward_returns(data_p2['close'])

    print(f"✓ Period 2 数据加载完成！形状: {data_p2['close'].shape}")

    # 恢复原始配置
    config.START_DATE = original_start
    config.END_DATE = original_end

    # ========================================
    # Period 1 分析
    # ========================================
    print("\n【步骤 3/5】Period 1 分析（样本内）...")
    print("-" * 100)

    # 计算因子值
    factor_values_p1, factor_name = calculate_factor(data_p1, factor_path)

    # 对齐
    common_index_p1 = factor_values_p1.index.intersection(forward_returns_p1.index)
    factor_values_p1_aligned = factor_values_p1.loc[common_index_p1]
    forward_returns_p1_aligned = forward_returns_p1.loc[common_index_p1]

    # IC分析
    ic_metrics_p1 = calculate_ic_metrics(factor_values_p1_aligned, forward_returns_p1_aligned)

    # 分组分析
    group_results_p1 = calculate_group_returns(factor_values_p1_aligned, forward_returns_p1_aligned)

    # 多空策略
    strategy_metrics_p1 = calculate_long_short_strategy(
        group_results_p1['group_returns_series'],
        ic_mean=ic_metrics_p1['ic_mean']
    )

    # 绘图
    import tempfile
    plot_p1_fd, plot_p1_path = tempfile.mkstemp(suffix='.png', prefix='single_p1_')
    os.close(plot_p1_fd)
    plot_group_returns(group_results_p1['group_cumulative_returns'], plot_p1_path)

    print(f"✓ Period 1 分析完成")

    # ========================================
    # Period 2 分析
    # ========================================
    print("\n【步骤 4/5】Period 2 分析（样本外）...")
    print("-" * 100)

    # 计算因子值
    factor_values_p2, _ = calculate_factor(data_p2, factor_path)

    # 对齐
    common_index_p2 = factor_values_p2.index.intersection(forward_returns_p2.index)
    factor_values_p2_aligned = factor_values_p2.loc[common_index_p2]
    forward_returns_p2_aligned = forward_returns_p2.loc[common_index_p2]

    # IC分析
    ic_metrics_p2 = calculate_ic_metrics(factor_values_p2_aligned, forward_returns_p2_aligned)

    # 分组分析
    group_results_p2 = calculate_group_returns(factor_values_p2_aligned, forward_returns_p2_aligned)

    # 多空策略
    strategy_metrics_p2 = calculate_long_short_strategy(
        group_results_p2['group_returns_series'],
        ic_mean=ic_metrics_p2['ic_mean']
    )

    # 绘图
    plot_p2_fd, plot_p2_path = tempfile.mkstemp(suffix='.png', prefix='single_p2_')
    os.close(plot_p2_fd)
    plot_group_returns(group_results_p2['group_cumulative_returns'], plot_p2_path)

    print(f"✓ Period 2 分析完成")

    # ========================================
    # 计算与已有因子的相关性
    # ========================================
    print("\n【步骤 5/5】计算与已有因子的相关性...")
    print("-" * 100)

    top_correlated = find_top_correlated_factors(
        factor_values_p1_aligned,
        factor_values_p2_aligned,
        results_dir='results',
        top_n=5
    )

    # ========================================
    # 保存结果
    # ========================================
    print("\n" + "=" * 100)
    save_single_factor_results(
        factor_name=factor_name,
        factor_values_p1=factor_values_p1_aligned,
        factor_values_p2=factor_values_p2_aligned,
        ic_metrics_p1=ic_metrics_p1,
        ic_metrics_p2=ic_metrics_p2,
        group_results_p1=group_results_p1,
        group_results_p2=group_results_p2,
        strategy_metrics_p1=strategy_metrics_p1,
        strategy_metrics_p2=strategy_metrics_p2,
        plot_p1_path=plot_p1_path,
        plot_p2_path=plot_p2_path,
        top_correlated=top_correlated,
        output_dir=intermediate_dir
    )

    print("=" * 100)
    print(f"分析完成! 结果保存在 {intermediate_dir} 文件夹")
    print("=" * 100)


if __name__ == "__main__":
    main()
