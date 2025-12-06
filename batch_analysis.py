"""
批量运行因子分析 - 支持样本外验证

使用方法:
  1. 分析factors目录下的所有因子:
     python batch_analysis.py

  2. 分析factors_ta目录下的所有因子:
     修改 config.py 中的 FACTOR_DIR = 'factors_ta'
     然后运行: python batch_analysis.py

  3. 分析单个因子:
     修改下方 factor_files 列表，只保留需要的因子文件名

  4. 分析前N个因子:
     修改下方 factor_files = factor_files[:N]

功能说明:
  - 自动分析两个时段（Period 1和Period 2）
  - Period 1: 样本内（2024-07-19 到 2024-10-18）
  - Period 2: 样本外（2024-10-19 到 2025-01-18）
  - 结果保存在 results/all_factors_metrics.csv
  - CSV包含两个时段的所有指标（列名带_P1和_P2后缀）


### 1. 分析factors目录下的所有因子

```bash
python3 batch_analysis.py
```

### 2. 分析factors_ta目录下的所有因子

**方法1：修改config.py**
```python
# 编辑 config.py
FACTOR_DIR = 'factors_ta'  # 改为 factors_ta
```
然后运行：
```bash
python3 batch_analysis.py
```

**方法2：使用命令行参数**
```bash
python3 batch_analysis.py --dir factors_ta
```

### 3. 分析前N个因子

```bash
# 分析前10个因子
python3 batch_analysis.py --limit 10

# 分析factors_ta目录的前20个因子
python3 batch_analysis.py --dir factors_ta --limit 20
```

### 4. 分析单个因子

```bash
# 分析momentum_mom_3.py因子
python3 batch_analysis.py --factor momentum_mom_3.py

# 分析factors_ta目录下的rsi_14.py
python3 batch_analysis.py --dir factors_ta --factor rsi_14.py

"""
import os
import sys
import time
import argparse

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import load_data
from src.return_calculator import calculate_forward_returns
from src.factor_calculator import calculate_factor
from src.ic_analyzer import calculate_ic_metrics
from src.group_analyzer import calculate_group_returns, plot_group_returns
from src.long_short_strategy import calculate_long_short_strategy
from src.result_saver import save_results_two_periods
import config


def run_factor_analysis_two_periods(factor_file, data_p1, data_p2, forward_returns_p1, forward_returns_p2, factor_dir):
    """
    运行单个因子的两时段分析

    Args:
        factor_file: 因子文件名
        data_p1: Period 1的OHLCV数据
        data_p2: Period 2的OHLCV数据
        forward_returns_p1: Period 1的未来收益率
        forward_returns_p2: Period 2的未来收益率
        factor_dir: 因子目录路径

    Returns:
        (success, result): 成功标志和结果信息
    """
    try:
        # 构建完整路径
        full_path = os.path.abspath(os.path.join(factor_dir, factor_file))

        # ========================================
        # Period 1 分析（样本内）
        # ========================================
        print("\n  [Period 1] 样本内分析...")

        # 1. 计算因子值
        factor_values_p1, factor_name = calculate_factor(data_p1, full_path)

        # 2. 对齐因子值和收益率
        common_index_p1 = factor_values_p1.index.intersection(forward_returns_p1.index)
        factor_values_p1_aligned = factor_values_p1.loc[common_index_p1]
        forward_returns_p1_aligned = forward_returns_p1.loc[common_index_p1]

        # 3. IC分析
        ic_metrics_p1 = calculate_ic_metrics(factor_values_p1_aligned, forward_returns_p1_aligned)

        # 4. 分组分析
        group_results_p1 = calculate_group_returns(factor_values_p1_aligned, forward_returns_p1_aligned)

        # 5. 多空策略分析
        strategy_metrics_p1 = calculate_long_short_strategy(
            group_results_p1['group_returns_series'],
            ic_mean=ic_metrics_p1['ic_mean']
        )

        # 6. 绘制分组曲线图（Period 1）
        import tempfile
        plot_p1_fd, plot_p1_path = tempfile.mkstemp(suffix='.png', prefix='group_returns_p1_')
        os.close(plot_p1_fd)
        plot_group_returns(group_results_p1['group_cumulative_returns'], plot_p1_path)

        # ========================================
        # Period 2 分析（样本外）
        # ========================================
        print("\n  [Period 2] 样本外分析...")

        # 1. 计算因子值
        factor_values_p2, _ = calculate_factor(data_p2, full_path)

        # 2. 对齐因子值和收益率
        common_index_p2 = factor_values_p2.index.intersection(forward_returns_p2.index)
        factor_values_p2_aligned = factor_values_p2.loc[common_index_p2]
        forward_returns_p2_aligned = forward_returns_p2.loc[common_index_p2]

        # 3. IC分析
        ic_metrics_p2 = calculate_ic_metrics(factor_values_p2_aligned, forward_returns_p2_aligned)

        # 4. 分组分析
        group_results_p2 = calculate_group_returns(factor_values_p2_aligned, forward_returns_p2_aligned)

        # 5. 多空策略分析
        strategy_metrics_p2 = calculate_long_short_strategy(
            group_results_p2['group_returns_series'],
            ic_mean=ic_metrics_p2['ic_mean']
        )

        # 6. 绘制分组曲线图（Period 2）
        plot_p2_fd, plot_p2_path = tempfile.mkstemp(suffix='.png', prefix='group_returns_p2_')
        os.close(plot_p2_fd)
        plot_group_returns(group_results_p2['group_cumulative_returns'], plot_p2_path)

        # ========================================
        # 保存两个时段的结果
        # ========================================
        save_results_two_periods(
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
            plot_p2_path=plot_p2_path
        )

        return True, factor_name

    except Exception as e:
        import traceback
        return False, f"{factor_file}: {str(e)}\n{traceback.format_exc()}"


