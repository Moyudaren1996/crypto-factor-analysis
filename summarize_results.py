"""
汇总并排序因子分析结果
"""
import pandas as pd
import numpy as np

# 读取结果
df = pd.read_csv('results/all_factors_metrics.csv')

print("=" * 120)
print("所有因子分析结果汇总（共 {} 个因子）".format(len(df)))
print("=" * 120)

# 按不同指标排序并展示
print("\n【按 ICIR 排序（绝对值，越大越稳定）】")
print("-" * 120)
df_icir = df.copy()
df_icir['ICIR_abs'] = df_icir['ICIR'].abs()
df_icir_sorted = df_icir.sort_values('ICIR_abs', ascending=False)
print(df_icir_sorted[['因子名称', 'IC均值', 'Rank IC均值', 'ICIR', 'Sharpe Ratio']].head(10).to_string(index=False))

print("\n【按 Sharpe Ratio 排序（越大越好）】")
print("-" * 120)
df_sharpe_sorted = df.sort_values('Sharpe Ratio', ascending=False)
print(df_sharpe_sorted[['因子名称', 'ICIR', 'Sharpe Ratio', '最大回撤', '累积收益率', '多空收益']].head(10).to_string(index=False))

print("\n【按 IC均值 排序（正向，越大越好）】")
print("-" * 120)
df_ic_sorted = df.sort_values('IC均值', ascending=False)
print(df_ic_sorted[['因子名称', 'IC均值', 'Rank IC均值', 'ICIR', 'Sharpe Ratio']].head(10).to_string(index=False))

print("\n【按 累积收益率 排序】")
print("-" * 120)
df_cum_sorted = df.sort_values('累积收益率', ascending=False)
print(df_cum_sorted[['因子名称', '累积收益率', 'Sharpe Ratio', '最大回撤', '多空收益']].head(10).to_string(index=False))

print("\n【所有因子完整结果（按Sharpe排序）】")
print("=" * 120)
df_full_sorted = df.sort_values('Sharpe Ratio', ascending=False)
print(df_full_sorted[['因子名称', 'IC均值', 'ICIR', 'Sharpe Ratio', '最大回撤', '累积收益率']].to_string(index=False))

print("\n" + "=" * 120)
print("统计摘要")
print("=" * 120)
print(f"总因子数量: {len(df)}")
print(f"正IC因子数量: {(df['IC均值'] > 0).sum()}")
print(f"正Sharpe因子数量: {(df['Sharpe Ratio'] > 0).sum()}")
print(f"Sharpe > 1 的因子数量: {(df['Sharpe Ratio'] > 1).sum()}")
print(f"ICIR绝对值 > 0.1 的因子数量: {(df['ICIR'].abs() > 0.1).sum()}")

print(f"\n平均IC: {df['IC均值'].mean():.6f}")
print(f"平均ICIR: {df['ICIR'].mean():.6f}")
print(f"平均Sharpe: {df['Sharpe Ratio'].mean():.4f}")

print("\n" + "=" * 120)
print("TOP 5 最佳因子（综合评分）")
print("=" * 120)
# 综合评分：标准化后加权
df_score = df.copy()
df_score['IC_score'] = (df_score['IC均值'] - df_score['IC均值'].mean()) / df_score['IC均值'].std()
df_score['ICIR_score'] = (df_score['ICIR'].abs() - df_score['ICIR'].abs().mean()) / df_score['ICIR'].abs().std()
df_score['Sharpe_score'] = (df_score['Sharpe Ratio'] - df_score['Sharpe Ratio'].mean()) / df_score['Sharpe Ratio'].std()
df_score['综合得分'] = df_score['IC_score'] * 0.3 + df_score['ICIR_score'] * 0.3 + df_score['Sharpe_score'] * 0.4

df_top = df_score.sort_values('综合得分', ascending=False).head(5)
print(df_top[['因子名称', 'IC均值', 'ICIR', 'Sharpe Ratio', '累积收益率', '综合得分']].to_string(index=False))

# 保存排序后的结果
df_full_sorted.to_csv('results/factors_ranked_by_sharpe.csv', index=False, encoding='utf-8-sig')
df_top.to_csv('results/top5_factors.csv', index=False, encoding='utf-8-sig')

print("\n排序结果已保存:")
print("  - results/factors_ranked_by_sharpe.csv")
print("  - results/top5_factors.csv")
print("=" * 120)
