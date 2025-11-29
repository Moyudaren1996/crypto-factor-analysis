"""
因子计算模块
从Python文件加载因子函数并执行计算
"""

import pandas as pd
import importlib.util
import os
from typing import Dict
import config


def load_factor_function(factor_file: str):
    """
    从Python文件加载因子函数

    Args:
        factor_file: 因子文件路径（相对于factors目录）

    Returns:
        factor_function: 因子计算函数
        factor_name: 因子名称
    """
    # 构建完整路径
    if not factor_file.endswith('.py'):
        factor_file += '.py'

    if not os.path.isabs(factor_file):
        factor_path = os.path.join(config.FACTOR_DIR, factor_file)
    else:
        factor_path = factor_file

    if not os.path.exists(factor_path):
        raise FileNotFoundError(f"因子文件不存在: {factor_path}")

    # 从文件名提取因子名称
    factor_name = os.path.splitext(os.path.basename(factor_path))[0]

    # 动态导入模块
    spec = importlib.util.spec_from_file_location(factor_name, factor_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # 获取calculate函数
    if not hasattr(module, 'calculate'):
        raise AttributeError(f"因子文件 {factor_file} 必须包含 'calculate' 函数")

    return module.calculate, factor_name


def calculate_factor(data: Dict[str, pd.DataFrame],
                     factor_file: str) -> tuple:
    """
    计算因子值

    Args:
        data: OHLCV数据字典
        factor_file: 因子文件路径

    Returns:
        factor_values: 因子值DataFrame (index=datetime, columns=symbols)
        factor_name: 因子名称
    """
    print(f"\n正在加载因子: {factor_file}")

    # 加载因子函数
    factor_func, factor_name = load_factor_function(factor_file)

    print(f"因子名称: {factor_name}")
    print("正在计算因子值...")

    # 执行因子计算
    try:
        factor_values = factor_func(data)
    except Exception as e:
        raise RuntimeError(f"因子计算失败: {str(e)}")

    # 验证返回值
    if not isinstance(factor_values, pd.DataFrame):
        raise TypeError(f"因子函数必须返回DataFrame，当前返回: {type(factor_values)}")

    # 处理无穷大和NaN值
    factor_values = factor_values.replace([float('inf'), float('-inf')], pd.NA)

    print(f"因子计算完成，形状: {factor_values.shape}")
    print(f"缺失值数量: {factor_values.isna().sum().sum()}")

    return factor_values, factor_name


if __name__ == "__main__":
    # 测试因子计算
    import sys
    sys.path.append('..')
    from src.data_loader import load_data

    data = load_data()

    # 这里需要先创建一个测试因子文件
    print("请先创建因子文件后再测试")
