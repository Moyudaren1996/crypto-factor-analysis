"""
主程序 - 因子分析流程
"""

import os
import sys
import argparse

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


def run_factor_analysis(factor_file: str):
    """
    运行完整的因子分析流程

    Args:
        factor_file: 因子文件路径
    """
    print("=" * 80)
    print("加密货币因子分析系统")
    print("=" * 80)

    # 1. 加载数据
    print("\n【步骤 1/7】加载数据")
    print("-" * 80)
    data = load_data()

    # 2. 计算因子值
    print("\n【步骤 2/7】计算因子值")
    print("-" * 80)
    factor_values, factor_name = calculate_factor(data, factor_file)

    # 3. 计算未来收益
    print("\n【步骤 3/7】计算未来收益")
    print("-" * 80)
    forward_returns = calculate_forward_returns(data['close'])

    # 对齐因子值和收益率（因为计算收益会损失最后几行）
    common_index = factor_values.index.intersection(forward_returns.index)
    factor_values = factor_values.loc[common_index]
    forward_returns = forward_returns.loc[common_index]

    # 4. IC分析
    print("\n【步骤 4/7】IC分析")
    print("-" * 80)
    ic_metrics = calculate_ic_metrics(factor_values, forward_returns)

    # 5. 分组分析
    print("\n【步骤 5/7】分组分析")
    print("-" * 80)
    group_results = calculate_group_returns(factor_values, forward_returns)

    # 绘制分组曲线图（临时文件）
    temp_plot_path = 'temp_group_returns.png'
    plot_group_returns(group_results['group_cumulative_returns'], temp_plot_path)

    # 6. 多空策略分析
    print("\n【步骤 6/7】多空策略分析")
    print("-" * 80)
    strategy_metrics = calculate_long_short_strategy(group_results['group_returns_series'])

    # 7. 保存结果
    print("\n【步骤 7/7】保存结果")
    print("-" * 80)
    save_results(
        factor_name=factor_name,
        factor_values=factor_values,
        ic_metrics=ic_metrics,
        group_results=group_results,
        strategy_metrics=strategy_metrics,
        group_plot_path=temp_plot_path
    )

    # 打印最终报告
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)
    print(f"\n因子名称: {factor_name}")
    print(f"\n【IC指标】")
    print(f"  IC均值:        {ic_metrics['ic_mean']:.6f}")
    print(f"  Rank IC均值:   {ic_metrics['rank_ic_mean']:.6f}")
    print(f"  ICIR:          {ic_metrics['icir']:.6f}")

    print(f"\n【分组收益】")
    for group_name, group_return in group_results['group_mean_returns'].items():
        print(f"  {group_name}:        {group_return:.6f}")

    print(f"\n【多空策略】")
    print(f"  多空收益:      {strategy_metrics['long_short_return']:.6f}")
    print(f"  Sharpe Ratio:  {strategy_metrics['sharpe_ratio']:.6f}")
    print(f"  最大回撤:      {strategy_metrics['max_drawdown']:.6f}")
    print(f"  累积收益率:    {strategy_metrics['cumulative_return']:.6f}")

    print(f"\n结果保存位置: {os.path.join(config.RESULT_DIR, factor_name)}")
    print("=" * 80)


def list_factors():
    """列出所有可用的因子文件"""
    if not os.path.exists(config.FACTOR_DIR):
        print(f"因子目录不存在: {config.FACTOR_DIR}")
        return

    factor_files = [f for f in os.listdir(config.FACTOR_DIR) if f.endswith('.py')]

    if not factor_files:
        print(f"在 {config.FACTOR_DIR} 目录下未找到因子文件")
        return

    print(f"\n可用因子文件 ({len(factor_files)}):")
    for i, factor_file in enumerate(factor_files, 1):
        print(f"  {i}. {factor_file}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='加密货币因子分析系统')
    parser.add_argument('--factor', '-f', type=str, help='因子文件名（如 momentum.py）')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有可用因子')

    args = parser.parse_args()

    if args.list:
        list_factors()
        return

    if args.factor:
        factor_file = args.factor
    else:
        # 交互式选择因子
        list_factors()
        factor_file = input("\n请输入因子文件名: ").strip()

    if not factor_file:
        print("错误: 未指定因子文件")
        return

    try:
        run_factor_analysis(factor_file)
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
