# 加密货币因子分析系统

一个用于分析加密货币5分钟级别因子的Python程序。

## 功能特点

- **IC指标分析**: IC、Rank IC、ICIR
- **分组分析**: 按因子值分成5组，计算各组收益及累积收益曲线
- **多空策略**: 计算做多高因子组、做空低因子组的策略表现
- **结果保存**: 自动保存所有指标、因子值和可视化图表
- **自动覆盖**: 同名因子再次分析时自动覆盖旧结果

## 项目结构

```
Crypto因子分析/
├── main_5m/                    # 原始数据目录
├── factors/                    # 因子定义目录
│   ├── momentum.py             # 动量因子示例
│   └── volume_price.py         # 量价因子示例
├── results/                    # 分析结果目录
│   ├── all_factors_metrics.csv # 所有因子指标汇总（横向比较）
│   ├── momentum/
│   │   ├── factor_values.csv   # 因子值
│   │   └── group_returns.png   # 分组曲线图
│   └── volume_price/
│       ├── factor_values.csv
│       └── group_returns.png
├── src/                        # 源代码
│   ├── data_loader.py          # 数据加载
│   ├── factor_calculator.py    # 因子计算
│   ├── return_calculator.py    # 收益计算
│   ├── ic_analyzer.py          # IC分析
│   ├── group_analyzer.py       # 分组分析
│   ├── long_short_strategy.py  # 多空策略
│   └── result_saver.py         # 结果保存
├── config.py                   # 配置文件
├── main.py                     # 主程序
└── requirements.txt            # 依赖库
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 查看可用因子

```bash
python3 main.py --list
```

### 3. 运行因子分析

```bash
python3 main.py --factor momentum.py
```

或者交互式选择：

```bash
python3 main.py
```

## 分析结果说明

分析结果保存在 `results/` 目录下，包含：

### 1. all_factors_metrics.csv - 所有因子指标汇总（横向比较）
位于 `results/all_factors_metrics.csv`，包含所有测试过的因子及其指标，每行是一个因子：

| 因子名称 | IC均值 | Rank IC均值 | ICIR | Group1平均收益 | ... | Sharpe Ratio | 最大回撤 | 累积收益率 |
|---------|--------|------------|------|---------------|-----|-------------|---------|-----------|
| momentum | -0.026 | -0.031 | -0.056 | 0.000023 | ... | -6.998 | -0.275 | 0.761 |
| volume_price | -0.025 | -0.027 | -0.056 | 0.000021 | ... | -6.689 | -0.261 | 0.774 |

**特点**:
- 每次运行因子分析，结果会自动更新到此文件
- 同名因子会覆盖之前的记录
- 方便在一个文件中横向比较所有因子的表现

### 2. 因子专属文件夹 - results/因子名/
每个因子有自己的文件夹，包含：

#### factor_values.csv - 因子值
保存所有时间点、所有币种的因子值，格式：
```
datetime,BTC_USDT,ETH_USDT,...
2024-10-01 00:00:00,0.012,0.015,...
```

#### group_returns.png - 分组收益曲线图
展示5组累积收益曲线的可视化图表

## 如何自定义因子

在 `factors/` 目录下创建新的Python文件，例如 `my_factor.py`：

```python
def calculate(data):
    """
    计算因子值

    Args:
        data: 字典包含 'open', 'high', 'low', 'close', 'volume'
              每个key对应DataFrame (index=datetime, columns=symbols)

    Returns:
        factor_values: 因子值DataFrame (index=datetime, columns=symbols)
    """
    close = data['close']
    # 在此编写你的因子逻辑
    factor = close.pct_change(20)  # 示例
    return factor
```

然后运行：
```bash
python3 main.py --factor my_factor.py
```

## 配置参数扩展

### 扩展到更多币种

编辑 [config.py](config.py)，修改 `SYMBOLS` 列表：

```python
SYMBOLS = [
    'BTC_USDT',
    'ETH_USDT',
    'BNB_USDT',
    # 添加更多币种...
    'LINK_USDT',
    'UNI_USDT',
]
```

### 扩展到更长时间

编辑 [config.py](config.py)，修改时间范围：

```python
START_DATE = '2024-01-01 00:00:00'  # 开始时间
END_DATE = '2024-12-31 23:55:00'    # 结束时间
```

### 修改分组数量

编辑 [config.py](config.py)：

```python
N_GROUPS = 10  # 改为10分组
```

### 修改预测周期

编辑 [config.py](config.py)：

```python
FORWARD_PERIODS = 12  # 改为预测未来12期（1小时）
```

## 当前测试配置

- **币种数量**: 9个（BTC, ETH, BNB, ADA, SOL, XRP, DOT, DOGE, AVAX）
- **时间范围**: 2024-10-01 至 2024-11-01（约8929个5分钟周期）
- **分组数量**: 5组
- **预测周期**: 1期（5分钟）

## 示例因子说明

### 1. momentum.py - 动量因子
- 计算过去20期的价格收益率
- 假设：过去表现好的资产未来仍会表现好

### 2. volume_price.py - 量价因子
- 结合价格变化和成交量放大的复合因子
- 理念：价格上涨且伴随成交量放大，表示上涨动能强

## 常见问题

### Q: 某个币种提示"在指定时间范围内无数据"？
A: 检查该币种的CSV文件中是否包含指定时间范围的数据。某些币种的历史数据可能不完整。

### Q: 如何解读IC指标？
A:
- IC均值：因子与未来收益的相关性，越接近±1越好
- Rank IC均值：排序相关性，更稳健的指标
- ICIR：IC信息比率，IC均值/IC标准差，衡量因子稳定性

### Q: 多空策略的Sharpe为负数怎么办？
A: 说明该因子在当前时段表现不佳，可以：
- 尝试反向使用（做空高因子组，做多低因子组）
- 调整因子参数
- 更换时间段测试

## 依赖库

- pandas >= 1.5.0
- numpy >= 1.23.0
- matplotlib >= 3.6.0
- scipy >= 1.9.0

## 注意事项

1. 确保 `main_5m/` 目录下有足够的币种数据
2. 因子计算时避免使用未来数据（前视偏差）
3. 结果会自动覆盖同名因子的旧分析
4. 大规模数据分析可能需要较长时间，请耐心等待

## 性能优化建议

- 使用向量化操作而非循环
- 合理设置时间范围，避免一次性加载过多数据
- 对于长时间分析，可以考虑分段处理

---

如有问题或建议，欢迎反馈！