def main():
    """主函数"""

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='批量运行加密货币因子分析（两时段样本外验证）',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 分析factors目录下的所有因子
  python batch_analysis.py

  # 分析factors_ta目录下的所有因子
  python batch_analysis.py --dir factors_ta

  # 分析前10个因子
  python batch_analysis.py --limit 10

  # 分析单个因子
  python batch_analysis.py --factor momentum.py
        """
    )

    parser.add_argument(
        '--dir',
        type=str,
        default=None,
        help=f'因子目录路径（默认: {config.FACTOR_DIR}）'
    )

    parser.add_argument(
        '--factor',
        type=str,
        default=None,
        help='指定单个因子文件名（如: momentum.py）'
    )

    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='限制分析前N个因子'
    )

    args = parser.parse_args()

    # 确定因子目录
    factor_dir = args.dir if args.dir else config.FACTOR_DIR

    if not os.path.exists(factor_dir):
        print(f"❌ 错误: 因子目录不存在: {factor_dir}")
        sys.exit(1)

    # 打印标题
    print("=" * 100)
    print("批量因子分析 - 两时段样本外验证")
    print("=" * 100)
    print(f"因子目录: {os.path.abspath(factor_dir)}")
    print(f"Period 1 (样本内): {config.PERIOD1_START} 到 {config.PERIOD1_END}")
    print(f"Period 2 (样本外): {config.PERIOD2_START} 到 {config.PERIOD2_END}")

    # ========================================
    # 加载 Period 1 数据
    # ========================================
    print("\n【步骤 1/4】加载 Period 1 数据（样本内）...")
    print("-" * 100)

    # 临时修改config以加载Period 1数据
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
    print("\n【步骤 2/4】加载 Period 2 数据（样本外）...")
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
    # 获取要分析的因子文件
    # ========================================
    print("\n【步骤 3/4】准备因子列表...")
    print("-" * 100)

    if args.factor:
        # 分析单个因子
        if not args.factor.endswith('.py'):
            args.factor += '.py'

        if not os.path.exists(os.path.join(factor_dir, args.factor)):
            print(f"❌ 错误: 因子文件不存在: {args.factor}")
            sys.exit(1)

        factor_files = [args.factor]
    else:
        # 分析目录下所有因子
        factor_files = [
            f for f in os.listdir(factor_dir)
            if f.endswith('.py') and not f.startswith('__')
        ]
        factor_files.sort()  # 按字母顺序排序

    # 限制数量
    if args.limit:
        factor_files = factor_files[:args.limit]

    print(f"找到 {len(factor_files)} 个因子文件")
    print("=" * 100)

    # ========================================
    # 批量运行
    # ========================================
    print("\n【步骤 4/4】批量分析因子...")
    print("=" * 100)

    success_count = 0
    failed_factors = []

    for i, factor_file in enumerate(factor_files, 1):
        print(f"\n[{i}/{len(factor_files)}] 正在分析: {factor_file}")
        print("-" * 100)

        start_time = time.time()
        success, result = run_factor_analysis_two_periods(
            factor_file, data_p1, data_p2,
            forward_returns_p1, forward_returns_p2,
            factor_dir
        )
        elapsed = time.time() - start_time

        if success:
            success_count += 1
            print(f"\n✓ 完成: {result} (耗时: {elapsed:.1f}秒)")
        else:
            failed_factors.append(result)
            print(f"\n✗ 失败: {result}")

    # ========================================
    # 汇总结果
    # ========================================
    print("\n" + "=" * 100)
    print("批量分析完成！")
    print("=" * 100)
    print(f"✓ 成功: {success_count}/{len(factor_files)}")
    print(f"✗ 失败: {len(failed_factors)}/{len(factor_files)}")

    if failed_factors:
        print("\n失败的因子:")
        for factor in failed_factors:
            print(f"  - {factor}")

    print(f"\n结果保存在: {os.path.abspath(config.RESULT_DIR)}/all_factors_metrics.csv")
    print("=" * 100)


if __name__ == "__main__":
    main()
