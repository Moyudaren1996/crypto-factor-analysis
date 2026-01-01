# Crypto Factor Analysis System
# 加密货币因子分析系统

一个专业的加密货币量化因子研究框架，支持5分钟级别K线数据的因子开发、测试、评估和策略回测。

## 项目信息

- **GitHub**: https://github.com/Moyudaren1996/crypto-factor-analysis
- **Token**: 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

---

## 项目概览

| 项目属性 | 说明 |
|---------|------|
| **数据频率** | 5分钟K线 |
| **覆盖币种** | 37个主流加密货币 |
| **因子数量** | 162个（6大类技术指标因子） |
| **分析方法** | IC分析、分组分析、多空策略回测 |
| **回测框架** | LightGBM滚动回测 |

---

## 目录结构

```
crypto-factor-analysis/
│
├── main.py                    # 主程序入口（单因子分析）
├── batch_analysis.py          # 批量因子分析脚本
├── single_factor_analysis.py  # 两时段分析（样本内外分离）
├── summarize_results.py       # 结果汇总排序
├── rolling_backtest_5m_strategy_regression_lgb.py  # LightGBM滚动回测（全量因子）
├── rolling_backtest_selected_factors.py  # 精选因子回测（使用selected_factors.txt）
├── config.py                  # 全局配置文件
├── requirements.txt           # Python依赖
├── selected_factors.txt       # 精选因子列表（57个）
│
├── src/                       # 核心源代码模块
│   ├── data_loader.py         # 数据加载（多币种OHLCV）
│   ├── factor_calculator.py   # 因子计算（动态加载）
│   ├── return_calculator.py   # 收益计算（未来N期）
│   ├── ic_analyzer.py         # IC分析（Pearson/Spearman）
│   ├── group_analyzer.py      # 分组分析（5分位数）
│   ├── long_short_strategy.py # 多空策略（Sharpe/回撤）
│   └── result_saver.py        # 结果保存（CSV/图表）
│
├── factors/                   # 因子库（162个因子）
│   ├── momentum_*.py          # 动量因子（34个）
│   ├── oscillator_*.py        # 摆动因子（26个）
│   ├── trend_*.py             # 趋势因子（36个）
│   ├── volatility_*.py        # 波动性因子（30个）
│   ├── volume_*.py            # 成交量因子（13个）
│   └── price_*.py             # 价格因子
│
├── factor_discard/            # 废弃因子存放区（75个）
│
├── main_5m/                   # 原始数据（36个币种5分钟K线）
│   └── {SYMBOL}_USDT_5m_*.csv
│
├── results/                   # 分析结果输出
│   ├── all_factors_metrics.csv    # 所有因子汇总指标
│   └── {factor_name}/             # 各因子详细结果
│       ├── factor_values.csv
│       └── group_returns.png
│
├── docs/                      # 项目文档
│   ├── FACTOR_DATABASE.md     # 因子库详细文档
│   ├── FACTOR_MINING_STANDARDS.md  # 因子挖掘规范
│   └── FACTOR_MINING_PROMPT.md     # AI辅助挖掘指南
│
├── rolling_results_5m_selected_factors/   # 滚动回测结果（全量因子）
├── rolling_results_selected_factors/      # 精选因子回测结果
├── trained_models_5m_selected_factors/    # 训练好的模型（全量因子）
├── trained_models_selected_factors/       # 精选因子模型
├── cache_5m/                  # 数据缓存
├── lgb_factor_results/        # LightGBM结果
└── insight/                   # 分析洞察
```

---

## 核心功能

### 1. 单因子分析 (main.py)

分析单个因子的预测能力和收益表现。

```bash
# 交互式选择因子
python3 main.py

# 指定因子
python3 main.py --factor momentum_roc_12.py

# 列出所有因子
python3 main.py --list
```

**分析流程**:
1. 加载多币种数据
2. 计算因子值
3. 计算未来6期收益（30分钟）
4. IC分析（相关性）
5. 5组分位数分析
6. 多空策略评估
7. 保存结果

### 2. 批量分析 (batch_analysis.py)

