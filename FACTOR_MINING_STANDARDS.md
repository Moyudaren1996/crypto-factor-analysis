# 因子命名与代码规范

## 版本信息
- **文档版本**: v2.0
- **创建日期**: 2024-12-01
- **更新日期**: 2025-12-06
- **适用范围**: 加密货币因子分析系统

---

## 1. 因子命名规则

### 1.1 文件命名格式

**格式**: `{category}_{name}_{param1}_{param2}_...{param_n}.py`

**示例**:
```
momentum_roc_12.py              # 动量类-ROC-12期
oscillator_rsi_6.py             # 摆动指标-RSI-6期
trend_macd_3_6_2.py             # 趋势类-MACD-快3慢6信号2
volatility_atr_12.py            # 波动率-ATR-12期
volatility_bbands_6_2.py        # 波动率-布林带-6期2倍标准差
volume_cmf_6.py                 # 成交量-CMF-6期
trend_ema_12.py                 # 趋势类-EMA-12期
```

### 1.2 因子类别 (Category)

| 类别 | 英文 | 说明 | 示例 |
|------|------|------|------|
| 动量 | momentum | 价格变化率、动量指标 | ROC, MOM, TSI, PPO |
| 摆动指标 | oscillator | 超买超卖指标 | RSI, Stochastic, Williams %R, CCI, Fisher |
| 趋势 | trend | 趋势跟踪指标 | MACD, ADX, EMA, SMA, TEMA, DEMA, KAMA |
| 波动率 | volatility | 价格波动性指标 | ATR, 布林带, Keltner通道, Choppiness |
| 成交量 | volume | 成交量相关指标 | OBV, CMF, MFI, PVO |
| 价格 | price | 价格相关指标 | VWAP |

### 1.3 参数命名规范

- **周期参数**: 使用数字，单位为K线根数（5分钟K线）
  - `3` = 3个5分钟K线 = 15分钟
  - `6` = 6个5分钟K线 = 30分钟
  - `12` = 12个5分钟K线 = 1小时
  - `144` = 144个5分钟K线 = 12小时
  - `288` = 288个5分钟K线 = 24小时

- **倍数参数**: 直接使用数字或小数
  - `2` = 2倍标准差
  - `1_5` = 1.5倍（文件名中小数点用下划线代替）

- **多参数**: 按计算顺序排列，用下划线分隔
  - `macd_3_6_2` = 快线3, 慢线6, 信号线2
  - `stoch_6_3_2` = K线周期6, K平滑3, D平滑2

---

## 2. 代码结构规范

### 2.1 标准模板

```python
"""
[因子类别]指标 - [因子名称]

因子描述:
    [详细描述指标的含义和计算逻辑]

参数:
    period: [周期值] ([时间描述，如30分钟])
    [其他参数]: [参数值] ([参数说明])

计算公式:
    [用数学表达式或伪代码描述计算逻辑]

输出:
    因子值DataFrame

数据依赖:
    - close: 收盘价 (必需/可选)
    - high: 最高价 (必需/可选)
    - low: 最低价 (必需/可选)
    - volume: 成交量 (必需/可选)

创建日期: YYYY-MM-DD
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算[因子名称]因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame，columns为币种symbol

    Returns:
        pd.DataFrame: 因子值，index为时间，columns为币种symbol
    """
    # 提取所需数据
    close = data['close']
    # high = data['high']
    # low = data['low']
    # volume = data['volume']

    # 定义参数
    period = 12  # 根据文件名设定

    # 计算因子
    # [在此处使用pandas/numpy进行向量化计算]
    factor = (close - close.shift(period)) / close.shift(period) * 100

    return factor
```

### 2.2 完整示例

#### 示例1: 动量指标 - ROC

**文件名**: `momentum_roc_12.py`

