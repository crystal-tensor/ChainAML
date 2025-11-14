
import pandas as pd

def detect_mining_launder(txs, lookahead=3, fanout_thresh=3):
    """
    挖矿洗白检测：包括两种模式
    1. Coinbase交易下游扇出检测
    2. 直接检测Coinbase交易（即使下游扇出较小）
    输入: DataFrame 列 ['tx_id','is_coinbase','outputs','ts']
    输出: DataFrame [tx_id, hop_fanout, mining_score, reason]
    """
    # 构造地址->后续tx索引
    addr_to_txs = {}
    for idx, r in txs.iterrows():
        for a in (r['outputs'] or []):
            addr_to_txs.setdefault(a, []).append(idx)
    rows = []
    
    for i, r in txs.iterrows():
        if not r.get('is_coinbase', False):
            continue
        
        # 模式1: 检测Coinbase交易的下游扇出
        frontier = set(r['outputs'] or [])
        visited = set()
        hop = 0
        fanout = 0
        while frontier and hop < lookahead:
            nxt = set()
            for a in list(frontier):
                visited.add(a)
                for j in addr_to_txs.get(a, []):
                    fanout += len(txs.iloc[j]['outputs'] or [])
                    for o in (txs.iloc[j]['outputs'] or []):
                        if o not in visited:
                            nxt.add(o)
            frontier = nxt
            hop += 1
        
        # 如果扇出达到阈值，标记为可疑
        if fanout >= fanout_thresh:
            score = 1.0 + fanout/50.0
            rows.append({
                'tx_id': r['tx_id'], 
                'hop_fanout': fanout, 
                'mining_score': score,
                'risk_score': min(score / 2.0, 1.0),  # 归一化到0-1
                'reason': f'挖矿洗钱: Coinbase交易，下游{lookahead}跳内总扇出{fanout}个地址（可能用于洗白挖矿奖励）'
            })
        # 模式2: 即使扇出较小，Coinbase交易本身也值得关注
        # 修改：所有Coinbase交易都应该被检测到，因为它们是挖矿奖励
        else:
            n_outputs = len(r.get('outputs', []))
            if n_outputs >= 3:
                score = 1.0 + n_outputs / 20.0
                rows.append({
                    'tx_id': r['tx_id'],
                    'hop_fanout': n_outputs,
                    'mining_score': score,
                    'risk_score': min(score / 2.0, 1.0),  # 归一化到0-1
                    'reason': f'挖矿交易: Coinbase交易，直接输出到{n_outputs}个地址（需关注后续流向）'
                })
            else:
                # 即使输出较少，Coinbase交易也应该被标记（可能是早期挖矿或特殊模式）
                score = 1.0 + max(fanout, n_outputs) / 30.0
                rows.append({
                    'tx_id': r['tx_id'],
                    'hop_fanout': max(fanout, n_outputs),
                    'mining_score': score,
                    'risk_score': min(score / 2.0, 1.0),  # 归一化到0-1
                    'reason': f'挖矿交易: Coinbase交易，输出到{n_outputs}个地址，下游{lookahead}跳内扇出{fanout}（挖矿奖励需关注）'
                })
    
    result_df = pd.DataFrame(rows)
    if len(result_df) > 0:
        # 按风险评分排序，只返回前50个
        result_df = result_df.sort_values('risk_score', ascending=False)
        result_df = result_df.head(50)
    
    return result_df
