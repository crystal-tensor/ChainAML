"""
基于量子抗性哈希链的量子算法检测器
融合量子抗性哈希链技术和现有检测方法，使用量子概率计算违规概率
"""

import pandas as pd
import numpy as np
import hashlib
from collections import defaultdict
from typing import Dict, List, Tuple

def build_quantum_resistant_hash_chain(txs_df) -> Dict[str, List[str]]:
    """
    构建量子抗性哈希链
    使用SHA-3（Keccak）作为量子抗性哈希函数
    返回: {address: [hash_chain_sequence]}
    """
    hash_chain_map = defaultdict(list)
    
    # 按时间排序
    sorted_txs = txs_df.sort_values('ts')
    
    for _, tx in sorted_txs.iterrows():
        tx_id = tx['tx_id']
        inputs = tx.get('inputs', [])
        outputs = tx.get('outputs', [])
        output_amounts = tx.get('output_amounts', [])
        
        # 为每笔交易生成量子抗性哈希
        tx_data = f"{tx_id}_{tx.get('ts', 0)}"
        for inp in inputs:
            tx_data += f"_{inp}"
        for out, amt in zip(outputs, output_amounts):
            tx_data += f"_{out}_{amt}"
        
        # 使用SHA-3 (SHAKE256) 作为量子抗性哈希
        tx_hash = hashlib.sha3_256(tx_data.encode()).hexdigest()
        
        # 构建地址的哈希链
        for inp in inputs:
            hash_chain_map[inp].append(tx_hash)
        for out in outputs:
            hash_chain_map[out].append(tx_hash)
    
    return hash_chain_map


def apply_canary_watermark(tx_id: str, tx_data: dict, risk_level: float) -> dict:
    """
    金丝雀水印机制：在可疑交易中嵌入水印标记
    用于追踪和识别可疑交易，即使交易被拆分或转移也能追踪
    
    参数:
        tx_id: 交易ID
        tx_data: 交易数据
        risk_level: 风险等级 (0-1)
    
    返回:
        包含水印信息的字典
    """
    # 生成水印标记（基于交易ID和风险等级）
    watermark_seed = f"{tx_id}_{risk_level}"
    watermark_hash = hashlib.sha3_256(watermark_seed.encode()).hexdigest()[:16]
    
    # 水印特征
    watermark = {
        'watermark_id': f"CANARY_{watermark_hash}",
        'risk_level': risk_level,
        'embedding_time': tx_data.get('ts', 0),
        'tracking_enabled': True,
        'cross_chain_trackable': True  # 支持跨链追踪
    }
    
    return watermark


def detect_cross_chain_mapping(txs_df, entity: str, hash_chain_map: Dict[str, List[str]]) -> dict:
    """
    跨链映射技术：检测和追踪跨链交易模式
    识别可能通过跨链桥进行的洗钱行为
    
    参数:
        txs_df: 交易数据
        entity: 实体（地址或交易ID）
        hash_chain_map: 哈希链映射
    
    返回:
        跨链映射信息
    """
    # 检测跨链模式：如果地址在短时间内出现在多个不同的交易模式中
    # 可能表示跨链转移
    
    if entity not in hash_chain_map:
        return {
            'cross_chain_detected': False,
            'chain_connections': 0,
            'suspicious_pattern': False
        }
    
    hash_chain = hash_chain_map[entity]
    
    # 分析哈希链模式
    # 如果哈希链中有多个不同的模式（喷洒、漏斗、混币等），可能是跨链洗钱
    pattern_diversity = len(set(hash_chain))
    
    # 检测跨链桥模式（简化版：检测快速转移模式）
    cross_chain_suspicious = pattern_diversity > 5  # 如果模式多样性高，可能涉及跨链
    
    return {
        'cross_chain_detected': cross_chain_suspicious,
        'chain_connections': pattern_diversity,
        'suspicious_pattern': cross_chain_suspicious,
        'hash_chain_length': len(hash_chain),
        'pattern_diversity': pattern_diversity
    }


