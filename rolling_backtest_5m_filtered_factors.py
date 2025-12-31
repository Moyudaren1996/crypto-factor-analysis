# -*- coding: utf-8 -*-
"""
滚动回测策略（5分钟级别）：LightGBM回归信号 - 筛选因子版本
- 仅使用P1 IC和P2 IC绝对值都大于0.01的57个因子
- 基于 rolling_backtest_5m_strategy_regression_lgb.py 修改
"""

from __future__ import annotations
import os
import warnings
from typing import Tuple, List, Dict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd



# 在导入 pandas_ta 前兼容性补丁
try:
    import importlib
    try:
        import importlib.metadata as _imd
    except Exception:
        import importlib_metadata as _imd
    if not hasattr(importlib, "metadata"):
        importlib.metadata = _imd

except Exception:
    pass

import joblib
from joblib import Parallel, delayed
import pandas_ta as ta
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
import json
import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt

import lightgbm as lgb

# 附加因子模块 - 尝试导入，如果不存在则跳过
try:
    import additional_features
    HAS_ADDITIONAL_FEATURES = True
except ImportError:
    HAS_ADDITIONAL_FEATURES = False
    print("警告: additional_features 模块不可用，将只使用 pandas_ta 技术指标")

# Linux 服务器环境：启用 pandas_ta 多进程以加速技术指标计算
try:
    import platform
    if platform.system() == 'Darwin':  # macOS
        ta.cores = 0  # macOS 禁用多进程避免 spawn 错误
    else:  # Linux
        ta.cores = 8  # 启用8核并行计算技术指标
except Exception:
    pass


warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ============================
# 筛选后的因子列表（P1 IC和P2 IC绝对值都大于0.01）
# ============================
SELECTED_FACTORS = [
    'oscillator_extreme_velocity_3_48', 'oscillator_ar_quality_6_24', 'momentum_asymaccel_24',
    'momentum_cross_dev_12', 'momentum_emadistancereversion_20', 'momentum_osrs_24',
    'momentum_pme_3_48', 'momentum_ppo_3_6_2', 'momentum_roc_1', 'momentum_roc_12',
    'momentum_roc_144', 'momentum_short_accel_revert_6_24', 'momentum_roc_2', 'momentum_roc_3',
    'momentum_roc_6', 'momentum_tsi_300_156', 'momentum_tsi_600_300', 'momentum_tsi_6_3',
    'oscillator_csrank_pvdiv_36', 'oscillator_ivr_3_12', 'oscillator_pvda_2_6',
    'oscillator_rsi_1', 'oscillator_rsi_12', 'oscillator_rsi_2', 'oscillator_rsi_24',
    'oscillator_rsi_3', 'oscillator_rsi_4', 'oscillator_rsi_48', 'oscillator_rsi_5',
    'oscillator_rsi_6', 'oscillator_rsi_72', 'oscillator_rsi_84', 'oscillator_stoch_3_2_2',
    'oscillator_stoch_6_3_2', 'oscillator_uo_2_4_6', 'oscillator_vcompress_6_36',
    'oscillator_willr_3', 'oscillator_willr_6', 'momentum_intraday_range_12_48',
    'trend_vortex_3', 'trend_vortex_6', 'volume_cmf_3', 'volume_cmf_6', 'volume_mfi_3',
    'volume_mfi_6', 'momentum_accel_reversal_12_6_48', 'momentum_path_efficiency_24_96',
    'momentum_volume_weighted_trend_24', 'momentum_dispersion_18_72', 'momentum_vol_price_div_12_48',
    'momentum_vol_ratio_18_36', 'momentum_updown_ratio_12_48', 'momentum_streak_intensity_3_24_48',
    'momentum_directional_pressure_12_48', 'volatility_momentum_ratio_12_72',
    'volatility_squeeze_ratio_12_48', 'volatility_range_deviation_24_72'
]

# ============================
# 全局配置参数
# ============================
RANDOM_STATE = 42
N_JOBS = 60  # LightGBM训练线程数（100核CPU，留40核给系统）
N_PARALLEL_SYMBOLS = 10  # 并行处理的币种数量（特征计算并行化）

# 币种配置
# 完整模式：所有33个币种
SYMBOLS = [
    "BTC", "ETH", "XRP", "BNB", "SOL", "TRX", "ADA", "LINK", "AVAX", "DOGE", "DOT", "MATIC",
    "ALGO", "UNI", "LTC",

    "FIL", "VET", "XLM", "ATOM", "XMR", "EOS", "AAVE", "GRT", "AXS", "THETA", "MANA",

    "POL", "APT", "HBAR", "ICP", "INJ", "OP", "ARB",
]

# 测试模式：如需测试，取消下面的注释，注释掉上面的完整模式
# SYMBOLS = ["BTC", "ETH", "SOL"]
# 旧的静态映射仅作为兜底（5分钟数据）
DATA_FILES = {
    "BTC": "BTC_USDT_5m_20180101_to_20251018.csv",
    "ETH": "ETH_USDT_5m_20180101_to_20251018.csv",
    "XRP": "XRP_USDT_5m_20180504_to_20251018.csv",
    "BNB": "BNB_USDT_5m_20180101_to_20251018.csv",
    "SOL": "SOL_USDT_5m_20200811_to_20251018.csv",
    "DOGE": "DOGE_USDT_5m_20190705_to_20251018.csv",
    "TRX": "TRX_USDT_5m_20180611_to_20251018.csv",
    "ADA": "ADA_USDT_5m_20180417_to_20251018.csv",
    "LINK": "LINK_USDT_5m_20190116_to_20251018.csv",
    "AVAX": "AVAX_USDT_5m_20200922_to_20251018.csv",
    "DOT": "DOT_USDT_5m_20200818_to_20251018.csv",
    "MATIC": "MATIC_USDT_5m_20190426_to_20251018.csv",
}
# 数据目录（优先从 main_5m/ 使用5分钟数据）
DATA_DIR = "main_5m"
# USDT-M 永续合约符号映射（资金费率接口用）。例如 SHIB 的期货合约为 1000SHIB。
FUT_PERP_SYMBOL_MAP = {
    "SHIB": "1000SHIB",
}

# 单币止损比例
STOP_LOSS_PERCENTAGE = 0.05

import glob

def get_data_file(symbol: str) -> str | None:
    """Return data file path for symbol.
    优先在 DATA_DIR 中寻找最新文件；否则退回静态映射或当前目录。
    文件命名应为 {SYMBOL}_USDT_5m_YYYYMMDD_to_YYYYMMDD.csv
    """
    # 1) 优先 main_5m 目录
    candidates = []
    for pat in (os.path.join(DATA_DIR, f"{symbol}_USDT_5m_*.csv"), os.path.join(DATA_DIR, f"{symbol}_USDT_5m_*.CSV")):
        candidates.extend(glob.glob(pat))
    if candidates:
        candidates.sort()
        return candidates[-1]
    # 2) 退回静态映射
    p = DATA_FILES.get(symbol)
    if p and os.path.exists(p):
        return p
    # 3) 最后在当前目录搜索
    candidates = []
    for pat in (f"{symbol}_USDT_5m_*.csv", f"{symbol}_USDT_5m_*.CSV"):
        candidates.extend(glob.glob(pat))
    if candidates:
        candidates.sort()
        return candidates[-1]
    return None


# 时间配置
DT_COL = "datetime"
N_HORIZON = 5  # 预测未来2小时后的收益率（5分钟 * 24 = 2小时）

