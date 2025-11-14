import os
import sys
import csv
from collections import Counter
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
# 让脚本能找到 chainaml 源码
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chainaml.src.data_loader import load_transactions
from chainaml.src.detectors import (
    detect_spraying,
    detect_funneling,
    detect_coinjoin,
    detect_mining_wash,
)

def to_float_list(values):
    result = []
    for v in values or []:
        try:
            result.append(float(v))
        except Exception:
            continue
    return result

def get_output_amounts(tx):
    # 兼容 output_amounts（纯金额列表）
    if isinstance(tx.get('output_amounts'), list):
        return to_float_list(tx['output_amounts'])
    # 兼容 outputs（可能是字典列表或金额列表/字符串列表）
    outputs = tx.get('outputs', [])
    if not isinstance(outputs, list):
        return []
    if outputs and isinstance(outputs[0], dict) and ('amount' in outputs[0]):
        return to_float_list([o.get('amount') for o in outputs if 'amount' in o])
    # 回退：当 outputs 是金额或金额字符串列表
    return to_float_list(outputs)

def compute_cv(amounts):
    amounts = to_float_list(amounts)
    if not amounts:
        return 0.0
    m = sum(amounts) / len(amounts)
    if m == 0:
        return 0.0
    var = sum((a - m) ** 2 for a in amounts) / len(amounts)
    return (var ** 0.5) / m

def visualize_reports(txs, spraying, funneling, coinjoin, mining):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(base_dir, 'data', 'report_plots')
    os.makedirs(out_dir, exist_ok=True)
    tx_index = {tx['tx_id']: tx for tx in txs}

    # 1) 摘要柱状图
    labels = ['喷洒', '归集', '类CoinJoin', '挖矿洗钱']
    counts = [len(spraying), len(funneling), len(coinjoin), len(mining)]
    plt.figure(figsize=(6, 4))
    plt.bar(labels, counts, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.title('可疑检测数量')
    plt.ylabel('数量')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'summary_counts.png'))
    plt.close()

    # 2) Spraying：输出数量 vs 金额 CV 散点图
    x_all, y_all = [], []
    for tx in txs:
        amounts = get_output_amounts(tx)
        x_all.append(len(amounts))
        y_all.append(compute_cv(amounts))
    plt.figure(figsize=(6, 4))
    plt.scatter(x_all, y_all, s=10, alpha=0.5, label='全部交易', color='#bbbbbb')

    x_flag, y_flag = [], []
    for res in spraying:
        tx = tx_index.get(res['tx_id'])
        if not tx:
            continue
        amounts = get_output_amounts(tx)
        x_flag.append(len(amounts))
        y_flag.append(compute_cv(amounts))
    if x_flag:
        plt.scatter(x_flag, y_flag, s=30, alpha=0.9, label='检测为喷洒', color='#d62728')
    plt.xlabel('输出数量')
    plt.ylabel('金额变异系数')
    plt.title('喷洒模式：输出数与金额变异系数')
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'spraying_outputs_vs_cv.png'))
    plt.close()

    # 3) Funneling：输入数量分布直方图
    inputs_counts = [len(tx.get('inputs', [])) for tx in txs]
    plt.figure(figsize=(6, 4))
    bins = max(10, int(max(inputs_counts) + 1)) if inputs_counts else 10
    plt.hist(inputs_counts, bins=bins, color='#1f77b4', alpha=0.6)
    flag_inputs = [len(tx_index[res['tx_id']].get('inputs', [])) for res in funneling if res['tx_id'] in tx_index]
    for ic in flag_inputs:
        plt.axvline(ic, color='#d62728', linestyle='--', alpha=0.7)
    plt.xlabel('输入数量')
    plt.ylabel('交易频数')
    plt.title('归集模式：高扇入分布')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'funneling_inputs_hist.png'))
    plt.close()

    # 4) CoinJoin-like：最大等额输出数分布
    max_equal = []
    for tx in txs:
        amounts = get_output_amounts(tx)
        if not amounts:
            max_equal.append(0)
            continue
        c = Counter([round(a, 8) for a in amounts])
        max_equal.append(max(c.values()))
    plt.figure(figsize=(6, 4))
    if max_equal:
        plt.hist(max_equal, bins=range(1, max(max_equal) + 2), color='#2ca02c', alpha=0.6, align='left')
    flag_equal = []
    for res in coinjoin:
        tx = tx_index.get(res['tx_id'])
        if not tx:
            continue
        c = Counter([round(a, 8) for a in get_output_amounts(tx)])
        flag_equal.append(max(c.values()))
    for me in flag_equal:
        plt.axvline(me, color='#d62728', linestyle='--', alpha=0.7)
    plt.xlabel('每笔交易的最大等额输出数')
    plt.ylabel('交易频数')
    plt.title('类 CoinJoin：等额输出倍数')
    plt.tight_layout()
    plt.savefig(os.path.join(out_dir, 'coinjoin_equal_outputs_hist.png'))
    plt.close()

    # 5) Mining Wash：输出 CSV
    csv_path = os.path.join(out_dir, 'mining_wash_detections.csv')
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['tx_id', 'reason'])
        for res in mining:
            writer.writerow([res.get('tx_id'), res.get('reason')])

    print(f"[图像已保存] {out_dir}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, 'data', 'sample_txs.json')
    if not os.path.exists(data_file):
        print(f"Error: Data file not found at '{data_file}'.")
        print("Please run 'python scripts/generate_sample_data.py' first.")
        sys.exit(1)
    txs = load_transactions(data_file)
    spraying = detect_spraying(txs)
    funneling = detect_funneling(txs)
    coinjoin = detect_coinjoin(txs)
    # 关键修复：传入喷洒检测函数用于挖矿洗钱检测的关联判断
    mining = detect_mining_wash(txs, detect_spraying)

    # 可视化
    visualize_reports(txs, spraying, funneling, coinjoin, mining)

if __name__ == "__main__":
    main()