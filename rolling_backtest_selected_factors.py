# -*- coding: utf-8 -*-
"""
滚动回测策略（5分钟级别）：使用selected_factors.txt中的因子
- 从factors/目录动态加载因子
- 支持pandas_ta因子和自定义因子
- 单周期快速测试模式
"""

from __future__ import annotations
import os
import sys
import warnings
import importlib.util
from typing import Tuple, List, Dict
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pandas_ta  # 激活 DataFrame.ta 访问器

import joblib
from joblib import Parallel, delayed
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, accuracy_score
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import lightgbm as lgb

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# ============================
# 全局配置参数
# ============================
RANDOM_STATE = 42
N_JOBS = 8  # LightGBM训练线程数
N_PARALLEL_SYMBOLS = 4  # 并行处理的币种数量

# 币种配置（所有可用币种）
SYMBOLS = [
    "AAVE", "ADA", 
    "ALGO", "APT", "ARB", "ATOM", "AVAX", "AXS",
    "BNB", "BTC", "DOGE", "DOT", "ENA", "EOS", "ETH", "EUL",
    "FIL", "GRT", "HBAR", "ICP", "INJ", "LINK", "LTC", 
    # "MANA", "MATIC", "OP", "PEPE", "POL", "PUMP", "SHIB", "SOL",
    # "SUI", "TAO", "THETA", "TRX", "UNI", "VET", "VIRTUAL", "XLM",
    # "XMR", "XRP", "ZEC","LUNA",
]

# 数据目录
DATA_DIR = "main_5m"

# 时间配置
DT_COL = "datetime"
N_HORIZON = 5  # 预测未来5个5分钟

# 只运行一个周期（快速测试）
SINGLE_PERIOD_MODE = True
SELECTED_PERIOD = 8  # 选择第8个周期（2024年下半年）

# 滚动回测周期配置
BACKTEST_PERIODS = []
start_date = datetime(2022, 1, 1)
for i in range(16):
    test_start = start_date + timedelta(days=i*90)
    test_end = test_start + timedelta(days=89)
    val_start = test_start - timedelta(days=180)
    val_end = test_start - timedelta(days=1)
    BACKTEST_PERIODS.append({
        "period": i + 1,
        "train_end": val_start - timedelta(days=1),
        "val_start": val_start,
        "val_end": val_end,
        "test_start": test_start,
        "test_end": test_end,
    })

# 如果是单周期模式，只保留选定的周期
if SINGLE_PERIOD_MODE:
    BACKTEST_PERIODS = [p for p in BACKTEST_PERIODS if p['period'] == SELECTED_PERIOD]

# 时间权重配置
USE_TIME_WEIGHTS = True
TIME_WEIGHT_METHOD = "linear"
TIME_WEIGHT_MIN = 0.5
TIME_WEIGHT_MAX = 1.5

# 交易配置
MAX_TRADES_PER_PERIOD = 1000
STOP_LOSS_PERCENTAGE = 0.05

# 回归阈值配置
REG_LONG_QUANTILE = 0.999
REG_SHORT_QUANTILE = 0.001
REG_EXIT_LONG_QUANTILE = 0.95
REG_EXIT_SHORT_QUANTILE = 0.05

# 目录配置
CACHE_DIR = "cache_5m_selected"
RESULTS_DIR = "rolling_results_selected_factors"
MODELS_DIR = "trained_models_selected_factors"
FACTORS_DIR = "factors"
SELECTED_FACTORS_FILE = "selected_factors.txt"

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# 全局交易记录
ALL_TRADES = []

def clear_all_trades():
    global ALL_TRADES
    ALL_TRADES = []

# ============================
# 加载selected_factors列表
# ============================
def load_selected_factors() -> List[str]:
    """从selected_factors.txt加载因子列表"""
    factors = []
    with open(SELECTED_FACTORS_FILE, 'r') as f:
        for line in f:
            factor_name = line.strip()
            if factor_name and not factor_name.startswith('#'):
                factors.append(factor_name)
    print(f"从 {SELECTED_FACTORS_FILE} 加载了 {len(factors)} 个因子")
    return factors