# 滚动回测周期配置
# 选项1: 6个月周期（8个周期，每个6个月）- 默认
# 选项2: 3个月周期（16个周期，每个3个月，验证期依然是6个月）
USE_3MONTH_PERIOD = True  # 设置为True使用3个月周期

BACKTEST_PERIODS = []
start_date = datetime(2022, 1, 1)

if USE_3MONTH_PERIOD:
    # 3个月周期：每3个月更新一次模型，但验证期依然是交易前6个月
    for i in range(16):
        test_start = start_date + timedelta(days=i*90)
        test_end = test_start + timedelta(days=89)  # 3个月
        val_start = test_start - timedelta(days=180)  # 验证集：测试前6个月
        val_end = test_start - timedelta(days=1)

        BACKTEST_PERIODS.append({
            "period": i + 1,
            "train_end": val_start - timedelta(days=1),
            "val_start": val_start,
            "val_end": val_end,
            "test_start": test_start,
            "test_end": test_end,
        })
else:
    # 6个月周期（默认）
    for i in range(8):
        test_start = start_date + timedelta(days=i*180)
        test_end = test_start + timedelta(days=179)  # 6个月
        val_start = test_start - timedelta(days=180)  # 验证集：测试前6个月
        val_end = test_start - timedelta(days=1)

        BACKTEST_PERIODS.append({
            "period": i + 1,
            "train_end": val_start - timedelta(days=1),
            "val_start": val_start,
            "val_end": val_end,
            "test_start": test_start,
            "test_end": test_end,
        })

# 特征预处理
WINSOR_LO = 0.0001
WINSOR_HI = 0.9999

# 时间权重配置
USE_TIME_WEIGHTS = True  # 是否启用时间权重
TIME_WEIGHT_METHOD = "linear"  # 权重方法: "exponential", "linear", "sqrt"
TIME_WEIGHT_DECAY = 0.99  # 指数衰减因子（仅用于exponential方法）
TIME_WEIGHT_MIN = 0.5  # 最小权重，防止早期数据权重过低
TIME_WEIGHT_MAX = 1.5  # 最大权重，防止最新数据权重过高

# 交易限制配置
MAX_TRADES_PER_PERIOD = 1000  # 每个周期最大交易次数

# 模型共享配置：True=每周期训练一个全市场共享模型；False=每币种单独训练
USE_SAME_MODEL = True

# 回归阈值配置（基于分位数）
REG_LONG_QUANTILE = 0.998   # 回归做多分位数阈值（开仓）
REG_SHORT_QUANTILE = 0.002  # 回归做空分位数阈值（开仓）
REG_EXIT_LONG_QUANTILE = 0.95   # 回归平多仓分位数阈值（关仓）
REG_EXIT_SHORT_QUANTILE = 0.05  # 回归平空仓分位数阈值（关仓）

# 缓存目录（复用5分钟因子缓存）
CACHE_DIR = "cache_5m"
RESULTS_DIR = "rolling_results_5m_filtered_factors"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# 因子存储格式：使用 Parquet 格式加速 I/O
FACTOR_FORMAT = "parquet"  # "parquet" 或 "csv"

# 模型保存目录（LightGBM专用）
MODELS_DIR = "trained_models_5m_filtered_factors"
os.makedirs(MODELS_DIR, exist_ok=True)

# 训练曲线保存目录
TRAINING_CURVES_DIR = os.path.join(RESULTS_DIR, "training_curves")
os.makedirs(TRAINING_CURVES_DIR, exist_ok=True)



# 全局交易记录列表
ALL_TRADES = []

def clear_all_trades():
    """清空全局交易记录列表"""
    global ALL_TRADES
    ALL_TRADES = []

# ============================
# 辅助函数（复用原有函数）
# ============================

def read_data(path: str, dt_col: str = DT_COL) -> pd.DataFrame:
    """读取CSV并整理列与索引"""
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    if dt_col.lower() not in df.columns:
        raise ValueError(f"未找到时间列: {dt_col}")
    df[dt_col.lower()] = pd.to_datetime(df[dt_col.lower()])
    df = df.sort_values(dt_col.lower()).reset_index(drop=True)
    df = df.set_index(dt_col.lower())
    return df