```python
"""
Momentum指标 - ROC (Rate of Change)

因子描述:
    变动率指标，衡量价格相对于N期前的百分比变化
    ROC > 0 表示价格上涨，ROC < 0 表示价格下跌

参数:
    period: 12 (1小时)

计算公式:
    ROC = (close - close[t-period]) / close[t-period] * 100

输出:
    因子值DataFrame，单位为百分比

数据依赖:
    - close: 收盘价 (必需)

创建日期: 2024-12-01
版本: v1.0
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算ROC因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']

    Returns:
        pd.DataFrame: 因子值
    """
    close = data['close']
    period = 12

    # 计算ROC
    roc = (close - close.shift(period)) / close.shift(period) * 100

    return roc
```


### 2.3 必需组件

每个因子文件必须包含：

1. **文档字符串**: 详细描述因子的类别、名称、参数、计算公式、输出和数据依赖
2. **导入语句**: `import pandas as pd`, `import numpy as np`
3. **calculate()函数**: 因子计算主函数，接收data字典，返回DataFrame

---

## 3. 开发规范

### 3.1 必须遵守的规则

**使用的库**:
- **只允许使用**: `pandas`, `numpy`
- **禁止使用**: `talib`, `pandas_ta`, `scipy`, 以及其他第三方技术分析库
- **推荐**: 基于pandas和numpy的向量化操作直接实现所有指标

**数据处理**:
- 直接操作data字典中的DataFrame
- 使用向量化操作，避免显式循环（for/while）
- 使用pandas的内置方法: `.rolling()`, `.ewm()`, `.shift()`, `.diff()` 等
- 正确处理NaN值和边界情况

**代码风格**:
- 参数直接硬编码在函数中（与文件名对应）
- 使用清晰的变量名
- 添加必要的注释说明计算逻辑
- 保持代码简洁，避免过度抽象

**避免未来函数** ⚠️ **极其重要**:
- **严格禁止使用未来数据**，所有计算只能使用当前时刻及之前的数据
- 不允许使用`shift(-n)`（负数位移会引入未来数据）
- 不允许使用全局统计量（如全序列的`.mean()`, `.std()`）进行标准化
- 滚动窗口计算时，确保窗口只包含历史数据
- 使用`.rolling()`时默认是向后看的（backward-looking），这是正确的

**控制计算量** ⚠️ **极其重要**:
- 避免过大的滚动窗口（建议不超过1440，即5天 × 288个5分钟K线）
- 避免嵌套多层循环
- 避免重复计算相同的中间结果
- 对于复杂指标，优先使用pandas内置的优化方法
- 避免使用`.apply()` lambda函数，尽量用向量化操作替代

### 3.2 常见错误示例

**错误1: 使用未来函数**
```python
# ❌ 错误：使用了未来数据
future_max = close.shift(-5).rolling(10).max()
future_return = close.shift(-1) / close - 1
```

**错误2: 使用全局统计量**
```python
# ❌ 错误：使用了全序列统计量
normalized = (close - close.mean()) / close.std()
# 这会导致在t时刻使用了t+1, t+2...的数据
```

**错误3: 计算量过大**
```python
# ❌ 错误：窗口过大
result = close.rolling(10000).mean()  # 10000个5分钟 ≈ 34天
```

**错误4: 引入不允许的库**
```python
# ❌ 错误：使用了不允许的库
import talib
import pandas_ta as ta
import scipy
```

**错误5: 使用循环代替向量化**
```python
# ❌ 错误：使用循环
result = []
for i in range(len(close)):
    result.append(close.iloc[i] / close.iloc[i-10] - 1)

# ✅ 正确：使用向量化
result = close / close.shift(10) - 1
```

---

## 4. 可用算子定义

以下算子都可以通过pandas和numpy实现，无需额外依赖。

### 4.1 数学运算算子

| 算子 | 函数形式 | 说明 | pandas/numpy实现 |
|------|---------|------|-----------------|
| Addition | `Add(x, y)` | 加法 | `x + y` |
| Subtraction | `Sub(x, y)` | 减法 | `x - y` |
| Multiplication | `Mul(x, y)` | 乘法 | `x * y` |
| Division | `Div(x, y)` | 除法 | `x / y` |
| Logarithm | `Log(x)` | 对数 | `np.log(x)` |
| Absolute Value | `Abs(x)` | 绝对值 | `x.abs()` 或 `np.abs(x)` |
| Power | `Power(x, n)` | 幂运算 | `x ** n` 或 `np.power(x, n)` |
| Sign | `Sign(x)` | 符号函数 | `np.sign(x)` |
| Square Root | `Sqrt(x)` | 平方根 | `np.sqrt(x)` |
| Exponential | `Exp(x)` | 指数函数 | `np.exp(x)` |

