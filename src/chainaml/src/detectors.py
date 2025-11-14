# src/detectors.py
import numpy as np

# --- Detector 1: Spraying ---
def detect_spraying(transactions, n_out_threshold=10, amount_cv_threshold=0.05):
    """
    检测喷洒交易。
    特征：单个交易有大量输出，且输出金额方差极小（近乎等额）。
    """
    alerts = []
    for tx in transactions:
        if tx['is_coinbase']:
            continue
        
        n_outputs = len(tx['outputs'])
        if n_outputs >= n_out_threshold:
            amounts = tx['output_amounts']
            # 计算变异系数 (Coefficient of Variation)
            if np.mean(amounts) > 0:
                cv = np.std(amounts) / np.mean(amounts)
                if cv < amount_cv_threshold:
                    alerts.append({
                        "tx_id": tx['tx_id'],
                        "type": "Spraying",
                        "reason": f"High fan-out ({n_outputs} outputs) with low amount variance (CV={cv:.4f})."
                    })
    return alerts

# --- Detector 2: Funneling ---
def detect_funneling(transactions, n_in_threshold=5):
    """
    检测漏斗交易。
    特征：单个交易有大量输入，通常归集到一个或少数几个输出地址。
    """
    alerts = []
    for tx in transactions:
        n_inputs = len(tx['inputs'])
        if n_inputs >= n_in_threshold:
            alerts.append({
                "tx_id": tx['tx_id'],
                "type": "Funneling",
                "reason": f"High fan-in ({n_inputs} inputs) consolidating funds."
            })
    return alerts

# --- Detector 3: CoinJoin-like Activity ---
def detect_coinjoin(transactions, equal_output_threshold=2):
    """
    检测CoinJoin类交易。
    特征：多输入、多输出，并且有多个金额完全相等的输出。
    """
    alerts = []
    for tx in transactions:
        if len(tx['inputs']) > 1 and len(tx['outputs']) > 1:
            amounts = tx['output_amounts']
            # 统计每个金额出现的次数
            amount_counts = {amount: amounts.count(amount) for amount in set(amounts)}
            
            for amount, count in amount_counts.items():
                if count >= equal_output_threshold:
                    alerts.append({
                        "tx_id": tx['tx_id'],
                        "type": "CoinJoin-like",
                        "reason": f"Found {count} equal outputs with amount {amount}, suggesting a CoinJoin."
                    })
                    break # 一个交易只报一次警
    return alerts

# --- Detector 4: Mining Wash ---
def detect_mining_wash(transactions, spray_detector_func, hops=5):
    """
    检测挖矿洗白。
    特征：一个coinbase交易的产出，在N跳之内被用于一个可疑的（如喷洒）交易。
    """
    alerts = []
    tx_map = {tx['tx_id']: tx for tx in transactions}
    addr_source_tx = {}
    
    # 第一次遍历，建立地址与来源交易的映射
    for tx in transactions:
        for output_addr in tx['outputs']:
            addr_source_tx[output_addr] = tx['tx_id']

    # 第二次遍历，从可疑交易向上追溯
    suspicious_spray_txs = {alert['tx_id'] for alert in spray_detector_func(transactions)}

    for tx_id in suspicious_spray_txs:
        current_tx = tx_map.get(tx_id)
        if not current_tx: continue

        # 开始回溯
        for hop in range(hops):
            if not current_tx['inputs']: # 到达coinbase或图的起点
                break
            
            # 简化PoC：我们只回溯第一个输入
            prev_addr = current_tx['inputs'][0]
            prev_tx_id = addr_source_tx.get(prev_addr)
            
            if not prev_tx_id:
                break
            
            prev_tx = tx_map.get(prev_tx_id)
            if not prev_tx:
                break

            if prev_tx['is_coinbase']:
                alerts.append({
                    "tx_id": tx_id, # 报告的是最终的洗钱交易
                    "type": "Mining Wash",
                    "reason": f"Funds from Coinbase TX ({prev_tx_id}) were used in a suspicious spray transaction within {hop + 1} hops."
                })
                break # 找到源头，停止回溯
            current_tx = prev_tx
            
    return alerts