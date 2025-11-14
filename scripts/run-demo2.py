# scripts/run_demo.py
import sys
import os

# 将src目录添加到Python路径中
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from chainaml.src.data_loader import load_transactions
from chainaml.src.detectors import (
    detect_spraying,
    detect_funneling,
    detect_coinjoin,
    detect_mining_wash
)

def run_all_detectors(transactions):
    """运行所有检测器并汇总结果"""
    all_alerts = {}

    # 基础检测器
    spray_alerts = detect_spraying(transactions)
    funnel_alerts = detect_funneling(transactions)
    coinjoin_alerts = detect_coinjoin(transactions)
    
    all_alerts["Spraying"] = spray_alerts
    all_alerts["Funneling"] = funnel_alerts
    all_alerts["CoinJoin-like"] = coinjoin_alerts

    # 依赖于其他检测器的高级检测器
    mining_wash_alerts = detect_mining_wash(transactions, detect_spraying)
    all_alerts["Mining Wash"] = mining_wash_alerts
    
    return all_alerts

def print_report(alerts_by_type):
    """打印格式化的检测报告"""
    print("\n" + "="*50)
    print("      ChainAML PoC Detection Report")
    print("="*50 + "\n")

    total_alerts = 0
    for alert_type, alerts in alerts_by_type.items():
        print(f"--- {alert_type} Detections ({len(alerts)}) ---")
        if not alerts:
            print("None found.")
        else:
            for alert in alerts:
                print(f"  [!] TX_ID: {alert['tx_id']}")
                print(f"      Reason: {alert['reason']}")
            total_alerts += len(alerts)
        print("-"*(len(alert_type) + 20) + "\n")

    print(f"\nSUMMARY: Found a total of {total_alerts} suspicious transactions.")
    print("="*50)


if __name__ == "__main__":
    # 1. 加载数据
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_file = os.path.join(base_dir, 'data', 'sample_txs.json')
    txs = load_transactions(data_file)
    # 其后逻辑保持不变
    
    if txs:
        # 2. 运行检测
        all_alerts = run_all_detectors(txs)
        
        # 3. 打印报告
        print_report(all_alerts)