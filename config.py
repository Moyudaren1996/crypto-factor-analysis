"""
配置文件 - 因子分析参数配置
"""

# 币种配置 - 全量币种（排除时间范围不完整的币种）
SYMBOLS = [
    'AAVE_USDT', 'ADA_USDT', 'ALGO_USDT', 'APT_USDT', 'ARB_USDT',
    'ATOM_USDT', 'AVAX_USDT', 'AXS_USDT', 'BNB_USDT', 'BTC_USDT',
    'DOGE_USDT', 'DOT_USDT', 'ENA_USDT', 'EOS_USDT', 'ETH_USDT',
    'FIL_USDT', 'GRT_USDT', 'HBAR_USDT', 'ICP_USDT',
    'INJ_USDT', 'LINK_USDT', 'LTC_USDT', 'LUNA_USDT', 'MANA_USDT',
    'OP_USDT', 'PEPE_USDT',
    'SHIB_USDT', 'SOL_USDT', 'SUI_USDT', 'TAO_USDT', 'THETA_USDT',
    'TRX_USDT', 'UNI_USDT', 'VET_USDT', 'XLM_USDT',
    'XRP_USDT', 'ZEC_USDT'
]

# 时间配置 - 6个月数据，分为两个3个月时段
# Period 1: 样本内（2024-07-19到2024-10-18，约3个月）
# Period 2: 样本外（2024-10-19到2025-01-18，约3个月）
PERIOD1_START = '2024-07-19 00:00:00'
PERIOD1_END = '2024-10-18 23:55:00'
PERIOD2_START = '2024-10-19 00:00:00'
PERIOD2_END = '2025-01-18 23:55:00'

# 兼容旧代码
START_DATE = PERIOD1_START
END_DATE = PERIOD2_END

# 分析配置
N_GROUPS = 5  # 分组数量（quintile）
FORWARD_PERIODS = 6  # 预测周期（5分钟，即1个周期）

# 路径配置
DATA_DIR = '../main_5m'  # 数据目录
FACTOR_DIR = 'factors'  # 因子定义目录
RESULT_DIR = 'results'  # 分析结果目录

# 年化参数（用于计算Sharpe Ratio）
# 5分钟数据，一年约有 365*24*12 = 105120 个周期
PERIODS_PER_YEAR = 365 * 24 * 12