# ============================
# 因子计算模块
# ============================
def load_factor_module(factor_name: str):
    """动态加载因子模块"""
    factor_file = os.path.join(FACTORS_DIR, f"{factor_name}.py")
    if not os.path.exists(factor_file):
        print(f"警告: 因子文件不存在: {factor_file}")
        return None

    spec = importlib.util.spec_from_file_location(factor_name, factor_file)
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print(f"加载因子 {factor_name} 失败: {e}")
        return None

def compute_factor(data: Dict[str, pd.DataFrame], factor_name: str) -> pd.DataFrame:
    """计算单个因子"""
    module = load_factor_module(factor_name)
    if module is None:
        return None

    try:
        # 直接调用因子模块的calculate函数
        factor_values = module.calculate(data)

        # 处理无穷大
        factor_values = factor_values.replace([np.inf, -np.inf], np.nan)
        return factor_values
    except Exception as e:
        print(f"计算因子 {factor_name} 失败: {e}")
        return None

def compute_all_selected_factors(df_ohlcv: pd.DataFrame, symbol: str,
                                  selected_factors: List[str]) -> pd.DataFrame:
    """计算所有选中的因子"""
    df = df_ohlcv.copy()

    # 准备数据字典（单个币种）
    data = {
        'open': df[['open']].rename(columns={'open': symbol}),
        'high': df[['high']].rename(columns={'high': symbol}),
        'low': df[['low']].rename(columns={'low': symbol}),
        'close': df[['close']].rename(columns={'close': symbol}),
        'volume': df[['volume']].rename(columns={'volume': symbol}),
    }

    # 计算每个因子
    factor_count = 0
    for factor_name in selected_factors:
        factor_values = compute_factor(data, factor_name)
        if factor_values is not None and symbol in factor_values.columns:
            df[factor_name] = factor_values[symbol]
            factor_count += 1

    print(f"[{symbol}] 成功计算 {factor_count}/{len(selected_factors)} 个因子")

    # 前向填充
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.ffill()

    return df

# ============================
# 数据加载
# ============================
import glob

def get_data_file(symbol: str) -> str:
    """获取币种数据文件路径"""
    candidates = []
    for pat in (os.path.join(DATA_DIR, f"{symbol}_USDT_5m_*.csv"),
                os.path.join(DATA_DIR, f"{symbol}_USDT_5m_*.CSV")):
        candidates.extend(glob.glob(pat))
    if candidates:
        candidates.sort()
        return candidates[-1]
    return None

def read_data(path: str, dt_col: str = DT_COL) -> pd.DataFrame:
    """读取CSV数据"""
    df = pd.read_csv(path, parse_dates=[dt_col])
    df.columns = [c.strip().lower() for c in df.columns]
    if dt_col.lower() not in df.columns:
        raise ValueError(f"未找到时间列: {dt_col}")
    # 使用numpy排序避免pandas bug
    df = df.iloc[df[dt_col.lower()].values.argsort()]
    df = df.reset_index(drop=True)
    df = df.set_index(dt_col.lower())
    return df

# ============================
# 特征和标签构建
# ============================
def make_label_regression(df: pd.DataFrame, n: int) -> pd.Series:
    """生成回归标签（未来收益率）"""
    future = df["close"].shift(-n)
    label = (future - df["close"]) / df["close"]
    return label

def time_split_mask(index: pd.DatetimeIndex, start: str, end: str) -> np.ndarray:
    start_ts = pd.to_datetime(start)
    end_ts = pd.to_datetime(end)
    return (index >= start_ts) & (index <= end_ts)

def purge_by_horizon(idx: pd.DatetimeIndex, mask: np.ndarray, n: int) -> np.ndarray:
    """避免标签泄漏"""
    s = pd.Series(mask.astype(bool), index=idx)
    purged = (s & s.shift(-n).fillna(False)).values
    return purged

