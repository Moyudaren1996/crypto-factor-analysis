"""
Volatility指标 - HLRM (High-Low Ratio Momentum)

因子描述:
    高低价格比率动量,衡量日内波动幅度相对于价格的变化趋势
    HL_Ratio表示每个时间点的相对波动幅度
    该因子计算HL_Ratio的动量,捕捉波动幅度的趋势变化

    波动幅度扩大可能预示:
    - 市场活跃度上升,趋势即将启动
    - 不确定性增加,可能出现反转

    波动幅度收窄可能预示:
    - 市场进入整理,酝酿突破
    - 趋势减弱,即将盘整

参数:
    ratio_period: 6 (计算HL_Ratio的平滑周期,30分钟)
    momentum_period: 12 (计算动量的周期,1小时)

计算公式:
    HL_Ratio = (High - Low) / Close
    HL_Ratio_MA = HL_Ratio.rolling(6).mean()  # 平滑
    HLRM = (HL_Ratio_MA - HL_Ratio_MA[t-12]) / HL_Ratio_MA[t-12] * 100

输出:
    因子值DataFrame,单位为百分比

数据依赖:
    - high: 最高价 (必需)
    - low: 最低价 (必需)
    - close: 收盘价 (必需)

创建日期: 2025-12-06
版本: v1.0 (优化3: 高低价格比率动量)
"""
import pandas as pd
import numpy as np

def calculate(data):
    """
    计算HLRM因子

    Args:
        data: dict with keys ['open', 'high', 'low', 'close', 'volume']
              每个key对应的value是DataFrame,columns为币种symbol

    Returns:
        pd.DataFrame: 因子值,index为时间,columns为币种symbol
    """
    # 提取所需数据
    high = data['high']
    low = data['low']
    close = data['close']

    # 定义参数
    ratio_period = 6
    momentum_period = 12

    # 计算高低价格比率
    hl_ratio = (high - low) / close

    # 对比率进行平滑,减少噪音
    hl_ratio_ma = hl_ratio.rolling(ratio_period).mean()

    # 计算比率的动量
    hlrm = (hl_ratio_ma - hl_ratio_ma.shift(momentum_period)) / hl_ratio_ma.shift(momentum_period) * 100

    return hlrm