def compute_all_indicators(df_ohlcv: pd.DataFrame) -> pd.DataFrame:
    """使用pandas_ta计算所有可用技术指标"""
    df = df_ohlcv.copy()
    df["adj_close"] = df["close"].astype(float)

    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"缺少必要列: {col}")
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 因果安全的技术指标集合
    # 禁用 pandas_ta 在 macOS 下的多进程以避免 spawn/<stdin> 问题
    try:
        df.ta.cores = 0  # 0 = no multiprocessing
    except Exception:
        pass

    # 重要：禁用 pandas_ta 对 TA-Lib 的依赖，避免多进程环境下参数传递冲突
    # pandas_ta 会检测到 TA-Lib 并优先使用，但在 joblib Parallel 环境下会出现参数错误
    import pandas_ta as _ta
    _ta.Imports["talib"] = False  # 强制 pandas_ta 使用自己的实现而不是 TA-Lib
    causal_strategy = ta.Study(
        name="CausalOnly_5m",
        ta=[
            # 均线/趋势类（周期 × 12 以保持相同时间跨度，5分钟是1小时的1/12）
            {"kind": "ema", "length": 120}, {"kind": "ema", "length": 240}, {"kind": "ema", "length": 600},
            {"kind": "sma", "length": 120}, {"kind": "sma", "length": 240}, {"kind": "sma", "length": 600},
            {"kind": "wma", "length": 240}, {"kind": "wma", "length": 600}, {"kind": "wma", "length": 1200},
            {"kind": "dema", "length": 240}, {"kind": "dema", "length": 720},
            {"kind": "tema", "length": 240}, {"kind": "tema", "length": 720},
            {"kind": "kama", "length": 360}, {"kind": "kama", "length": 720}, {"kind": "kama", "length": 1200},
            {"kind": "trix", "length": 360}, {"kind": "trix", "length": 720},
            {"kind": "vwap"},
            # 动量/摆动类（周期 × 12）
            {"kind": "rsi", "length": 84}, {"kind": "rsi", "length": 168}, {"kind": "rsi", "length": 336}, {"kind": "rsi", "length": 672},
            {"kind": "stoch", "k": 168, "d": 36, "smooth_k": 36}, {"kind": "stoch", "k": 336, "d": 60, "smooth_k": 60},
            {"kind": "tsi", "long": 300, "short": 156}, {"kind": "tsi", "long": 600, "short": 300},
            {"kind": "ppo", "fast": 144, "slow": 312, "signal": 108}, {"kind": "pvo", "fast": 144, "slow": 312, "signal": 108},
            {"kind": "roc", "length": 144}, {"kind": "roc", "length": 288}, {"kind": "roc", "length": 576}, {"kind": "roc", "length": 1152}, {"kind": "roc", "length": 1400},
            # 波动率/通道类（周期 × 12）
            {"kind": "atr", "length": 168}, {"kind": "atr", "length": 336}, {"kind": "atr", "length": 672}, {"kind": "atr", "length": 1200},
            {"kind": "bbands", "length": 240, "std": 2},
            {"kind": "kc", "length": 240, "scalar": 1.5}, {"kind": "kc", "length": 240, "scalar": 2.0},
            {"kind": "kc", "length": 480, "scalar": 1.5}, {"kind": "kc", "length": 480, "scalar": 2.0},
            # 趋势强度/方向性（周期 × 12）
            {"kind": "adx", "length": 168}, {"kind": "adx", "length": 240}, {"kind": "adx", "length": 360}, {"kind": "adx", "length": 672},
            # 量能/资金流（周期 × 12）
            # {"kind": "obv"},
            {"kind": "cmf", "length": 240}, {"kind": "cmf", "length": 480}, {"kind": "cmf", "length": 960},
            {"kind": "mfi", "length": 168}, {"kind": "mfi", "length": 336}, {"kind": "mfi", "length": 672},
            # 其他（周期 × 12）
            {"kind": "cci", "length": 240}, {"kind": "willr", "length": 168},

            # 新增：5分钟级别短期因子（捕捉高频特征）
            # 超短期动量（5分钟、10分钟、15分钟、30分钟、1小时）
            {"kind": "roc", "length": 1}, {"kind": "roc", "length": 2}, {"kind": "roc", "length": 3}, {"kind": "roc", "length": 6}, {"kind": "roc", "length": 12},
            {"kind": "rsi", "length": 6}, {"kind": "rsi", "length": 12}, {"kind": "rsi", "length": 24}, {"kind": "rsi", "length": 48},
            # 短期移动平均（5分钟到2小时）
            {"kind": "ema", "length": 6}, {"kind": "ema", "length": 12}, {"kind": "ema", "length": 24}, {"kind": "ema", "length": 48},
            {"kind": "sma", "length": 6}, {"kind": "sma", "length": 12}, {"kind": "sma", "length": 24}, {"kind": "sma", "length": 48},
            # 短期波动率
            {"kind": "atr", "length": 6}, {"kind": "atr", "length": 12}, {"kind": "atr", "length": 24}, {"kind": "atr", "length": 48},
            {"kind": "bbands", "length": 24, "std": 2}, {"kind": "bbands", "length": 48, "std": 2}, {"kind": "bbands", "length": 96, "std": 2},
            # 中期因子（2-6小时）
            {"kind": "ema", "length": 72}, {"kind": "sma", "length": 72},
            {"kind": "rsi", "length": 72}, {"kind": "atr", "length": 72},


            # ============ 超短期因子（5-30分钟级别，完全无重合）============
            # 1. 超短期RSI（5-30分钟）- 去除length=6
            {"kind": "rsi", "length": 1},   # 5分钟RSI
            {"kind": "rsi", "length": 2},   # 10分钟RSI
            {"kind": "rsi", "length": 3},   # 15分钟RSI
            {"kind": "rsi", "length": 4},   # 20分钟RSI
            {"kind": "rsi", "length": 5},   # 25分钟RSI

            # 2. 超短期Stochastic（5-30分钟）
            {"kind": "stoch", "k": 3, "d": 2, "smooth_k": 2},   # 15分钟KD
            {"kind": "stoch", "k": 6, "d": 3, "smooth_k": 2},   # 30分钟KD

            # 3. 超短期Williams %R（5-30分钟）
            {"kind": "willr", "length": 3},   # 15分钟
            {"kind": "willr", "length": 6},   # 30分钟

            # 4. 超短期CCI（5-30分钟）
            {"kind": "cci", "length": 3},   # 15分钟
            {"kind": "cci", "length": 6},   # 30分钟

            # 5. 超短期MACD（5-30分钟）
            {"kind": "macd", "fast": 3, "slow": 6, "signal": 2},   # 15分钟/30分钟/10分钟
            {"kind": "macd", "fast": 4, "slow": 8, "signal": 3},   # 20分钟/40分钟/15分钟

            # 6. 超短期布林带（5-30分钟）
            {"kind": "bbands", "length": 3, "std": 2},   # 15分钟
            {"kind": "bbands", "length": 6, "std": 2},   # 30分钟
            {"kind": "bbands", "length": 6, "std": 1.5}, # 30分钟，1.5倍std

            # 7. 超短期Keltner通道（5-30分钟）
            {"kind": "kc", "length": 3, "scalar": 1.5},   # 15分钟
            {"kind": "kc", "length": 6, "scalar": 1.5},   # 30分钟
            {"kind": "kc", "length": 6, "scalar": 2.0},   # 30分钟，2倍ATR

            # 8. 超短期ATR（5-30分钟）- 去除length=6
            {"kind": "atr", "length": 1},   # 5分钟
            {"kind": "atr", "length": 2},   # 10分钟
            {"kind": "atr", "length": 3},   # 15分钟
            {"kind": "atr", "length": 4},   # 20分钟
            {"kind": "atr", "length": 5},   # 25分钟

            # 9. 超短期ADX（5-30分钟）
            {"kind": "adx", "length": 3},   # 15分钟
            {"kind": "adx", "length": 6},   # 30分钟

            # 10. 超短期MFI（5-30分钟）
            {"kind": "mfi", "length": 3},   # 15分钟
            {"kind": "mfi", "length": 6},   # 30分钟

            # 11. 超短期CMF（5-30分钟）
            {"kind": "cmf", "length": 3},   # 15分钟
            {"kind": "cmf", "length": 6},   # 30分钟

            # 12. 超短期Fisher Transform（5-30分钟）
            {"kind": "fisher", "length": 3},   # 15分钟
            {"kind": "fisher", "length": 6},   # 30分钟

            # 13. 超短期Aroon（5-30分钟）
            {"kind": "aroon", "length": 3},   # 15分钟
            {"kind": "aroon", "length": 6},   # 30分钟

            # 14. 超短期Choppiness Index（5-30分钟）
            {"kind": "chop", "length": 3},   # 15分钟
            {"kind": "chop", "length": 6},   # 30分钟

            # 15. 超短期线性回归（5-30分钟）
            {"kind": "linreg", "length": 3},   # 15分钟
            {"kind": "linreg", "length": 6},   # 30分钟

            # 16. 超短期TSI（5-30分钟）
            {"kind": "tsi", "long": 6, "short": 3},   # 30分钟/15分钟

            # 17. 超短期PPO（5-30分钟）
            {"kind": "ppo", "fast": 3, "slow": 6, "signal": 2},   # 15分钟/30分钟/10分钟

            # 18. 超短期PVO（5-30分钟）
            {"kind": "pvo", "fast": 3, "slow": 6, "signal": 2},   # 15分钟/30分钟/10分钟

            # 19. 超短期Vortex Indicator（5-30分钟）
            {"kind": "vortex", "length": 3},   # 15分钟
            {"kind": "vortex", "length": 6},   # 30分钟

            # 20. 超短期UO（5-30分钟）
            {"kind": "uo", "fast": 2, "medium": 4, "slow": 6},   # 10分钟/20分钟/30分钟

            # 21. 超短期动量指标（5-30分钟）
            {"kind": "mom", "length": 1},   # 5分钟动量
            {"kind": "mom", "length": 2},   # 10分钟动量
            {"kind": "mom", "length": 3},   # 15分钟动量
            {"kind": "mom", "length": 6},   # 30分钟动量

            # 22. 超短期TEMA（5-30分钟）
            {"kind": "tema", "length": 3},   # 15分钟
            {"kind": "tema", "length": 6},   # 30分钟

            # 23. 超短期DEMA（5-30分钟）
            {"kind": "dema", "length": 3},   # 15分钟
            {"kind": "dema", "length": 6},   # 30分钟

            # 24. 超短期KAMA（5-30分钟）
            {"kind": "kama", "length": 3},   # 15分钟
            {"kind": "kama", "length": 6},   # 30分钟
        ],
    )
    # 在部分 macOS 环境下，pandas_ta 的多进程可能引发 spawn/<stdin> 问题
    # 这里加入一次回退：若首次执行失败，尝试禁用并串行重试
    try:
        df.ta.study(causal_strategy)
    except Exception as e:
        print(f"[warn] pandas_ta.strategy 出错，尝试禁用多进程后重试: {e}")
        try:
            import pandas_ta as _ta  # 避免在函数作用域内重绑定全局 ta
            try:
                _ta.cores = 0  # 禁用 multiprocessing
            except Exception:
                pass
            df.ta.study(causal_strategy)
        except Exception as e2:
            # 若仍失败，直接抛出以便上层感知
            raise

    # 将正负无穷转为NaN
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    # 时间截面前向填充，保留 NaN 让 XGBoost 处理
    # 修改：移除 dropna()，让 XGBoost 的 tree_method='hist' 原生处理 NaN
    df = df.ffill()
    return df