def build_feature_matrix(df_all: pd.DataFrame, n: int, selected_factors: List[str]) -> Tuple[pd.DataFrame, pd.Series]:
    """构建特征矩阵和标签"""
    y = make_label_regression(df_all, n)

    valid_mask = y.notna()
    df_all = df_all.loc[valid_mask]
    y = y.loc[valid_mask]

    # 使用selected_factors作为特征列
    feat_cols = [c for c in selected_factors if c in df_all.columns]
    X = df_all[feat_cols].select_dtypes(include=[np.number]).copy()
    X = X.ffill()

    y = y.loc[X.index]
    return X, y

# ============================
# 时间权重
# ============================
def calculate_time_weights(index: pd.DatetimeIndex, method: str = TIME_WEIGHT_METHOD,
                          min_weight: float = TIME_WEIGHT_MIN,
                          max_weight: float = TIME_WEIGHT_MAX) -> np.ndarray:
    """计算时间权重"""
    if len(index) == 0:
        return np.array([])

    latest_time = index.max()
    earliest_time = index.min()
    time_span = (latest_time - earliest_time).total_seconds()

    if time_span == 0:
        return np.ones(len(index))

    time_positions = np.array((index - earliest_time).total_seconds()) / time_span

    if method == "linear":
        weights = min_weight + (max_weight - min_weight) * time_positions
    elif method == "sqrt":
        weights = min_weight + (max_weight - min_weight) * np.sqrt(time_positions)
    else:
        weights = np.ones(len(index))

    weights = np.clip(weights, min_weight, max_weight)
    weights = weights / weights.mean()

    return weights

# ============================
# 模型训练
# ============================
def train_lgb_reg(X_train: pd.DataFrame, y_train: pd.Series,
                  X_val: pd.DataFrame, y_val: pd.Series,
                  sample_weight: np.ndarray = None):
    """训练LightGBM回归模型"""
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

# ============================
# 阈值计算
# ============================
def auto_threshold_quantile(scores: np.ndarray, long_quantile: float, short_quantile: float) -> Tuple[float, float]:
    """基于分位数确定阈值"""
    if scores is None or len(scores) == 0:
        return np.inf, -np.inf
    thr_long = float(np.quantile(scores, long_quantile))
    thr_short = float(np.quantile(scores, short_quantile))
    return thr_long, thr_short

# ============================
# 回测函数
# ============================
def reg_signal_backtest(reg_pred: pd.Series, px_open: pd.Series,
                        px_high: pd.Series, px_low: pd.Series,
                        n_hold: int, reg_long_thr: float, reg_short_thr: float,
                        reg_exit_long_thr: float = None, reg_exit_short_thr: float = None,
                        max_trades: int = None, stop_loss_pct: float = STOP_LOSS_PERCENTAGE) -> Tuple[pd.Series, pd.DataFrame]:
    """回归信号回测"""
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
            "entry_price": entry_price,
            "exit_price": exit_price,
            "trade_return": float(trade_r),
            "reg_signal": float(reg_val),
            "hit_sl": int(hit_sl),
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

    return {
        "total_return": total_ret,
        "num_trades": len(trades),
    }

def print_regression_metrics(y_true: pd.Series, y_pred: np.ndarray, dataset_name: str = "Dataset") -> dict:
    """打印回归指标"""
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    corr = np.corrcoef(y_true, y_pred)[0, 1]

    y_true_direction = np.sign(y_true)
    y_pred_direction = np.sign(y_pred)
    direction_accuracy = accuracy_score(y_true_direction, y_pred_direction)

    print(f"\n{dataset_name} 指标:")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  MAE: {mae:.6f}")
    print(f"  R²: {r2:.6f}")
    print(f"  相关系数: {corr:.6f}")
    print(f"  方向准确率: {direction_accuracy:.4f} ({direction_accuracy*100:.2f}%)")

    return {
        'rmse': rmse,
        'mae': mae,
        'r2': r2,
        'corr': corr,
        'direction_accuracy': direction_accuracy,
    }

# ============================
# 单币种特征处理
# ============================
def _process_single_symbol_features(symbol: str, period_config: dict, selected_factors: List[str]) -> dict:
    """处理单个币种的特征计算"""
    data_file = get_data_file(symbol)
    if not data_file or not os.path.exists(data_file):
        return {'symbol': symbol, 'error': f'数据文件不存在'}

    df0 = read_data(data_file, DT_COL)

    # 计算因子（总是重新计算）
    df_all = compute_all_selected_factors(df0, symbol, selected_factors)

    X, y = build_feature_matrix(df_all, N_HORIZON, selected_factors)
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

