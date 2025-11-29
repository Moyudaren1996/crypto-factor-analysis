"""
数据加载模块
负责从CSV文件加载多币种OHLCV数据，并进行数据对齐和清洗
"""

import pandas as pd
import os
from typing import List, Dict
import config


def load_data(symbols: List[str] = None,
              start_date: str = None,
              end_date: str = None) -> Dict[str, pd.DataFrame]:
    """
    加载多币种OHLCV数据

    Args:
        symbols: 币种列表，默认使用config中的配置
        start_date: 开始时间，格式 'YYYY-MM-DD HH:MM:SS'
        end_date: 结束时间，格式 'YYYY-MM-DD HH:MM:SS'

    Returns:
        data_dict: 字典，包含 'open', 'high', 'low', 'close', 'volume'
                  每个key对应一个DataFrame (index=datetime, columns=symbols)
    """
    if symbols is None:
        symbols = config.SYMBOLS
    if start_date is None:
        start_date = config.START_DATE
    if end_date is None:
        end_date = config.END_DATE

    print(f"正在加载 {len(symbols)} 个币种的数据...")
    print(f"时间范围: {start_date} 至 {end_date}")

    # 存储每个币种的数据
    all_data = {}

    for symbol in symbols:
        # 构造文件路径
        # 文件名格式: BTC_USDT_5m_20180101_to_20251018.csv
        csv_files = [f for f in os.listdir(config.DATA_DIR) if f.startswith(symbol)]

        if not csv_files:
            print(f"警告: 未找到 {symbol} 的数据文件，跳过")
            continue

        file_path = os.path.join(config.DATA_DIR, csv_files[0])

        # 读取CSV
        df = pd.read_csv(file_path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)

        # 筛选时间范围
        df = df.loc[start_date:end_date]

        # 检查是否有数据
        if len(df) == 0:
            print(f"警告: {symbol} 在指定时间范围内无数据，跳过")
            continue

        all_data[symbol] = df
        print(f"  {symbol}: 加载 {len(df)} 条记录")

    if len(all_data) == 0:
        raise ValueError("没有成功加载任何币种数据")

    # 数据对齐 - 找到所有币种的共同时间戳
    print("\n正在对齐时间戳...")
    common_index = None
    for symbol, df in all_data.items():
        if common_index is None:
            common_index = df.index
        else:
            common_index = common_index.intersection(df.index)

    print(f"共同时间戳数量: {len(common_index)}")

    # 重新索引所有数据到共同时间戳
    for symbol in all_data:
        all_data[symbol] = all_data[symbol].loc[common_index]

    # 构建面板数据结构
    print("\n构建面板数据...")
    data_dict = {
        'open': pd.DataFrame(),
        'high': pd.DataFrame(),
        'low': pd.DataFrame(),
        'close': pd.DataFrame(),
        'volume': pd.DataFrame()
    }

    for symbol, df in all_data.items():
        data_dict['open'][symbol] = df['open']
        data_dict['high'][symbol] = df['high']
        data_dict['low'][symbol] = df['low']
        data_dict['close'][symbol] = df['close']
        data_dict['volume'][symbol] = df['volume']

    # 数据清洗 - 处理缺失值和异常值
    print("\n清洗数据...")
    for key in data_dict:
        # 前向填充缺失值
        data_dict[key] = data_dict[key].ffill()
        # 后向填充剩余的缺失值
        data_dict[key] = data_dict[key].bfill()

        # 检查是否还有缺失值
        missing_count = data_dict[key].isna().sum().sum()
        if missing_count > 0:
            print(f"警告: {key} 仍有 {missing_count} 个缺失值")

    print(f"\n数据加载完成!")
    print(f"最终形状: {data_dict['close'].shape} (时间 × 币种)")
    print(f"时间范围: {data_dict['close'].index[0]} 至 {data_dict['close'].index[-1]}")

    return data_dict


if __name__ == "__main__":
    # 测试数据加载
    data = load_data()
    print("\n数据预览:")
    print(data['close'].head())
    print("\n数据统计:")
    print(data['close'].describe())