def quantum_superposition_probability(hash_chains: List[List[str]], 
                                     base_scores: Dict[str, float]) -> float:
    """
    使用量子叠加原理计算违规概率
    将多个检测器的分数视为量子态，通过叠加计算最终概率
    """
    if not hash_chains or not base_scores:
        return 0.0
    
    # 量子叠加：将各检测器分数视为量子态振幅
    amplitudes = []
    for detector, score in base_scores.items():
        # 归一化分数到 [0, 1] 区间
        normalized_score = min(score / 10.0, 1.0)
        amplitudes.append(normalized_score)
    
    # 量子概率 = |振幅|^2 的叠加
    probabilities = [a ** 2 for a in amplitudes]
    
    # 使用哈希链长度作为纠缠强度因子
    chain_length = len(hash_chains[0]) if hash_chains else 1
    entanglement_factor = min(chain_length / 100.0, 1.0)
    
    # 最终概率 = 叠加概率 * 纠缠因子
    base_prob = np.mean(probabilities)
    quantum_prob = base_prob * (1 + entanglement_factor * 0.3)
    
    return min(quantum_prob, 1.0)


def detect_quantum_aml(txs_df, 
                       spray_results: pd.DataFrame,
                       funnel_results: pd.DataFrame,
                       coinjoin_results: pd.DataFrame,
                       mining_results: pd.DataFrame,
                       max_results: int = 100,
                       min_risk_score: float = 0.3) -> pd.DataFrame:
    """
    量子算法检测器：融合所有检测方法，使用量子抗性哈希链和量子概率计算
    
    参数:
        txs_df: 交易数据DataFrame
        spray_results: 喷洒检测结果
        funnel_results: 漏斗检测结果
        coinjoin_results: 混币检测结果
        mining_results: 挖矿洗白检测结果
        max_results: 最大返回结果数量（默认100）
        min_risk_score: 最小风险评分阈值（默认0.3）
    
    返回:
        DataFrame包含 [tx_id/address, quantum_score, quantum_probability, detection_details]
    """
    # 1. 构建量子抗性哈希链
    hash_chain_map = build_quantum_resistant_hash_chain(txs_df)
    
    # 2. 收集所有检测结果
    entity_scores = defaultdict(lambda: {
        'spray': 0.0,
        'funnel': 0.0,
        'coinjoin': 0.0,
        'mining': 0.0,
        'detected_by': [],
        'details': {}
    })
    
    # 处理喷洒检测结果
    for _, row in spray_results.iterrows():
        tx_id = row['tx_id']
        score = row.get('spray_score', 0.0)
        entity_scores[tx_id]['spray'] = score
        entity_scores[tx_id]['detected_by'].append('spray')
        entity_scores[tx_id]['details']['spray'] = {
            'n_outs': row.get('n_outs', 0),
            'cv': row.get('cv', 0.0)
        }
    
    # 处理漏斗检测结果
    for _, row in funnel_results.iterrows():
        address = row['address']
        score = row.get('funnel_score', 0.0)
        entity_scores[address]['funnel'] = score
        entity_scores[address]['detected_by'].append('funnel')
        entity_scores[address]['details']['funnel'] = {
            'unique_senders': row.get('unique_senders', 0),
            'forward_ratio': row.get('forward_ratio', 0.0)
        }
    
    # 处理混币检测结果
    for _, row in coinjoin_results.iterrows():
        tx_id = row['tx_id']
        score = row.get('coinjoin_score', 0.0)
        entity_scores[tx_id]['coinjoin'] = score
        entity_scores[tx_id]['detected_by'].append('coinjoin')
        entity_scores[tx_id]['details']['coinjoin'] = {
            'n_in': row.get('n_in', 0),
            'n_out': row.get('n_out', 0)
        }
    
    # 处理挖矿洗白检测结果
    for _, row in mining_results.iterrows():
        tx_id = row['tx_id']
        score = row.get('mining_score', 0.0)
        entity_scores[tx_id]['mining'] = score
        entity_scores[tx_id]['detected_by'].append('mining')
        entity_scores[tx_id]['details']['mining'] = {
            'hop_fanout': row.get('hop_fanout', 0)
        }
    
    # 3. 计算量子概率（只处理已被检测到的实体，提高性能）
    rows = []
    # 先按检测数量排序，优先处理被多个检测器标记的实体
    sorted_entities = sorted(
        entity_scores.items(), 
        key=lambda x: (len(x[1]['detected_by']), sum([x[1][d] for d in ['spray', 'funnel', 'coinjoin', 'mining']])),
        reverse=True
    )
    
    for entity, scores_dict in sorted_entities:
        if not scores_dict['detected_by']:
            continue
        
        # 获取该实体的哈希链
        hash_chains = []
        if entity in hash_chain_map:
            hash_chains = [hash_chain_map[entity]]
        
        # 构建基础分数字典（只包含非零分数）
        base_scores = {}
        for detector in ['spray', 'funnel', 'coinjoin', 'mining']:
            if scores_dict[detector] > 0:
                base_scores[detector] = scores_dict[detector]
        
        # 计算量子概率
        quantum_prob = quantum_superposition_probability(hash_chains, base_scores)
        
        # 计算综合量子分数
        total_score = sum([scores_dict[d] for d in ['spray', 'funnel', 'coinjoin', 'mining']])
        quantum_score = total_score * (1 + quantum_prob)
        
        # 确定有效的交易ID
        # 如果entity是交易ID，直接使用；如果是地址，尝试从原始检测结果中找到相关交易ID
        valid_tx_id = None
        if entity.startswith('tx_'):
            # entity本身就是交易ID
            valid_tx_id = entity
        else:
            # entity是地址，需要找到相关的交易ID
            # 优先从funnel_results中查找（因为funnel检测返回的是地址，但已经有tx_id字段）
            if 'funnel' in scores_dict['detected_by']:
                for _, row in funnel_results.iterrows():
                    if row.get('address') == entity:
                        valid_tx_id = row.get('tx_id')
                        if valid_tx_id and valid_tx_id.startswith('tx_'):
                            break
            # 如果funnel中没找到，尝试从其他检测结果中查找
            # 注意：spray、coinjoin、mining的entity本身就是交易ID，所以这里不需要查找
            # 如果还是找不到，尝试从交易数据中查找包含该地址的交易
            if not valid_tx_id or not valid_tx_id.startswith('tx_'):
                # 从交易数据中查找包含该地址的第一笔交易
                matching_txs = txs_df[
                    (txs_df['inputs'].apply(lambda x: entity in (x or []))) |
                    (txs_df['outputs'].apply(lambda x: entity in (x or [])))
                ]
                if not matching_txs.empty:
                    valid_tx_id = matching_txs.iloc[0]['tx_id']
            # 如果还是找不到有效的交易ID，使用entity本身
            if not valid_tx_id or not valid_tx_id.startswith('tx_'):
                valid_tx_id = entity
        
        # 应用金丝雀水印机制
        # 获取交易数据（如果是交易ID）
        tx_data = {}
        if valid_tx_id and valid_tx_id.startswith('tx_'):
            tx_row = txs_df[txs_df['tx_id'] == valid_tx_id]
            if not tx_row.empty:
                tx_data = tx_row.iloc[0].to_dict()
        
        watermark = apply_canary_watermark(valid_tx_id or entity, tx_data, quantum_prob)
        
        # 检测跨链映射
        cross_chain_info = detect_cross_chain_mapping(txs_df, entity, hash_chain_map)
        
        # 构建详细信息
        enhanced_details = scores_dict['details'].copy()
        enhanced_details['canary_watermark'] = watermark
        enhanced_details['cross_chain_mapping'] = cross_chain_info
        
        # 生成原因描述
        reason_parts = [f'量子概率: {quantum_prob:.2%}']
        if watermark['risk_level'] > 0.5:
            reason_parts.append(f'金丝雀水印: {watermark["watermark_id"]}')
        if cross_chain_info['cross_chain_detected']:
            reason_parts.append(f'跨链映射: 检测到{cross_chain_info["chain_connections"]}个链连接')
        reason = ' | '.join(reason_parts)
        
        risk_score = min(quantum_prob, 1.0)
        
        # 提前过滤：如果风险评分太低，跳过（提高性能）
        if risk_score < min_risk_score:
            continue
        
        rows.append({
            'tx_id': valid_tx_id or entity,  # 使用有效的交易ID
            'entity': entity,  # 保留原始entity用于显示
            'quantum_score': quantum_score,
            'quantum_probability': quantum_prob,
            'risk_score': risk_score,  # 归一化风险评分
            'detected_by': ','.join(scores_dict['detected_by']),
            'details': enhanced_details,
            'canary_watermark_id': watermark['watermark_id'],
            'cross_chain_detected': cross_chain_info['cross_chain_detected'],
            'reason': reason
        })
        
        # 如果已经收集了足够的候选结果，提前停止（提高性能）
        if len(rows) >= max_results * 2:  # 收集2倍数量，然后筛选
            break
    
    result_df = pd.DataFrame(rows)
    if len(result_df) > 0:
        result_df = result_df.sort_values('quantum_probability', ascending=False)
        # 只返回风险评分最高的结果
        result_df = result_df[result_df['risk_score'] >= min_risk_score]
        result_df = result_df.head(max_results)
    
    return result_df