批量分析多个因子，支持样本内外分离。

```bash
# 分析所有因子
python3 batch_analysis.py

# 分析前10个因子
python3 batch_analysis.py --limit 10

# 指定单个因子
python3 batch_analysis.py --factor momentum_roc_12.py
```

### 3. 结果汇总 (summarize_results.py)

按不同指标排序，找出最佳因子。

```bash
python3 summarize_results.py
```

**输出**:
- 按ICIR排序（稳定性）
- 按Sharpe Ratio排序（风险调整收益）
- 按累积收益率排序

### 4. 滚动回测 (rolling_backtest_5m_strategy_regression_lgb.py)

使用LightGBM模型进行多周期滚动回测（全量因子）。

```bash
python3 rolling_backtest_5m_strategy_regression_lgb.py
```

**回测设置**:
- 33个币种
- 16个滚动周期（2022-2025，每周期3个月）
- 训练集：累积历史数据
- 测试集：3个月

### 5. 精选因子回测 (rolling_backtest_selected_factors.py)

使用 `selected_factors.txt` 中的57个精选因子进行回测。

```bash
python3 rolling_backtest_selected_factors.py
```

**特点**:
- 从 `factors/` 目录动态加载因子
- 支持 pandas_ta 因子和自定义因子
- 可配置单周期快速测试模式
- 结果保存到 `rolling_results_selected_factors/`

**配置参数**（在脚本开头修改）:
```python
SINGLE_PERIOD_MODE = True   # 单周期模式（快速测试）
SELECTED_PERIOD = 8         # 选择第8个周期
SYMBOLS = ["BTC", "ETH", "SOL", ...]  # 测试币种
```

---

## 核心模块说明

### src/data_loader.py
**功能**: 从CSV加载多币种OHLCV数据
- 加载36个币种的5分钟K线
- 时间范围对齐
- 缺失值处理（前向+后向填充）

### src/factor_calculator.py
**功能**: 动态加载并计算因子值
- 使用importlib动态导入
- 处理无穷大和NaN值

### src/ic_analyzer.py
**功能**: 计算因子与收益的相关性
- **IC**: Pearson相关系数
- **Rank IC**: Spearman相关系数
- **ICIR**: IC信息比率 = IC均值/IC标准差

### src/group_analyzer.py
**功能**: 按因子值分组分析
- 5组分位数分组
- 计算各组平均收益
- 生成累积收益曲线

### src/long_short_strategy.py
**功能**: 多空组合策略分析
- IC>0时：做多高因子组，做空低因子组
- IC<0时：反向操作
- 计算Sharpe、最大回撤、累积收益

---

## 因子库

### 因子分类

| 类别 | 数量 | 描述 | 示例 |
|------|------|------|------|
| **Momentum** | 34 | 动量/趋势强度 | momentum_roc_12, momentum_asymaccel_24 |
| **Oscillator** | 26 | 超买超卖指标 | oscillator_rsi_6, oscillator_extreme_velocity_3_48 |
| **Trend** | 36 | 趋势方向/强度 | trend_ema_6, trend_vortex_48 |
| **Volatility** | 30 | 波动性指标 | volatility_atr_24, volatility_range_momentum_12 |
| **Volume** | 13 | 成交量分析 | volume_cmf_240, volume_obv_slope_24 |
| **Price** | 1 | 价格指标 | price_vwap |

### 因子命名规则

```
{类别}_{名称}_{参数1}_{参数2}...{参数n}.py
```

示例:
- `momentum_roc_12.py` - 动量类ROC因子，周期12
- `oscillator_rsi_6.py` - 摆动类RSI因子，周期6
- `trend_adx_240.py` - 趋势类ADX因子，周期240

### 因子入库标准

因子需在两个时间段均满足：
- **|IC| > 0.01** - 具有预测能力
- **|ICIR| > 0.05** - 具有稳定性
- **与现有因子相关性 < 70%** - 具有独特性

---

## 配置文件 (config.py)

