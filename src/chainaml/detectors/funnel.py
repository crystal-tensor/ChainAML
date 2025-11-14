
import pandas as pd
from collections import defaultdict

def detect_funneling(txs, window_seconds=3600*6, min_unique_senders=5, min_forward_ratio=0.5, min_inputs_single_tx=4):
    """
    漏斗检测：包括两种模式
    1. 地址聚合模式：在时间窗口内，某地址收到来自大量唯一发送方的入账
    2. 单笔交易模式：单笔交易中输入多输出少（典型的漏斗模式）
    输入: txs DataFrame 列 ['ts','tx_id','inputs','outputs','output_amounts']
    输出: DataFrame [tx_id, address, unique_senders, forward_ratio, dest, funnel_score, reason]
    """
    txs = txs.copy()
    txs = txs.sort_values('ts')
    rows = []
    
    # 模式1: 单笔交易漏斗检测（输入多输出少）
    for _, r in txs.iterrows():
        ins = r['inputs'] or []
        outs = r['outputs'] or []
        n_inputs = len(ins)
        n_outputs = len(outs)
        
        # 检测单笔交易漏斗：输入>=min_inputs_single_tx，输出<=2
        if n_inputs >= min_inputs_single_tx and n_outputs <= 2:
            ratio = n_inputs / max(n_outputs, 1)
            score = 1.0 + ratio / 10
            rows.append({
                'tx_id': r['tx_id'],
                'address': outs[0] if outs else 'unknown',
                'unique_senders': n_inputs,
                'forward_ratio': 1.0 if n_outputs == 1 else 0.5,
                'dest': outs[0] if outs else 'unknown',
                'funnel_score': score,
                'risk_score': min(score / 2.0, 1.0),  # 归一化到0-1
                'reason': f'单笔漏斗交易: {n_inputs}个输入汇聚到{n_outputs}个输出（输入/输出比={ratio:.1f}）'
            })
    
    # 模式2: 地址聚合漏斗检测（原有逻辑，但降低阈值）
    recv_map = defaultdict(lambda: {'senders': set(), 'received_txs': [], 'forward_to': defaultdict(int)})
    for _, r in txs.iterrows():
        ts = r['ts']
        ins = r['inputs'] or []
        outs = r['outputs'] or []
        # 每个输出地址归因到所有输入地址集合（简化）
        for o in outs:
            entry = recv_map[o]
            for s in set(ins):
                entry['senders'].add(s)
            entry['received_txs'].append((ts, r['tx_id'], tuple(set(ins))))
    
    # 简化"转出"统计：如果某地址作为输入出现在某交易中，且该交易向单一地址o2大额转出，则视为forward
    addr_out_to = defaultdict(lambda: defaultdict(int))
    for _, r in txs.iterrows():
        ins = r['inputs'] or []
        outs = r['outputs'] or []
        if len(outs)==1:
            o2 = outs[0]
            for a in set(ins):
                addr_out_to[a][o2] += 1
    
    for addr, info in recv_map.items():
        uniq = len(info['senders'])
        if uniq >= min_unique_senders:
            out_map = addr_out_to.get(addr, {})
            if not out_map:
                continue
            dest, cnt = max(out_map.items(), key=lambda x: x[1])
            total = sum(out_map.values())
            forward_ratio = cnt/total if total>0 else 0
            if forward_ratio >= min_forward_ratio:
                # 获取一个代表性的交易ID（使用最近的一笔交易）
                tx_id = info['received_txs'][-1][1] if info['received_txs'] else addr
                score = 1.0 + uniq/100
                rows.append({
                    'tx_id': tx_id,
                    'address': addr, 
                    'unique_senders': uniq, 
                    'forward_ratio': forward_ratio, 
                    'dest': dest, 
                    'funnel_score': score,
                    'risk_score': min(score / 2.0, 1.0),  # 归一化到0-1
                    'reason': f'漏斗地址: 收到来自{uniq}个唯一发送方的资金，{forward_ratio*100:.1f}%转出到{dest[:20]}...'
                })
    
    return pd.DataFrame(rows)
