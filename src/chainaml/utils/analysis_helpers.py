# src/chainaml/utils/analysis_helpers.py
import numpy as np
from collections import Counter

def calculate_amount_cv(amounts):
    """
    计算金额的变异系数 (Coefficient of Variation)
    CV = 标准差 / 平均值
    CV 越接近0，说明金额越趋同（越"等额"）
    """
    if not amounts or len(amounts) < 2:
        return 0.0

    mean = np.mean(amounts)
    std_dev = np.std(amounts)

    if mean == 0:
        return 0.0

    return std_dev / mean

def find_equal_outputs(outputs, tolerance=0.01):
    """
    查找等额输出
    返回一个字典，key为金额，value为该金额出现的次数
    """
    amounts = [output['amount'] for output in outputs]

    # 使用计数器来统计每个金额出现的次数
    # 考虑到浮点数精度，这里可以引入一个取整或分组的逻辑
    # 为简化PoC，我们假设金额是精确的
    amount_counts = Counter(amounts)

    # 返回出现超过1次的金额
    return {amount: count for amount, count in amount_counts.items() if count > 1}