```python
# 币种配置（37个）
SYMBOLS = ['AAVE_USDT', 'ADA_USDT', ..., 'ZEC_USDT']

# 时间配置
PERIOD1_START = '2024-07-19 00:00:00'  # 样本内开始
PERIOD1_END = '2024-10-18 23:55:00'    # 样本内结束（约3个月）
PERIOD2_START = '2024-10-19 00:00:00'  # 样本外开始
PERIOD2_END = '2025-01-18 23:55:00'    # 样本外结束（约3个月）

# 分析参数
N_GROUPS = 5           # 分组数量
FORWARD_PERIODS = 6    # 预测周期（6个5分钟=30分钟）
PERIODS_PER_YEAR = 105120  # 年化周期数

# 路径配置
DATA_DIR = 'main_5m'
FACTOR_DIR = 'factors'
RESULT_DIR = 'results'
```

---

## 指标说明

### IC指标

| 指标 | 说明 | 优秀标准 |
|------|------|---------|
| **IC** | Pearson相关系数，衡量线性相关性 | \|IC\| > 0.02 |
| **Rank IC** | Spearman相关系数，更稳健 | \|Rank IC\| > 0.02 |
| **ICIR** | IC信息比率，衡量稳定性 | \|ICIR\| > 0.1 |

### 策略指标

| 指标 | 说明 | 优秀标准 |
|------|------|---------|
| **Sharpe Ratio** | 风险调整收益 | > 1.0 |
| **Max Drawdown** | 最大回撤 | > -20% |
| **Cumulative Return** | 累积收益率 | > 10% |

### 分组分析

- **Group 1**: 因子值最低的20%
- **Group 5**: 因子值最高的20%
- IC>0时：预期Group5 > Group1
- IC<0时：预期Group1 > Group5

---

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行单因子分析

```bash
python3 main.py --factor momentum_roc_12.py
```

### 3. 批量分析所有因子

```bash
python3 batch_analysis.py
```

### 4. 查看结果汇总

```bash
python3 summarize_results.py
```

---

## 自定义因子

在 `factors/` 目录下创建新的Python文件：

```python
"""
我的自定义因子
计算价格变化率
"""

def calculate(data):
    """
    Args:
        data: {'open': DataFrame, 'high': DataFrame,
               'low': DataFrame, 'close': DataFrame,
               'volume': DataFrame}
              每个DataFrame: index=datetime, columns=symbols

    Returns:
        pd.DataFrame: 因子值 (index=datetime, columns=symbols)
    """
    close = data['close']
    factor = close.pct_change(20)
    return factor
```

**重要**: 只能使用 pandas 和 numpy，禁止使用 talib、pandas_ta 等库。

---

## 技术栈

| 库 | 版本 | 用途 |
|----|------|------|
| pandas | >= 1.5.0 | 数据处理 |
| numpy | >= 1.23.0 | 数值计算 |
| matplotlib | >= 3.6.0 | 可视化 |
| scipy | >= 1.9.0 | 统计分析 |
| scikit-learn | >= 1.2.0 | 机器学习工具 |
| lightgbm | >= 4.0.0 | 梯度提升模型 |
| xgboost | >= 2.0.0 | XGBoost模型 |

---

## 文档

详细文档位于 `docs/` 目录：

- [FACTOR_DATABASE.md](docs/FACTOR_DATABASE.md) - 因子库完整文档
- [FACTOR_MINING_STANDARDS.md](docs/FACTOR_MINING_STANDARDS.md) - 因子挖掘规范
- [FACTOR_MINING_PROMPT.md](docs/FACTOR_MINING_PROMPT.md) - AI辅助挖掘指南

---

## 注意事项

1. 确保 `main_5m/` 目录包含足够的币种数据
2. 因子计算时避免使用未来数据（前视偏差）
3. 理论Sharpe是实际可实现的3-10倍（未考虑交易成本、滑点等）
4. 大规模数据分析可能需要较长时间

---

## 更新日志

- **2025-01-01**: 新增 `rolling_backtest_selected_factors.py` 精选因子回测脚本
- **2025-01-01**: 项目结构整理，文档移至 `docs/` 目录，创建 `CLAUDE.md` 规则文件
- **初始版本**: 162个因子，完整分析框架