**示例**:
```python
# 对数收益率
log_return = np.log(close / close.shift(1))

# 价格标准化
normalized = (close - close.rolling(100).mean()) / close.rolling(100).std()

# 符号函数
price_direction = np.sign(close.diff())
```

### 4.2 时间序列算子（滚动窗口）

| 算子 | 函数形式 | 说明 | pandas实现 |
|------|---------|------|-----------|
| Rolling Mean | `Mean(x, N)` | 滚动均值 | `x.rolling(N).mean()` |
| Rolling Std | `Std(x, N)` | 滚动标准差 | `x.rolling(N).std()` |
| Rolling Variance | `Var(x, N)` | 滚动方差 | `x.rolling(N).var()` |
| Rolling Sum | `Sum(x, N)` | 滚动求和 | `x.rolling(N).sum()` |
| Rolling Max | `Max(x, N)` | 滚动最大值 | `x.rolling(N).max()` |
| Rolling Min | `Min(x, N)` | 滚动最小值 | `x.rolling(N).min()` |
| Median | `Med(x, N)` | 滚动中位数 | `x.rolling(N).median()` |
| Percentile Rank | `Rank(x, N)` | 百分位排名 | `x.rolling(N).rank(pct=True)` |
| Quantile | `Quantile(x, N, q)` | 分位数 | `x.rolling(N).quantile(q)` |
| Valid Count | `Count(x, N)` | 有效值计数 | `x.rolling(N).count()` |
| Lag | `Ref(x, N)` | 滞后 | `x.shift(N)` (N > 0) |
| Difference | `Diff(x, N)` | 差分 | `x.diff(N)` |
| Delta | `Delta(x, N)` | N期变化量 | `x - x.shift(N)` |
| Percent Change | `Pct(x, N)` | N期收益率 | `x.pct_change(N)` |
| Index of Max | `IdxMax(x, N)` | 最大值位置 | `x.rolling(N).apply(np.argmax)` |
| Index of Min | `IdxMin(x, N)` | 最小值位置 | `x.rolling(N).apply(np.argmin)` |

**示例**:
```python
# 20期移动平均
ma20 = close.rolling(20).mean()

# 价格动量
momentum = close - close.shift(10)

# 相对位置（在N期内的排名百分比）
rank_pct = close.rolling(20).rank(pct=True)

# 滚动最大值回撤
rolling_max = close.rolling(100).max()
drawdown = (close - rolling_max) / rolling_max
```

### 4.3 指数移动平均 (EWM)

| 算子 | 函数形式 | 说明 | pandas实现 |
|------|---------|------|-----------|
| EMA | `EMA(x, N)` | 指数移动平均 | `x.ewm(span=N, adjust=False).mean()` |
| EWM Std | `EWM_Std(x, N)` | 指数加权标准差 | `x.ewm(span=N, adjust=False).std()` |
| EWM Var | `EWM_Var(x, N)` | 指数加权方差 | `x.ewm(span=N, adjust=False).var()` |

**示例**:
```python
# 12期EMA
ema12 = close.ewm(span=12, adjust=False).mean()

# MACD (双EMA)
ema_fast = close.ewm(span=12, adjust=False).mean()
ema_slow = close.ewm(span=26, adjust=False).mean()
macd = ema_fast - ema_slow
signal = macd.ewm(span=9, adjust=False).mean()
```

### 4.4 回归算子（滚动窗口）

使用numpy的线性回归功能，可在滚动窗口内实现。

