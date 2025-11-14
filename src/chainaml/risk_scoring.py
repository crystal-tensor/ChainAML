
import pandas as pd

def combine_scores(spray_df, funnel_df, coinjoin_df, mining_df, weights=None, topk=10):
    """
    将不同检测源的信号合并为[entity, score]。
    entity 可以是 tx_id 或 address，简单合并后仅做演示。
    """
    if weights is None:
        weights = {'spray':1.0, 'funnel':1.2, 'coinjoin':0.8, 'mining':1.0}

    rows = []
    for _,r in spray_df.iterrows():
        rows.append((r['tx_id'], weights['spray']*r.get('spray_score',1.0), 'spray'))
    for _,r in funnel_df.iterrows():
        # funnel现在也包含tx_id字段，优先使用tx_id
        entity = r.get('tx_id', r.get('address', 'unknown'))
        rows.append((entity, weights['funnel']*r.get('funnel_score',1.0), 'funnel'))
    for _,r in coinjoin_df.iterrows():
        rows.append((r['tx_id'], weights['coinjoin']*r.get('coinjoin_score',1.0), 'coinjoin'))
    for _,r in mining_df.iterrows():
        rows.append((r['tx_id'], weights['mining']*r.get('mining_score',1.0), 'mining'))

    df = pd.DataFrame(rows, columns=['entity','score','detection_type'])
    # 按entity分组，计算总分和检测类型列表
    grouped = df.groupby('entity').agg({
        'score': 'sum',
        'detection_type': lambda x: list(set(x))
    }).reset_index()
    grouped = grouped.sort_values('score', ascending=False).head(topk)
    
    # 添加reason字段
    def generate_reason(row):
        types = row['detection_type']
        type_names = {
            'spray': '喷洒',
            'funnel': '漏斗',
            'coinjoin': '混币',
            'mining': '挖矿洗钱'
        }
        type_str = '、'.join([type_names.get(t, t) for t in types])
        return f'综合风险评分: 检测到{type_str}模式，综合风险评分{row["score"]:.2f}'
    
    grouped['reason'] = grouped.apply(generate_reason, axis=1)
    # 计算归一化的风险评分（0-1之间）
    if len(grouped) > 0 and grouped['score'].max() > 0:
        grouped['risk_score'] = grouped['score'] / grouped['score'].max()
    else:
        grouped['risk_score'] = grouped['score']
    
    # 重命名entity为tx_id以保持一致性
    grouped = grouped.rename(columns={'entity': 'tx_id'})
    
    return grouped[['tx_id', 'risk_score', 'score', 'reason', 'detection_type']]
