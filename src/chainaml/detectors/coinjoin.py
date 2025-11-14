
# 模块顶层
import pandas as pd
import numpy as np
from chainaml.heuristics import equal_amounts

def detect_coinjoin_like(txs, min_in=3, min_out=3, rel_tol=0.05):
    """
    CoinJoin/混币模式启发式：
      - inputs数量>=min_in 且 outputs数量>=min_out
      - 输出金额近似相等（容差rel_tol，放宽到5%）
    输入: DataFrame 列 ['tx_id','inputs','outputs','output_amounts']
    输出: DataFrame [tx_id, n_in, n_out, coinjoin_score, reason]
    """
    rows = []
    for _, r in txs.iterrows():
        ins = r['inputs'] or []
        outs = r['outputs'] or []
        amts = r['output_amounts'] or []
        
        # 基本条件：输入和输出数量满足要求
        if len(ins) >= min_in and len(outs) >= min_out and len(outs)==len(amts):
            # 检查金额是否近似相等
            if equal_amounts(amts, rel_tol=rel_tol):
                rows.append({
                    'tx_id': r['tx_id'], 
                    'n_in': len(ins), 
                    'n_out': len(outs), 
                    'coinjoin_score': 1.0 + len(outs)/20,
                    'reason': f'混币交易: {len(ins)}个输入，{len(outs)}个输出，输出金额近似相等（类似CoinJoin模式）'
                })
            # 如果金额不完全相等，但输入输出数量都较多，也可能是混币模式
            elif len(ins) >= 5 and len(outs) >= 5:
                # 计算金额的变异系数
                if len(amts) > 0 and np.mean(amts) > 0:
                    cv = np.std(amts) / np.mean(amts)
                    # 如果变异系数较小（<0.2），也认为是混币
                    if cv < 0.2:
                        rows.append({
                            'tx_id': r['tx_id'], 
                            'n_in': len(ins), 
                            'n_out': len(outs), 
                            'coinjoin_score': 1.0 + len(outs)/30,
                            'reason': f'混币交易: {len(ins)}个输入，{len(outs)}个输出，金额变异系数CV={cv:.3f}（疑似混币模式）'
                        })
    return pd.DataFrame(rows)
