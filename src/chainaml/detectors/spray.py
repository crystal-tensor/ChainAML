
import pandas as pd
import numpy as np

def detect_spraying(txs, min_outputs=20, cv_thresh=0.05):
    """
    简易喷洒特征：
      - 单笔交易输出地址数量>=min_outputs
      - 输出金额变异系数CV<=cv_thresh（金额接近均分）
    入参txs: DataFrame列包含 ['tx_id','outputs','output_amounts']
    返回: DataFrame [tx_id, n_outs, cv, spray_score]
    """
    rows = []
    for _, r in txs.iterrows():
        outs = r['outputs']
        amts = r['output_amounts']
        if not isinstance(outs, list) or not isinstance(amts, list):
            continue
        n_outs = len(outs)
        if n_outs >= min_outputs and len(amts) == n_outs:
            m = np.mean(amts) if amts else 0
            s = np.std(amts) if amts else 0
            cv = (s/m) if m>0 else 1.0
            if cv <= cv_thresh:
                rows.append({
                    'tx_id': r['tx_id'], 
                    'n_outs': n_outs, 
                    'cv': cv, 
                    'spray_score': 1.0 + (min_outputs/n_outs),
                    'reason': f'喷洒交易: {n_outs}个输出，金额变异系数CV={cv:.4f}（接近等额分配）'
                })
    return pd.DataFrame(rows)
