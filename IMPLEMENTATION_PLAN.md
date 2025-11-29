# 加密货币因子分析程序 - 实现计划

## 1. 项目概述

构建一个用于分析加密货币5分钟级别因子的程序，计算IC指标、分组收益、多空策略等核心指标。

## 2. 数据说明

- **数据源**: `main_5m/` 目录下的CSV文件
- **数据格式**: datetime, timestamp, open, high, low, close, volume
- **测试参数**:
  - 时间范围: 1个月 (约8640个5分钟周期)
  - 币种数量: 10个
  - 测试因子: 2个

## 3. 核心功能模块

### 3.1 数据加载模块 (`data_loader.py`)

**功能**:
- 读取指定币种的OHLCV数据
- 数据对齐（确保所有币种时间戳一致）
- 数据清洗（处理缺失值、异常值）
- 支持时间范围筛选

**输入**: 币种列表、时间范围
**输出**: 面板数据 (多币种 × 时间序列)

### 3.2 因子计算模块 (`factor_calculator.py`)

**功能**:
- 从Python文件加载因子函数
- 执行因子计算（输入OHLCV，输出因子值）
- 因子值标准化/归一化（可选）

**因子函数规范**:
```python
def factor_function(data):
    """
    Args:
        data: dict包含 'open', 'high', 'low', 'close', 'volume'
              每个key对应DataFrame (index=datetime, columns=symbols)

    Returns:
        factor_values: DataFrame (index=datetime, columns=symbols)
    """
    pass
```

### 3.3 收益计算模块 (`return_calculator.py`)

**功能**:
- 计算未来N期收益率
- 支持不同收益计算方式（简单收益率、对数收益率）

**公式**:
- 1周期收益率: `(close_t+1 - close_t) / close_t`

### 3.4 IC分析模块 (`ic_analyzer.py`)

**功能**:
- 计算每个时间截面的IC (Pearson相关系数)
- 计算每个时间截面的Rank IC (Spearman相关系数)
- 计算IC均值、标准差
- 计算ICIR = IC均值 / IC标准差

**输出**:
- IC均值
- Rank IC均值
- ICIR

### 3.5 分组分析模块 (`group_analyzer.py`)

**功能**:
- 按因子值每期分成5组（quintile）
- 计算每组的平均收益率
- 计算累积收益曲线
- 生成分组收益曲线图

**输出**:
- 5组的平均收益率
- 5组的累积收益曲线数据
- 分组曲线图（PNG文件）

### 3.6 多空策略模块 (`long_short_strategy.py`)

**功能**:
- 做多第5组（因子值最高），做空第1组（因子值最低）
- 计算多空组合收益率
- 计算Sharpe Ratio (年化)
- 计算最大回撤

**公式**:
- 多空收益 = Group5收益 - Group1收益
- Sharpe = 年化收益均值 / 年化收益标准差
- 最大回撤 = max((累积最高点 - 当前点) / 累积最高点)

### 3.7 结果保存模块 (`result_saver.py`)

**功能**:
- 创建因子专属文件夹
- 保存分析指标到统一的汇总CSV（支持横向比较）
- 保存分组曲线图
- 保存因子值数据
- 覆盖同名因子的旧结果

**输出结构**:
```
results/
  ├── all_factors_metrics.csv  # 所有因子指标汇总（横向比较）
  ├── factor_name_1/
  │   ├── factor_values.csv    # 因子值
  │   └── group_returns.png    # 分组曲线图
  └── factor_name_2/
      ├── factor_values.csv
      └── group_returns.png
```

**all_factors_metrics.csv 格式**（每行是一个因子）:
```
因子名称,IC均值,Rank IC均值,ICIR,Group1平均收益,Group2平均收益,Group3平均收益,Group4平均收益,Group5平均收益,多空收益,Sharpe Ratio,最大回撤,累积收益率
momentum,0.05,0.048,1.2,0.001,0.0015,0.002,0.0025,0.003,0.002,1.5,0.15,1.25
volume_price,0.03,0.028,0.8,0.0008,0.0012,0.0018,0.0022,0.0028,0.002,1.3,0.12,1.18
```