# ============================
# 主回测函数
# ============================
def run_period_with_shared_model(period_config: dict, selected_factors: List[str]) -> Tuple[List[dict], dict]:
    """运行单个周期的回测"""
    period_no = period_config['period']
    print(f"\n{'='*80}")
    print(f"周期 {period_no}: {period_config['test_start']} -> {period_config['test_end']}")
    print(f"{'='*80}")

    # 串行处理（减少内存占用）
    print(f"处理 {len(SYMBOLS)} 个币种的特征计算...")
    results_raw = []
    for symbol in SYMBOLS:
        result = _process_single_symbol_features(symbol, period_config, selected_factors)
        results_raw.append(result)

    # 整理结果
    sym_data = {}
    common_cols = None

    for result in results_raw:
        if 'error' in result:
            print(f"  {result['symbol']}: {result.get('error', '')}")
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

    if not sym_data or not common_cols:
        print("无可用数据，跳过本周期")
        return [], {}

    # 构建训练/验证集
    common_cols = sorted(list(common_cols))
    print(f"\n共同特征列数: {len(common_cols)}")

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

    X_train_all = pd.concat(X_train_list, axis=0)
    y_train_all = pd.concat(y_train_list, axis=0)
    train_index_all = pd.DatetimeIndex(np.concatenate([ix.values for ix in idx_train_list]))
    X_val_all = pd.concat(X_val_list, axis=0)
    y_val_all = pd.concat(y_val_list, axis=0)

    for sym, d in sym_data.items():
        d['X_val_clip'] = d['Xc'].loc[d['m_val']]
        d['X_test_clip'] = d['Xc'].loc[d['m_test']]

    # 时间权重
    sample_weights = None
    if USE_TIME_WEIGHTS:
        sample_weights = calculate_time_weights(train_index_all, method=TIME_WEIGHT_METHOD)
        print(f"时间权重: min={sample_weights.min():.4f}, max={sample_weights.max():.4f}")

    # 训练模型
    print(f"\n训练LightGBM（训练集={len(X_train_all)}，验证集={len(X_val_all)}）...")
    reg_model = train_lgb_reg(X_train_all, y_train_all, X_val_all, y_val_all, sample_weights)

    # 评估
    reg_pred_train = reg_model.predict(X_train_all, num_iteration=reg_model.best_iteration)
    reg_pred_val = reg_model.predict(X_val_all, num_iteration=reg_model.best_iteration)
    train_metrics = print_regression_metrics(y_train_all, reg_pred_train, "训练集")
    val_metrics = print_regression_metrics(y_val_all, reg_pred_val, "验证集")

    # 计算阈值
    reg_long_thr, reg_short_thr = auto_threshold_quantile(reg_pred_val, REG_LONG_QUANTILE, REG_SHORT_QUANTILE)
    reg_exit_long_thr, reg_exit_short_thr = auto_threshold_quantile(reg_pred_val, REG_EXIT_LONG_QUANTILE, REG_EXIT_SHORT_QUANTILE)

    print(f"\n阈值:")
    print(f"  开仓: 做多>={reg_long_thr:.6f}, 做空<={reg_short_thr:.6f}")
    print(f"  平仓: 平多<={reg_exit_long_thr:.6f}, 平空>={reg_exit_short_thr:.6f}")

    # 保存模型
    model_path = os.path.join(MODELS_DIR, f"period_{period_no}_model.pkl")
    joblib.dump(reg_model, model_path)
    print(f"\n模型已保存: {model_path}")

    # 对每个币种回测
    results = []
    print(f"\n回测各币种...")

    for symbol, d in sym_data.items():
        X_test_clip = d['X_test_clip']
        if X_test_clip.empty:
            continue

        reg_pred_test = pd.Series(
            reg_model.predict(X_test_clip, num_iteration=reg_model.best_iteration),
            index=X_test_clip.index
        )

        # 测试集指标
        y_test_sym = d['y'].loc[d['m_test']]
        test_metrics = print_regression_metrics(y_test_sym, reg_pred_test.values, f"测试集 ({symbol})")

        # 回测
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

        # 记录交易
        for tr in trades.itertuples():
            ALL_TRADES.append({
                'symbol': symbol,
                'period': period_no,
                'signal_time': tr.signal_time,
                'entry_time': tr.entry_time,
                'exit_time': tr.exit_time,
                'side': tr.side,
                'entry_price': tr.entry_price,
                'exit_price': tr.exit_price,
                'trade_return': tr.trade_return,
            })

        metrics = calculate_metrics(ret_test, trades)
        results.append({
            'symbol': symbol,
            'period': period_no,
            'test_start': d['test_start'],
            'test_end': d['test_end'],
            'total_return': metrics['total_return'],
            'num_trades': metrics['num_trades'],
            'test_r2': test_metrics['r2'],
            'test_corr': test_metrics['corr'],
            'test_direction_acc': test_metrics['direction_accuracy'],
        })

        print(f"  {symbol}: 收益={metrics['total_return']:.4f}, 交易={metrics['num_trades']}")

    # 汇总
    period_training_metrics = {
        'period': period_no,
        'train_samples': len(X_train_all),
        'val_samples': len(X_val_all),
        'train_rmse': train_metrics['rmse'],
        'val_rmse': val_metrics['rmse'],
        'val_r2': val_metrics['r2'],
        'val_corr': val_metrics['corr'],
    }

    return results, period_training_metrics


