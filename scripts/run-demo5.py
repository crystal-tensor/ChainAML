#!/usr/bin/env python
# scripts/run_demo.py
import json
import sys
import os
from collections import defaultdict

# 将 src 目录添加到 Python 路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.chainaml.detectors.spray_detector import SprayDetector
from src.chainaml.detectors.funnel_detector import FunnelDetector
from src.chainaml.detectors.coinjoin_detector import CoinjoinDetector
from src.chainaml.detectors.mining_detector import MiningWashDetector

def load_transactions(filepath):
    """
    加载JSON格式的交易数据
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：找不到示例数据文件 '{filepath}'")
        print("请确保您已在 'sample/sample_txs.json' 创建了数据文件。")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误：示例数据文件 '{filepath}' 格式不正确。")
        sys.exit(1)

def build_tx_lookup(txs):
    """
    创建一个字典以便快速回溯交易
    """
    return {tx['tx_id']: tx for tx in txs}

def main():
    print("="*50)
    print(" Aegis (神盾) 链上反洗钱 (AML) PoC 演示")
    print("="*50)
    
    # 定义数据文件路径
    # 使用os.path.join确保跨平台兼容性
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, 'sample', 'sample_txs.json')
    
    print(f"正在加载示例数据: {data_file}\n")
    transactions = load_transactions(data_file)
    tx_lookup = build_tx_lookup(transactions)
    
    print(f"已加载 {len(transactions)} 笔交易。开始初始化检测器...\n")
    
    # 1. 初始化所有检测器
    spray_detector = SprayDetector()
    funnel_detector = FunnelDetector()
    coinjoin_detector = CoinjoinDetector()
    mining_detector = MiningWashDetector()
    
    all_alerts = []

    # 2. 遍历所有交易，应用检测器
    print("--- 开始逐笔交易扫描 ---")
    for tx in transactions:
        print(f"正在分析 TX: {tx['tx_id']}...")
        
        # 应用“逐笔”检测器
        spray_detector.detect(tx)
        funnel_detector.detect(tx)
        coinjoin_detector.detect(tx)
        
        # 应用需要回溯的检测器
        mining_detector.detect(tx, tx_lookup)

    # 3. 收集所有警报
    all_alerts.extend(spray_detector.get_alerts())
    all_alerts.extend(funnel_detector.get_alerts())
    all_alerts.extend(coinjoin_detector.get_alerts())
    all_alerts.extend(mining_detector.get_alerts())
    
    # 4. （PoC中未实现）应用“全局”检测器
    # 在生产环境中，漏斗检测器（FunnelDetector）不应逐笔运行，
    # 而应在图数据库中运行，或像您方案中提到的那样，
    # 分析一个地址的全局入度和出度。
    # tx_funnel_hub_01 在我们的PoC中被FunnelDetector捕获，
    # 因为它的输入数量（25）满足了min_inputs（20）。
    
    print("\n--- 扫描完成 ---")

    # 5. 打印最终报告
    if not all_alerts:
        print("\n未发现任何高风险洗钱模式。")
    else:
        print(f"\n检测到 {len(all_alerts)} 个高风险警报！")
        print("="*50)
        print(" 警报详情：")
        print("="*50)
        for i, alert in enumerate(all_alerts, 1):
            print(f"\n[警报 {i}] - {alert['detector']} (严重性: {alert['severity']})")
            print(f"  交易ID: {alert['tx_id']}")
            print(f"  消息: {alert['message']}")

    print("\n="*50)
    print("PoC 演示结束。")
    print("注意：本PoC仅演示了基于规则的启发式检测。")
    print("生产系统还需整合图谱分析(GNN)、地址聚类和链下情报。")
    print("="*50)

if __name__ == "__main__":
    # 创建空的 __init__.py 文件（如果它们不存在），以确保Python将目录视为包
    paths_to_touch = [
        'src/__init__.py',
        'src/chainaml/__init__.py',
        'src/chainaml/detectors/__init__.py',
        'src/chainaml/utils/__init__.py'
    ]
    for p in paths_to_touch:
        init_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), p)
        if not os.path.exists(init_path):
            try:
                with open(init_path, 'w') as f:
                    pass
            except IOError:
                pass # 忽略权限错误等
                
    main()