**说明**:
- 每次运行因子分析，结果会追加到 `all_factors_metrics.csv`
- 如果是同名因子，会覆盖该因子之前在CSV中的记录
- 这样可以在一个文件中对比所有测试过的因子表现

### 3.8 主程序 (`main.py`)

**功能**:
- 命令行界面，选择因子文件
- 配置参数（币种、时间范围）
- 调用各模块完成完整分析流程
- 输出分析报告

**流程**:
1. 加载配置（币种列表、时间范围）
2. 加载数据
3. 加载因子函数
4. 计算因子值
5. 计算未来收益
6. 执行IC分析
7. 执行分组分析
8. 执行多空策略分析
9. 保存所有结果

## 4. 配置文件 (`config.py`)

**测试配置**:
```python
# 币种配置
SYMBOLS = [
    'BTC_USDT', 'ETH_USDT', 'BNB_USDT', 'ADA_USDT',
    'SOL_USDT', 'XRP_USDT', 'DOT_USDT', 'DOGE_USDT',
    'AVAX_USDT', 'MATIC_USDT'
]

# 时间配置
START_DATE = '2024-10-01'  # 1个月前
END_DATE = '2024-11-01'

# 分析配置
N_GROUPS = 5  # 分组数量
FORWARD_PERIODS = 1  # 预测周期（5分钟）

# 路径配置
DATA_DIR = 'main_5m'
FACTOR_DIR = 'factors'  # 存放因子py文件
RESULT_DIR = 'results'  # 存放分析结果
```

## 5. 示例因子文件

### `factors/momentum.py`
```python
def calculate(data):
    """动量因子：过去20期收益率"""
    close = data['close']
    return close.pct_change(20)
```

### `factors/volume_price.py`
```python
def calculate(data):
    """量价因子：成交量加权价格变化"""
    close = data['close']
    volume = data['volume']

    price_change = close.pct_change(10)
    volume_ma = volume.rolling(10).mean()

    return price_change * (volume / volume_ma)
```

## 6. 依赖库

- pandas: 数据处理
- numpy: 数值计算
- matplotlib: 绘图
- scipy: 统计计算

## 7. 文件结构

```
Crypto因子分析/
├── main_5m/                    # 原始数据目录
├── factors/                    # 因子定义目录
│   ├── momentum.py
│   └── volume_price.py
├── results/                    # 分析结果目录（自动生成）
├── src/                        # 源代码目录
│   ├── data_loader.py
│   ├── factor_calculator.py
│   ├── return_calculator.py
│   ├── ic_analyzer.py
│   ├── group_analyzer.py
│   ├── long_short_strategy.py
│   └── result_saver.py
├── config.py                   # 配置文件
├── main.py                     # 主程序
└── requirements.txt            # 依赖库
```

## 8. 扩展性设计

程序设计为参数化，便于后续扩展：

- 币种数量：修改 `config.py` 中的 `SYMBOLS` 列表
- 时间范围：修改 `START_DATE` 和 `END_DATE`
- 分组数量：修改 `N_GROUPS`
- 预测周期：修改 `FORWARD_PERIODS`（支持多周期分析）

## 9. 开发步骤

1. 创建项目结构和配置文件
2. 实现数据加载模块（先验证数据读取正确性）
3. 实现因子计算模块（测试示例因子）
4. 实现收益计算模块
5. 实现IC分析模块
6. 实现分组分析模块
7. 实现多空策略模块
8. 实现结果保存模块
9. 整合主程序
10. 测试完整流程

## 10. 注意事项

- 数据对齐：确保所有币种的时间戳对齐
- 前视偏差：计算因子时不能使用未来数据
- 异常处理：处理数据缺失、除零等异常情况
- 性能优化：使用向量化操作，避免循环
- 结果覆盖：同名因子再次分析时自动覆盖旧结果
