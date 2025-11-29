"""
批量运行所有因子分析
"""
import os
import sys
import time

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_data
from src.return_calculator import calculate_forward_returns
from src.factor_calculator import calculate_factor
from src.ic_analyzer import calculate_ic_metrics
from src.group_analyzer import calculate_group_returns, plot_group_returns
from src.long_short_strategy import calculate_long_short_strategy
from src.result_saver import save_results
import config

def run_factor_analysis(factor_file):
    """运行单个因子分析"""
    try:
        # 1. 加载数据（只加载一次）
        # 2. 计算因子值
        factor_values, factor_name = calculate_factor(data, factor_file)

        # 3. 对齐因子值和收益率
        common_index = factor_values.index.intersection(forward_returns.index)
        factor_values_aligned = factor_values.loc[common_index]
        forward_returns_aligned = forward_returns.loc[common_index]

        # 4. IC分析
        ic_metrics = calculate_ic_metrics(factor_values_aligned, forward_returns_aligned)

        # 5. 分组分析
        group_results = calculate_group_returns(factor_values_aligned, forward_returns_aligned)

        # 绘制分组曲线图
        temp_plot_path = f'temp_group_returns_{factor_name}.png'
        plot_group_returns(group_results['group_cumulative_returns'], temp_plot_path)

        # 6. 多空策略分析
        strategy_metrics = calculate_long_short_strategy(group_results['group_returns_series'])

        # 7. 保存结果
        save_results(
            factor_name=factor_name,
            factor_values=factor_values,
            ic_metrics=ic_metrics,
            group_results=group_results,
            strategy_metrics=strategy_metrics,
            group_plot_path=temp_plot_path
        )

        return True, factor_name
    except Exception as e:
        return False, f"{factor_file}: {str(e)}"

if __name__ == "__main__":
    print("=" * 100)
    print("批量因子分析")
    print("=" * 100)

    # 加载数据（所有因子共用）
    print("\n加载数据...")
    data = load_data()
    forward_returns = calculate_forward_returns(data['close'])
    print("数据加载完成！")

    # 获取所有因子文件
    factor_dir = config.FACTOR_DIR
    factor_files = [f for f in os.listdir(factor_dir) if f.endswith('.py')]

    print(f"\n找到 {len(factor_files)} 个因子文件")
    print("=" * 100)

    # 批量运行
    success_count = 0
    failed_factors = []

    for i, factor_file in enumerate(factor_files, 1):
        print(f"\n[{i}/{len(factor_files)}] 正在分析: {factor_file}")
        print("-" * 100)

        start_time = time.time()
        success, result = run_factor_analysis(factor_file)
        elapsed = time.time() - start_time

        if success:
            success_count += 1
            print(f"✓ 完成: {result} (耗时: {elapsed:.1f}秒)")
        else:
            failed_factors.append(result)
            print(f"✗ 失败: {result}")

    # 汇总结果
    print("\n" + "=" * 100)
    print("批量分析完成！")
    print("=" * 100)
    print(f"成功: {success_count}/{len(factor_files)}")
    print(f"失败: {len(failed_factors)}/{len(factor_files)}")

    if failed_factors:
        print("\n失败的因子:")
        for factor in failed_factors:
            print(f"  - {factor}")

    print(f"\n结果保存在: {config.RESULT_DIR}/all_factors_metrics.csv")
