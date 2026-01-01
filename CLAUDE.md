# Claude Code 项目规则

本文件定义了 Claude Code 在此项目中工作时必须遵循的规则。

---

## 文档同步规则

### README.md 同步更新

每当对项目进行以下改动时，**必须同步更新 README.md**：

1. **新增文件/目录**
   - 在"目录结构"部分添加新文件/目录的说明
   - 如果是核心模块，在"核心模块说明"部分添加描述

2. **新增因子**
   - 更新因子数量统计
   - 如果是新类别，在"因子分类"表格中添加

3. **修改配置参数**
   - 更新"配置文件 (config.py)"部分的示例代码

4. **新增/修改功能**
   - 更新"核心功能"部分的使用说明
   - 更新命令行示例

5. **修改依赖**
   - 更新"技术栈"表格

6. **重要变更**
   - 在"更新日志"部分添加记录，格式：`- **YYYY-MM-DD**: 变更描述`

---

## 因子开发规则

### 因子文件规范

1. **命名规则**: `{类别}_{名称}_{参数1}_{参数2}...{参数n}.py`
   - 类别: momentum, oscillator, trend, volatility, volume, price
   - 示例: `momentum_roc_12.py`, `oscillator_rsi_6.py`

2. **代码结构**:
   ```python
   """
   因子描述
   参数说明
   """

   import pandas as pd
   import numpy as np

   def calculate(data):
       """
       Args:
           data: {'open': DataFrame, 'high': DataFrame,
                  'low': DataFrame, 'close': DataFrame,
                  'volume': DataFrame}
       Returns:
           pd.DataFrame: 因子值
       """
       # 实现代码
       return factor
   ```

3. **库限制**: 只能使用 pandas 和 numpy，禁止使用 talib、pandas_ta

### 入库标准

因子需在两个时间段均满足：
- |IC| > 0.01
- |ICIR| > 0.05
- 与现有因子相关性 < 70%

---

## 代码规范

1. **Python 版本**: 3.8+
2. **编码**: UTF-8
3. **风格**: PEP 8
4. **注释**: 使用中文注释

---

## 目录结构约定

```
crypto-factor-analysis/
├── main.py                    # 主程序入口
├── batch_analysis.py          # 批量分析
├── config.py                  # 配置文件
├── src/                       # 核心模块
├── factors/                   # 因子库
├── factor_discard/            # 废弃因子
├── main_5m/                   # 原始数据
├── results/                   # 分析结果
├── docs/                      # 文档
├── README.md                  # 项目文档 (PRD)
└── CLAUDE.md                  # Claude Code 规则 (本文件)
```

---

## 提交规范

1. 提交前确认 README.md 已同步更新
2. 新增因子需先通过入库标准测试
3. 废弃因子移至 `factor_discard/` 目录
