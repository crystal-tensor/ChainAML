
from collections import defaultdict
import numpy as np

def equal_amounts(amts, rel_tol=0.005):
    if len(amts) < 2:
        return False
    amts = np.array(amts, dtype=float)
    m = amts.mean()
    if m == 0:
        return False
    return (np.abs(amts - m) / m).max() <= rel_tol

def co_spend_clusters(txs):
    """
    极简共同支出聚类：同一笔交易所有输入地址归于同一簇。
    输入: txs: iterable of dict with 'tx_id','inputs' (list of addr)
    返回: addr->cluster_id 映射
    """
    parent = {}
    def find(x):
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]
    def union(a,b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for t in txs:
        ins = t.get('inputs', [])
        if len(ins) >= 2:
            head = ins[0]
            for addr in ins[1:]:
                union(head, addr)
    # 压缩并规范id
    clusters = {}
    for a in list(parent.keys()):
        clusters[a] = find(a)
    return clusters