def main():
    """主函数"""
    clear_all_trades()

    print("=" * 80)
    print("滚动回测：使用 selected_factors.txt 中的因子")
    print("=" * 80)

    # 加载因子列表
    selected_factors = load_selected_factors()
    print(f"\n因子列表前10个: {selected_factors[:10]}")

    print(f"\n配置:")
    print(f"  币种数量: {len(SYMBOLS)}")
    print(f"  因子数量: {len(selected_factors)}")
    print(f"  回测周期: {len(BACKTEST_PERIODS)}")
    print(f"  预测跨度: {N_HORIZON} x 5分钟 = {N_HORIZON * 5}分钟")
    print(f"  单周期模式: {SINGLE_PERIOD_MODE}")
    if SINGLE_PERIOD_MODE:
        print(f"  选定周期: {SELECTED_PERIOD}")
    print("=" * 80)

    all_results = []
    all_training_metrics = []

    for period_config in BACKTEST_PERIODS:
        res_list, training_metrics = run_period_with_shared_model(period_config, selected_factors)
        if res_list:
            all_results.extend(res_list)
            all_training_metrics.append(training_metrics)

    # 保存结果
    if all_results:
        results_df = pd.DataFrame(all_results)
        results_file = os.path.join(RESULTS_DIR, "backtest_results.csv")
        results_df.to_csv(results_file, index=False)
        print(f"\n结果已保存: {results_file}")

        # 汇总
        print("\n" + "=" * 80)
        print("回测结果汇总")
        print("=" * 80)
        print(results_df.to_string(index=False))

        # 总体统计
        print(f"\n总体统计:")
        print(f"  平均收益: {results_df['total_return'].mean():.4f}")
        print(f"  总交易数: {results_df['num_trades'].sum()}")
        print(f"  平均方向准确率: {results_df['test_direction_acc'].mean():.4f}")

    # 保存交易记录
    if ALL_TRADES:
        trades_df = pd.DataFrame(ALL_TRADES)
        trades_df = trades_df.sort_values('signal_time').reset_index(drop=True)
        trades_file = os.path.join(RESULTS_DIR, "all_trades.csv")
        trades_df.to_csv(trades_file, index=False)
        print(f"\n交易记录已保存: {trades_file}")
        print(f"总交易数: {len(trades_df)}")
        if len(trades_df) > 0:
            print(f"胜率: {(trades_df['trade_return'] > 0).mean():.2%}")
            print(f"平均收益: {trades_df['trade_return'].mean():.4f}")


if __name__ == "__main__":
    main()