| 算子 | 函数形式 | 说明 | 实现方式 |
|------|---------|------|---------|
| Slope | `Slope(x, N)` | 回归斜率 | 使用`np.polyfit` |
| Intercept | `Intercept(x, N)` | 回归截距 | 使用`np.polyfit` |
| R-squared | `Rsquare(x, N)` | 决定系数 | 手动计算 |
| Residual | `Resi(x, N)` | 回归残差 | `x - 拟合值` |

**示例**:
```python
# 计算N期线性回归斜率
def linear_regression_slope(series, window):
    def calc_slope(y):
        if len(y) < 2:
            return np.nan
        x = np.arange(len(y))
        slope, _ = np.polyfit(x, y, 1)
        return slope
    return series.rolling(window).apply(calc_slope, raw=True)

slope = linear_regression_slope(close, 20)
```

### 4.5 统计算子（滚动窗口）

| 算子 | 函数形式 | 说明 | pandas实现 |
|------|---------|------|-----------|
| Skewness | `Skew(x, N)` | 偏度 | `x.rolling(N).skew()` |
| Kurtosis | `Kurt(x, N)` | 峰度 | `x.rolling(N).kurt()` |
| Correlation | `Corr(x, y, N)` | 相关系数 | `x.rolling(N).corr(y)` |
| Covariance | `Cov(x, y, N)` | 协方差 | `x.rolling(N).cov(y)` |

**示例**:
```python
# 价格与成交量的20期相关性
price_volume_corr = close.rolling(20).corr(volume)

# 收益率的偏度
returns = close.pct_change()
return_skew = returns.rolling(50).skew()
```

### 4.6 条件算子

| 算子 | 函数形式 | 说明 | pandas/numpy实现 |
|------|---------|------|-----------------|
| Conditional | `If(cond, x, y)` | 条件选择 | `np.where(cond, x, y)` 或 `x.where(cond, y)` |
| Greater Than | `Gt(x, y)` | 大于 | `(x > y).astype(int)` |
| Less Than | `Lt(x, y)` | 小于 | `(x < y).astype(int)` |
| Greater Equal | `Ge(x, y)` | 大于等于 | `(x >= y).astype(int)` |
| Less Equal | `Le(x, y)` | 小于等于 | `(x <= y).astype(int)` |
| Equal | `Eq(x, y)` | 等于 | `(x == y).astype(int)` |
| Not Equal | `Ne(x, y)` | 不等于 | `(x != y).astype(int)` |

**示例**:
```python
# 价格突破20日均线信号
ma20 = close.rolling(20).mean()
breakout_signal = (close > ma20).astype(int)

# 条件选择：上涨时用成交量，下跌时用0
volume_on_up = np.where(close > close.shift(1), volume, 0)
```

### 4.7 逻辑算子

| 算子 | 函数形式 | 说明 | pandas实现 |
|------|---------|------|-----------|
| Logical AND | `And(x, y)` | 逻辑与 | `x & y` |
| Logical OR | `Or(x, y)` | 逻辑或 | `x \| y` |
| Logical NOT | `Not(x)` | 逻辑非 | `~x` |

**示例**:
```python
# 价格上涨且成交量放大
price_up = close > close.shift(1)
volume_up = volume > volume.shift(1)
signal = price_up & volume_up
```

### 4.8 其他常用操作

| 操作 | 说明 | pandas实现 |
|------|------|-----------|
| Cumulative Sum | 累积求和 | `x.cumsum()` |
| Cumulative Product | 累积乘积 | `x.cumprod()` |
| Cumulative Max | 累积最大值 | `x.cummax()` |
| Cumulative Min | 累积最小值 | `x.cummin()` |
| Clip | 截断值 | `x.clip(lower, upper)` |
| Replace | 替换值 | `x.replace(old, new)` |
| Fill NA | 填充缺失值 | `x.fillna(value)` 或 `x.ffill()` / `x.bfill()` |

**示例**:
```python
# 累积收益
cumulative_return = (1 + returns).cumprod() - 1

# 截断异常值
clipped = close.clip(lower=close.quantile(0.01), upper=close.quantile(0.99))

# 前向填充缺失值
filled = close.ffill()
```
---