def compute_all_features(df_ohlcv: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """计算所有技术指标特征 + 附加因子"""
    # 第一步：计算原有的技术指标
    merged = compute_all_indicators(df_ohlcv)

    # 第二步：计算附加因子（来自additional_features模块）
    # 如果模块可用，直接在 merged 上计算，确保索引完全对齐
    if HAS_ADDITIONAL_FEATURES:
        merged = additional_features.compute_safe_additional_factors(merged)
        print(f"[{symbol}] 合并后特征数: {len(merged.columns)} (包含附加因子)")
    else:
        print(f"[{symbol}] 特征数: {len(merged.columns)} (仅pandas_ta技术指标)")

    merged = merged.replace([np.inf, -np.inf], np.nan)
    # 丢弃整列均为 NaN 的特征，防止少数衍生/宏观列为空导致整表被 drop 掉
    merged = merged.dropna(axis=1, how="all")
    # 前向填充，保留 NaN 让 XGBoost 处理
    # 修改：移除 dropna()，让 XGBoost 的 tree_method='hist' 原生处理 NaN
    merged = merged.ffill()
    return merged

def make_label_regression(df: pd.DataFrame, n: int) -> pd.Series:
    """根据 n 步未来收盘价生成回归标签（未来收益率）"""
    future = df["close"].shift(-n)
    label = (future - df["close"]) / df["close"]  # 未来收益率
    return label


def time_split_mask(index: pd.DatetimeIndex, start: str, end: str) -> np.ndarray:
    start_ts = pd.to_datetime(start)
    end_ts = pd.to_datetime(end)
    return (index >= start_ts) & (index <= end_ts)

def purge_by_horizon(idx: pd.DatetimeIndex, mask: np.ndarray, n: int) -> np.ndarray:
    """避免跨分割边界的标签泄漏"""
    s = pd.Series(mask.astype(bool), index=idx)
    purged = (s & s.shift(-n).fillna(False)).values
    return purged

def winsorize_by_train_quantiles(X: pd.DataFrame, train_mask: np.ndarray, lo: float, hi: float) -> Tuple[pd.DataFrame, pd.Series, pd.Series]:
    """基于训练集分位数对特征进行截尾"""
    X = X.copy()
    X_train = X.loc[train_mask]
    q_low = X_train.quantile(lo)
    q_high = X_train.quantile(hi)
    X = X.clip(lower=q_low, upper=q_high, axis=1)
    return X, q_low, q_high


def filter_selected_factors(X: pd.DataFrame) -> pd.DataFrame:
    """筛选出符合条件的因子列"""
    # 找到X中存在的筛选因子
    available_factors = [f for f in SELECTED_FACTORS if f in X.columns]

    # 同时保留所有的基础技术指标列（pandas_ta生成的）
    # 这些列名通常包含特定的模式
    ta_patterns = ['RSI_', 'STOCH', 'WILLR_', 'UO_', 'CMF_', 'MFI_', 'ROC_', 'TSI_', 'PPO_', 'VORTEX']
    ta_cols = [c for c in X.columns if any(p in c.upper() for p in ta_patterns)]

    # 合并筛选因子和技术指标列
    all_selected = list(set(available_factors + ta_cols))

    print(f"筛选因子数: {len(available_factors)}/{len(SELECTED_FACTORS)} (可用/目标)")
    print(f"技术指标列数: {len(ta_cols)}")
    print(f"总选择特征数: {len(all_selected)}")

    if len(all_selected) == 0:
        print(f"警告：没有找到任何筛选因子，返回所有列")
        return X

    return X[all_selected]


def build_feature_matrix(df_all: pd.DataFrame, n: int) -> Tuple[pd.DataFrame, pd.Series]:
    """从包含OHLCV+指标的df中产出特征矩阵X与标签y（回归）"""
    y = make_label_regression(df_all, n)

    # 丢弃未来不可见的最后n行
    valid_mask = y.notna()
    df_all = df_all.loc[valid_mask]
    y = y.loc[valid_mask]

    # 仅保留指标列作为特征
    drop_cols = {"open", "high", "low", "close", "volume", "timestamp", "adj_close"}
    feat_cols = [c for c in df_all.columns if c not in drop_cols]
    X = df_all[feat_cols].select_dtypes(include=[np.number]).copy()

    # 筛选因子 - 关键修改点
    X = filter_selected_factors(X)

    y = y.loc[X.index]
    return X, y

def auto_threshold_quantile(scores: np.ndarray, long_quantile: float = 0.97, short_quantile: float = 0.03) -> Tuple[float, float]:
    """基于验证集分布的指定分位数确定阈值"""
    if scores is None or len(scores) == 0:
        return np.inf, -np.inf
    thr_long = float(np.quantile(scores, long_quantile))
    thr_short = float(np.quantile(scores, short_quantile))
    return thr_long, thr_short

def calculate_time_weights(index: pd.DatetimeIndex, method: str = TIME_WEIGHT_METHOD,
                          decay_factor: float = TIME_WEIGHT_DECAY,
                          min_weight: float = TIME_WEIGHT_MIN,
                          max_weight: float = TIME_WEIGHT_MAX) -> np.ndarray:
    """
    计算时间权重：越接近最新时间的样本权重越高
    """
    if len(index) == 0:
        return np.array([])

    # 计算时间位置（0到1之间，0为最早，1为最新）
    latest_time = index.max()
    earliest_time = index.min()
    time_span = (latest_time - earliest_time).total_seconds()

    if time_span == 0:
        return np.ones(len(index))

    time_positions = np.array((index - earliest_time).total_seconds()) / time_span

    if method == "exponential":
        weights = decay_factor ** (1 - time_positions)
    elif method == "linear":
        weights = min_weight + (max_weight - min_weight) * time_positions
    elif method == "sqrt":
        weights = min_weight + (max_weight - min_weight) * np.sqrt(time_positions)
    else:
        raise ValueError(f"不支持的权重方法: {method}")

    weights = np.clip(weights, min_weight, max_weight)
    weights = np.array(weights)
    weights = weights / weights.mean()

    return weights


def train_lgb_reg(X_train: pd.DataFrame, y_train: pd.Series, X_val: pd.DataFrame, y_val: pd.Series,
                  sample_weight: np.ndarray = None):
    """训练LightGBM回归器（支持GPU加速）"""

    params = {
        'objective': 'regression',
        'metric': ['rmse', 'mae'],
        'boosting_type': 'gbdt',
        'num_leaves': 127,
        'learning_rate': 0.02,
        'feature_fraction': 0.7,
        'bagging_fraction': 0.7,
        'bagging_freq': 1,
        'min_child_samples': 20,
        'lambda_l1': 0.0,
        'lambda_l2': 1.0,
        'num_threads': N_JOBS,
        'verbosity': -1,
        'seed': RANDOM_STATE,
        'device': 'cpu',
    }

    train_data = lgb.Dataset(X_train, label=y_train, weight=sample_weight)
    val_data = lgb.Dataset(X_val, label=y_val, reference=train_data)

    model = lgb.train(
        params,
        train_data,
        num_boost_round=400,
        valid_sets=[train_data, val_data],
        valid_names=['train', 'valid'],
        callbacks=[
            lgb.early_stopping(stopping_rounds=30, verbose=False),
            lgb.log_evaluation(period=0)
        ]
    )

    return model

def plot_training_curves(model, period_no: int, save_dir: str = TRAINING_CURVES_DIR):
    """绘制并保存训练曲线（RMSE和MAE）- LightGBM版本"""
    try:
        evals_result = model.evals_result_

        train_key = 'train'
        val_key = 'valid'

        fig, axes = plt.subplots(1, 2, figsize=(14, 5))

        if 'rmse' in evals_result[train_key]:
            train_rmse = evals_result[train_key]['rmse']
            val_rmse = evals_result[val_key]['rmse']

            axes[0].plot(train_rmse, label='Train RMSE', linewidth=2, alpha=0.8)
            axes[0].plot(val_rmse, label='Val RMSE', linewidth=2, alpha=0.8)
            axes[0].set_xlabel('Iteration', fontsize=11)
            axes[0].set_ylabel('RMSE', fontsize=11)
            axes[0].set_title(f'Period {period_no} - RMSE Training Curve', fontsize=12, fontweight='bold')
            axes[0].legend(fontsize=10)
            axes[0].grid(True, alpha=0.3)

            final_train_rmse = train_rmse[-1]
            final_val_rmse = val_rmse[-1]
            axes[0].text(0.98, 0.98, f'Final Train: {final_train_rmse:.6f}\nFinal Val: {final_val_rmse:.6f}',
                        transform=axes[0].transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        if 'mae' in evals_result[train_key]:
            train_mae = evals_result[train_key]['mae']
            val_mae = evals_result[val_key]['mae']

            axes[1].plot(train_mae, label='Train MAE', linewidth=2, alpha=0.8)
            axes[1].plot(val_mae, label='Val MAE', linewidth=2, alpha=0.8)
            axes[1].set_xlabel('Iteration', fontsize=11)
            axes[1].set_ylabel('MAE', fontsize=11)
            axes[1].set_title(f'Period {period_no} - MAE Training Curve', fontsize=12, fontweight='bold')
            axes[1].legend(fontsize=10)
            axes[1].grid(True, alpha=0.3)

            final_train_mae = train_mae[-1]
            final_val_mae = val_mae[-1]
            axes[1].text(0.98, 0.98, f'Final Train: {final_train_mae:.6f}\nFinal Val: {final_val_mae:.6f}',
                        transform=axes[1].transAxes, fontsize=9,
                        verticalalignment='top', horizontalalignment='right',
                        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        save_path = os.path.join(save_dir, f"period_{period_no}_training_curves.png")
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        print(f"训练曲线已保存: {save_path}")
        return save_path

    except Exception as e:
        print(f"绘制训练曲线失败: {e}")
        return None

def print_regression_metrics(y_true: pd.Series, y_pred: np.ndarray, dataset_name: str = "Dataset"):
    """打印回归指标和预测值分布统计（包括方向准确率）"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    corr = np.corrcoef(y_true, y_pred)[0, 1]

    y_true_direction = np.sign(y_true)
    y_pred_direction = np.sign(y_pred)
    direction_accuracy = accuracy_score(y_true_direction, y_pred_direction)

    non_zero_mask = y_true_direction != 0
    if non_zero_mask.sum() > 0:
        direction_accuracy_nonzero = accuracy_score(
            y_true_direction[non_zero_mask],
            y_pred_direction[non_zero_mask]
        )
    else:
        direction_accuracy_nonzero = np.nan

    pred_min = np.min(y_pred)
    pred_max = np.max(y_pred)
    pred_mean = np.mean(y_pred)
    pred_std = np.std(y_pred)
    pred_q25 = np.quantile(y_pred, 0.25)
    pred_q50 = np.quantile(y_pred, 0.50)
    pred_q75 = np.quantile(y_pred, 0.75)

    print(f"\n{dataset_name} 指标:")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  MAE: {mae:.6f}")
    print(f"  R²: {r2:.6f}")
    print(f"  相关系数: {corr:.6f}")
    print(f"  方向准确率（全部）: {direction_accuracy:.4f} ({direction_accuracy*100:.2f}%)")
    print(f"  方向准确率（非零）: {direction_accuracy_nonzero:.4f} ({direction_accuracy_nonzero*100:.2f}%)")
    print(f"  预测值分布: min={pred_min:.6f}, max={pred_max:.6f}, mean={pred_mean:.6f}, std={pred_std:.6f}")
    print(f"  预测值分位数: Q25={pred_q25:.6f}, Q50={pred_q50:.6f}, Q75={pred_q75:.6f}")

    return {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'corr': corr,
        'direction_accuracy': direction_accuracy,
        'direction_accuracy_nonzero': direction_accuracy_nonzero,
    }

def reg_signal_backtest(reg_pred: pd.Series, px_open: pd.Series,
                        px_high: pd.Series, px_low: pd.Series,
                        n_hold: int, reg_long_thr: float, reg_short_thr: float,
                        reg_exit_long_thr: float = None, reg_exit_short_thr: float = None,
                        max_trades: int = None, stop_loss_pct: float = STOP_LOSS_PERCENTAGE) -> Tuple[pd.Series, pd.DataFrame]:
    """
    回归信号回测：基于回归预测值的阈值进行开仓和平仓。
    """
    common_idx = reg_pred.index.intersection(px_open.index).intersection(px_high.index).intersection(px_low.index)
    reg_pred = reg_pred.loc[common_idx]
    px_open = px_open.loc[common_idx]
    px_high = px_high.loc[common_idx]
    px_low = px_low.loc[common_idx]

    idx = px_open.index
    ret = pd.Series(0.0, index=idx)
    trades = []

    if max_trades is None:
        max_trades = float('inf')

    i = 0
    n = len(idx)
    trade_count = 0

    while i < n - 1 and trade_count < max_trades:
        t = idx[i]
        reg_val = float(reg_pred.iat[i])

        if reg_val >= reg_long_thr:
            side = 1
        elif reg_val <= reg_short_thr:
            side = -1
        else:
            i += 1
            continue

        entry_idx = i + 1
        if entry_idx >= n:
            break
        entry_price = float(px_open.iat[entry_idx])

        exit_idx = None
        exit_price = None
        hit_sl = False
        exit_reason = None

        for k in range(entry_idx, n):
            if side == 1:
                stop_price = entry_price * (1.0 - stop_loss_pct)
                if float(px_low.iat[k]) <= stop_price:
                    exit_idx = k
                    exit_price = stop_price
                    hit_sl = True
                    exit_reason = "stop_loss"
                    break
            else:
                stop_price = entry_price * (1.0 + stop_loss_pct)
                if float(px_high.iat[k]) >= stop_price:
                    exit_idx = k
                    exit_price = stop_price
                    hit_sl = True
                    exit_reason = "stop_loss"
                    break

            if k > entry_idx:
                reg_val_k = float(reg_pred.iat[k])
                if side == 1 and reg_exit_long_thr is not None:
                    if reg_val_k <= reg_exit_long_thr:
                        exit_idx = k + 1 if k + 1 < n else k
                        exit_price = float(px_open.iat[exit_idx])
                        exit_reason = "signal_exit"
                        break
                elif side == -1 and reg_exit_short_thr is not None:
                    if reg_val_k >= reg_exit_short_thr:
                        exit_idx = k + 1 if k + 1 < n else k
                        exit_price = float(px_open.iat[exit_idx])
                        exit_reason = "signal_exit"
                        break

        if exit_idx is None:
            exit_idx = n - 1
            exit_price = float(px_open.iat[exit_idx])
            exit_reason = "end_of_data"

        if exit_idx > entry_idx:
            if side == 1:
                period_rets = px_open.pct_change().iloc[entry_idx:exit_idx].fillna(0.0)
            else:
                period_rets = -px_open.pct_change().iloc[entry_idx:exit_idx].fillna(0.0)
            ret.iloc[entry_idx:exit_idx] = period_rets.values

        if side == 1:
            trade_r = (exit_price - entry_price) / entry_price
        else:
            trade_r = (entry_price - exit_price) / entry_price

        trade_record = {
            "signal_time": t,
            "entry_time": idx[entry_idx],
            "exit_time": idx[exit_idx],
            "side": "LONG" if side == 1 else "SHORT",
            "side_flag": side,
            "entry_idx": entry_idx,
            "exit_idx": exit_idx,
            "entry_price": entry_price,
            "exit_price": exit_price,
            "trade_return": float(trade_r),
            "reg_signal": float(reg_val),
            "hit_sl": int(hit_sl),
            "sl_pct": float(stop_loss_pct),
            "exit_reason": exit_reason,
        }
        trades.append(trade_record)

        trade_count += 1
        i = exit_idx

    trades_df = pd.DataFrame(trades)
    return ret, trades_df

def calculate_metrics(returns: pd.Series, trades: pd.DataFrame) -> dict:
    """计算回测指标"""
    if len(trades) > 0:
        trade_returns = trades['trade_return'].values
        total_ret = float(np.prod(1 + trade_returns) - 1)
    else:
        total_ret = 0.0

    num_trades = len(trades)

    return {
        "total_return": total_ret,
        "num_trades": num_trades,
    }

def _process_single_symbol_features(symbol: str, period_config: dict) -> dict:
    """并行处理单个币种的特征计算（辅助函数）"""
    data_file = get_data_file(symbol)
    if not data_file or not os.path.exists(data_file):
        return {'symbol': symbol, 'error': f'数据文件不存在: {data_file}'}

    df0 = read_data(data_file, DT_COL)
    cache_file = os.path.join(CACHE_DIR, f"features_plus_{symbol}_rolling_5m.parquet")

    if not os.path.exists(cache_file):
        df_all = compute_all_features(df0, symbol)
        df_all.to_parquet(cache_file, index=True)
    else:
        df_all = pd.read_parquet(cache_file)
        obsolete_cols = {"funding_rate", "funding_rate_chg", "open_interest", "open_interest_chg", "premium", "premium_chg",
                         "agg_volume", "agg_trade_count", "agg_vwap", "agg_buy_ratio", "agg_imbalance",
                         "fr_ma_8", "fr_ma_24", "fr_vol_24", "fr_z_24", "fr_z_72", "fr_raw", "fr_abs", "fr_pos"}
        has_obsolete = len(obsolete_cols & set(df_all.columns)) > 0
        if has_obsolete:
            df_all = compute_all_features(df0, symbol)
            df_all.to_parquet(cache_file, index=True)

    X, y = build_feature_matrix(df_all, N_HORIZON)
    idx = X.index
    train_end_str = period_config['train_end'].strftime('%Y-%m-%d %H:%M:%S')
    val_start_str = period_config['val_start'].strftime('%Y-%m-%d %H:%M:%S')
    val_end_str = period_config['val_end'].strftime('%Y-%m-%d %H:%M:%S')
    test_start_str = period_config['test_start'].strftime('%Y-%m-%d %H:%M:%S')
    test_end_str = period_config['test_end'].strftime('%Y-%m-%d %H:%M:%S')

    m_train0 = idx <= pd.to_datetime(train_end_str)
    m_val0 = time_split_mask(idx, val_start_str, val_end_str)
    m_test0 = time_split_mask(idx, test_start_str, test_end_str)
    m_train = purge_by_horizon(idx, m_train0, N_HORIZON)
    m_val = purge_by_horizon(idx, m_val0, N_HORIZON)
    m_test = purge_by_horizon(idx, m_test0, N_HORIZON)

    if m_val.sum() < 100 or m_test.sum() < 100:
        return {'symbol': symbol, 'skip': True, 'val_count': m_val.sum(), 'test_count': m_test.sum()}

    return {
        'symbol': symbol,
        'df0': df0,
        'X': X,
        'y': y,
        'm_train': m_train,
        'm_val': m_val,
        'm_test': m_test,
        'test_start': test_start_str,
        'test_end': test_end_str,
        'train_count': int(m_train.sum()),
        'val_count': int(m_val.sum()),
    }


def run_period_with_shared_model(period_config: dict, use_time_weights: bool = None,
                                 weight_method: str = None) -> Tuple[List[dict], dict]:
    """使用全市场共享回归模型在单个周期进行训练与预测，返回每个币种的回测结果列表。"""
    period_no = period_config['period']
    print(f"\n[Shared-Model-Regression-FilteredFactors] 周期 {period_no} {period_config['test_start']} -> {period_config['test_end']}")

    print(f"并行处理 {len(SYMBOLS)} 个币种的特征计算（{N_PARALLEL_SYMBOLS} 并发）...")
    results = Parallel(n_jobs=N_PARALLEL_SYMBOLS, verbose=5)(
        delayed(_process_single_symbol_features)(symbol, period_config)
        for symbol in SYMBOLS
    )

    sym_data = {}
    common_cols = None
    total_train = 0
    total_val = 0

    for result in results:
        if 'error' in result:
            print(f"{result['symbol']} 数据文件不存在: {result.get('error', '')}")
            continue
        if result.get('skip'):
            print(f"  {result['symbol']}: 跳过（val={result['val_count']}, test={result['test_count']}）")
            continue

        symbol = result['symbol']
        X = result['X']

        if common_cols is None:
            common_cols = set(X.columns)
        else:
            common_cols &= set(X.columns)

        sym_data[symbol] = {
            'df0': result['df0'],
            'X': X,
            'y': result['y'],
            'm_train': result['m_train'],
            'm_val': result['m_val'],
            'm_test': result['m_test'],
            'test_start': result['test_start'],
            'test_end': result['test_end'],
        }
        total_train += result['train_count']
        total_val += result['val_count']

    if not sym_data or not common_cols:
        print("  共享模型：无可用符号或无共同特征列，跳过本周期")
        return [], {}

    common_cols = sorted(list(common_cols))
    print(f"共同特征列数: {len(common_cols)}")

    X_train_list = []
    y_train_list = []
    idx_train_list = []

    X_val_list = []
    y_val_list = []

    for sym, d in sym_data.items():
        Xc = d['X'][common_cols]
        X_train_list.append(Xc.loc[d['m_train']])
        y_train_list.append(d['y'].loc[d['m_train']])
        idx_train_list.append(Xc.loc[d['m_train']].index)

        X_val_list.append(Xc.loc[d['m_val']])
        y_val_list.append(d['y'].loc[d['m_val']])
        d['Xc'] = Xc

    if len(X_train_list) == 0:
        print("  共享模型：训练集为空，跳过本周期")
        return [], {}

    X_train_all = pd.concat(X_train_list, axis=0)
    y_train_all = pd.concat(y_train_list, axis=0)
    train_index_all = pd.DatetimeIndex(np.concatenate([ix.values for ix in idx_train_list]))

    X_val_all = pd.concat(X_val_list, axis=0)
    y_val_all = pd.concat(y_val_list, axis=0)

    for sym, d in sym_data.items():
        d['X_val_clip'] = d['Xc'].loc[d['m_val']]
        d['X_test_clip'] = d['Xc'].loc[d['m_test']]

    sample_weights = None
    use_weights = USE_TIME_WEIGHTS if use_time_weights is None else use_time_weights
    method = TIME_WEIGHT_METHOD if weight_method is None else weight_method
    if use_weights:
        sample_weights = calculate_time_weights(train_index_all, method=method)
        print(f"时间权重({method}): 最早样本权重={sample_weights.min():.4f}, 最新样本权重={sample_weights.max():.4f}, 平均权重={sample_weights.mean():.4f}")
    else:
        print("时间权重: 未启用")

    print(f"\n训练共享LightGBM回归模型（训练集={len(X_train_all)}，验证集={len(X_val_all)}）...")
    reg_model = train_lgb_reg(X_train_all, y_train_all, X_val_all, y_val_all, sample_weights)

    reg_pred_train = reg_model.predict(X_train_all, num_iteration=reg_model.best_iteration)
    reg_pred_val = reg_model.predict(X_val_all, num_iteration=reg_model.best_iteration)
    train_metrics = print_regression_metrics(y_train_all, reg_pred_train, "训练集")
    val_metrics = print_regression_metrics(y_val_all, reg_pred_val, "验证集")

    print(f"\n绘制训练曲线...")
    plot_training_curves(reg_model, period_no)

    test_start_str = period_config['test_start'].strftime('%Y-%m-%d %H:%M:%S')
    ref_start_str = (pd.to_datetime(test_start_str) - pd.Timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
    ref_end_str = (pd.to_datetime(test_start_str) - pd.Timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
    X_ref_list = []
    for sym, d in sym_data.items():
        idx_sym = d['Xc'].index
        m_ref0 = time_split_mask(idx_sym, ref_start_str, ref_end_str)
        m_ref = purge_by_horizon(idx_sym, m_ref0, N_HORIZON)
        X_ref_list.append(d['Xc'].loc[m_ref])
    X_ref_all = pd.concat([x for x in X_ref_list if len(x) > 0], axis=0) if any(len(x) > 0 for x in X_ref_list) else pd.DataFrame(columns=common_cols)
    if len(X_ref_all) > 0:
        reg_pred_ref_all = reg_model.predict(X_ref_all, num_iteration=reg_model.best_iteration)
    else:
        reg_pred_ref_all = reg_pred_val
    reg_long_thr, reg_short_thr = auto_threshold_quantile(reg_pred_ref_all, REG_LONG_QUANTILE, REG_SHORT_QUANTILE)
    reg_exit_long_thr, reg_exit_short_thr = auto_threshold_quantile(reg_pred_ref_all, REG_EXIT_LONG_QUANTILE, REG_EXIT_SHORT_QUANTILE)

    print(f"\n阈值信息（基于pre-test 1年数据）:")
    print(f"  开仓阈值: 做多>={reg_long_thr:.6f} (Q{REG_LONG_QUANTILE}), 做空<={reg_short_thr:.6f} (Q{REG_SHORT_QUANTILE})")
    print(f"  平仓阈值: 平多<={reg_exit_long_thr:.6f} (Q{REG_EXIT_LONG_QUANTILE}), 平空>={reg_exit_short_thr:.6f} (Q{REG_EXIT_SHORT_QUANTILE})")

    try:
        period_no = period_config['period']
        model_path = os.path.join(MODELS_DIR, f"period_{period_no}_shared_reg_5m.pkl")
        cfg_path = os.path.join(MODELS_DIR, f"period_{period_no}_shared_config_5m.json")
        joblib.dump(reg_model, model_path)
        cfg = {
            "period": int(period_no),
            "model_type": "regression",
            "shared": True,
            "symbols": SYMBOLS,
            "horizon_n": int(N_HORIZON),
            "feature_names": list(common_cols),
            "selected_factors": SELECTED_FACTORS,
            "reg_long_thr": float(reg_long_thr),
            "reg_short_thr": float(reg_short_thr),
            "reg_exit_long_thr": float(reg_exit_long_thr),
            "reg_exit_short_thr": float(reg_exit_short_thr),
            "train_end": period_config['train_end'].strftime('%Y-%m-%d %H:%M:%S'),
            "val_start": period_config['val_start'].strftime('%Y-%m-%d %H:%M:%S'),
            "val_end": period_config['val_end'].strftime('%Y-%m-%d %H:%M:%S'),
            "test_start": period_config['test_start'].strftime('%Y-%m-%d %H:%M:%S'),
            "test_end": period_config['test_end'].strftime('%Y-%m-%d %H:%M:%S'),
        }
        with open(cfg_path, "w") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
        print(f"已保存共享模型与配置: {model_path}, {cfg_path}")
    except Exception as e:
        print(f"保存共享模型失败: {e}")

    results = []
    test_metrics_list = []

    for symbol, d in sym_data.items():
        X_test_clip = d['X_test_clip']
        if X_test_clip.empty:
            continue
        reg_pred_test = pd.Series(reg_model.predict(X_test_clip, num_iteration=reg_model.best_iteration), index=X_test_clip.index)

        y_test_sym = d['y'].loc[d['m_test']]
        test_metrics = print_regression_metrics(y_test_sym, reg_pred_test.values, f"测试集 ({symbol})")
        test_metrics_list.append({
            'symbol': symbol,
            'period': period_no,
            **test_metrics
        })

        open_test = d['df0'].loc[X_test_clip.index, 'open']
        high_test = d['df0'].loc[X_test_clip.index, 'high']
        low_test = d['df0'].loc[X_test_clip.index, 'low']

        ret_test, trades = reg_signal_backtest(
            reg_pred_test,
            open_test, high_test, low_test,
            N_HORIZON,
            reg_long_thr, reg_short_thr,
            reg_exit_long_thr, reg_exit_short_thr,
            max_trades=MAX_TRADES_PER_PERIOD,
            stop_loss_pct=STOP_LOSS_PERCENTAGE
        )

        for tr in trades.itertuples():
            ALL_TRADES.append({
                'symbol': symbol,
                'period': period_no,
                'signal_time': tr.signal_time,
                'entry_time': tr.entry_time,
                'exit_time': tr.exit_time,
                'side': tr.side,
                'side_flag': tr.side_flag,
                'entry_price': tr.entry_price,
                'exit_price': tr.exit_price,
                'trade_return': tr.trade_return,
                'reg_signal': tr.reg_signal,
                'test_start': d['test_start'],
                'test_end': d['test_end'],
            })

        if not d['X_val_clip'].empty:
            reg_pred_val_sym = reg_model.predict(d['X_val_clip'])
            val_rmse = np.sqrt(mean_squared_error(d['y'].loc[d['m_val']], reg_pred_val_sym))
        else:
            val_rmse = np.nan

        metrics = calculate_metrics(ret_test, trades)
        results.append({
            'symbol': symbol,
            'period': period_no,
            'test_start': d['test_start'],
            'test_end': d['test_end'],
            'total_return': metrics['total_return'],
            'num_trades': metrics['num_trades'],
            'val_rmse': val_rmse,
            'train_samples': int(d['m_train'].sum()),
            'val_samples': int(d['m_val'].sum()),
            'test_samples': int(d['m_test'].sum()),
        })

    if test_metrics_list:
        test_metrics_df = pd.DataFrame(test_metrics_list)
        test_metrics_file = os.path.join(RESULTS_DIR, f"period_{period_no}_test_metrics.csv")
        test_metrics_df.to_csv(test_metrics_file, index=False)
        print(f"\n测试集指标已保存: {test_metrics_file}")

    period_training_metrics = {
        'period': period_no,
        'train_samples': len(X_train_all),
        'val_samples': len(X_val_all),
        'train_rmse': train_metrics['rmse'],
        'train_mae': train_metrics['mae'],
        'train_r2': train_metrics['r2'],
        'train_corr': train_metrics['corr'],
        'train_direction_acc': train_metrics['direction_accuracy'],
        'train_direction_acc_nonzero': train_metrics['direction_accuracy_nonzero'],
        'val_rmse': val_metrics['rmse'],
        'val_mae': val_metrics['mae'],
        'val_r2': val_metrics['r2'],
        'val_corr': val_metrics['corr'],
        'val_direction_acc': val_metrics['direction_accuracy'],
        'val_direction_acc_nonzero': val_metrics['direction_accuracy_nonzero'],
    }

    return results, period_training_metrics


def main():
    """主函数：运行所有币种单个周期的滚动回测（5分钟级别，回归模型，筛选因子）"""
    clear_all_trades()

    print("=" * 80)
    print("开始滚动回测（5分钟级别，LightGBM回归模型，筛选因子版本）...")
    print("=" * 80)
    print(f"数据频率: 5分钟")
    print(f"预测时间跨度: {N_HORIZON} 个5分钟 = {N_HORIZON * 5 / 60:.1f} 小时")
    print(f"币种数量: {len(SYMBOLS)}")
    print(f"筛选因子数量: {len(SELECTED_FACTORS)}")
    print(f"回测周期: 仅运行第1个周期（节省算力）")
    print(f"数据目录: {DATA_DIR}")
    print(f"缓存目录: {CACHE_DIR}")
    print(f"结果目录: {RESULTS_DIR}")
    print(f"模型目录: {MODELS_DIR}")
    print(f"模型类型: LightGBM回归")
    print("=" * 80)

    all_results = []
    all_training_metrics = []

    if USE_SAME_MODEL:
        # 只运行第一个周期
        period_config = BACKTEST_PERIODS[0]
        res_list, training_metrics = run_period_with_shared_model(period_config)
        if res_list:
            all_results.extend(res_list)
            all_training_metrics.append(training_metrics)
    else:
        print("注意：当前仅支持共享模型模式（USE_SAME_MODEL=True）")
        return

    results_df = pd.DataFrame(all_results)

    if len(results_df) == 0:
        print("没有成功的回测结果")
        return

    results_file = os.path.join(RESULTS_DIR, "rolling_backtest_results.csv")
    results_df.to_csv(results_file, index=False)
    print(f"\n详细结果已保存: {results_file}")

    if all_training_metrics:
        training_metrics_df = pd.DataFrame(all_training_metrics)
        training_metrics_file = os.path.join(RESULTS_DIR, "training_metrics_summary.csv")
        training_metrics_df.to_csv(training_metrics_file, index=False)
        print(f"\n训练指标汇总已保存: {training_metrics_file}")

        print("\n" + "="*80)
        print("训练指标汇总（所有周期）")
        print("="*80)
        print(training_metrics_df.to_string(index=False))

    generate_summary_tables(results_df)
    save_all_trades()

def save_all_trades():
    """保存所有交易记录到CSV文件，按时间排序"""
    if not ALL_TRADES:
        print("没有交易记录需要保存")
        return

    all_trades_df = pd.DataFrame(ALL_TRADES)

    all_trades_df['signal_time'] = pd.to_datetime(all_trades_df['signal_time'])
    all_trades_df['entry_time'] = pd.to_datetime(all_trades_df['entry_time'])
    all_trades_df['exit_time'] = pd.to_datetime(all_trades_df['exit_time'])

    all_trades_df = all_trades_df.sort_values('signal_time').reset_index(drop=True)
    all_trades_df.insert(0, 'trade_id', range(1, len(all_trades_df) + 1))

    output_file = os.path.join(RESULTS_DIR, "all_trades_chronological.csv")
    all_trades_df.to_csv(output_file, index=False)

    print(f"\n所有交易记录已保存: {output_file}")
    print(f"总交易数: {len(all_trades_df)}")
    print(f"时间范围: {all_trades_df['signal_time'].min()} 到 {all_trades_df['signal_time'].max()}")
    print(f"涉及币种: {sorted(all_trades_df['symbol'].unique())}")
    print(f"涉及周期: {sorted(all_trades_df['period'].unique())}")

    print(f"\n交易统计:")
    print(f"做多交易: {(all_trades_df['side'] == 'LONG').sum()}")
    print(f"做空交易: {(all_trades_df['side'] == 'SHORT').sum()}")
    print(f"盈利交易: {(all_trades_df['trade_return'] > 0).sum()}")
    print(f"亏损交易: {(all_trades_df['trade_return'] < 0).sum()}")
    print(f"总胜率: {(all_trades_df['trade_return'] > 0).mean():.2%}")
    print(f"平均收益: {all_trades_df['trade_return'].mean():.4f}")

def generate_summary_tables(results_df: pd.DataFrame):
    """生成3个汇总表格"""

    returns_table = results_df.pivot(index='symbol', columns='period', values='total_return')
    trades_table = results_df.pivot(index='symbol', columns='period', values='num_trades')
    rmse_table = results_df.pivot(index='symbol', columns='period', values='val_rmse')

    tables = {
        "returns": returns_table,
        "trades": trades_table,
        "val_rmse": rmse_table
    }

    for name, table in tables.items():
        file_path = os.path.join(RESULTS_DIR, f"summary_{name}.csv")
        table.to_csv(file_path)
        print(f"表格已保存: {file_path}")

    print("\n" + "="*80)
    print("表1: 各币种各周期收益率")
    print("="*80)
    print(returns_table.round(4))

    print("\n" + "="*80)
    print("表2: 各币种各周期交易次数")
    print("="*80)
    print(trades_table.fillna(0).astype(int))

    print("\n" + "="*80)
    print("表3: 各币种各周期验证集RMSE")
    print("="*80)
    print(rmse_table.round(6))


if __name__ == "__main__":
    main()
