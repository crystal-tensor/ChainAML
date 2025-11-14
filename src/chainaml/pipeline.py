
import pandas as pd
from chainaml.detectors.spray import detect_spraying
from chainaml.detectors.funnel import detect_funneling
from chainaml.detectors.coinjoin import detect_coinjoin_like
from chainaml.detectors.mining import detect_mining_launder
from chainaml.risk_scoring import combine_scores

def run_all(txs_df, config=None):
    """
    运行所有检测器
    
    Args:
        txs_df: 交易数据DataFrame
        config: 可选的配置字典，包含各检测器的参数
            - spray: {min_outputs, cv_thresh}
            - funnel: {min_unique_senders, min_forward_ratio, window_seconds}
            - coinjoin: {min_in, min_out, rel_tol}
            - mining: {lookahead, fanout_thresh}
    """
    if config is None:
        config = {}
    
    # 喷洒检测 - 使用更宽松的阈值以检测更多异常
    spray_config = config.get('spray', {})
    spray = detect_spraying(
        txs_df,
        min_outputs=spray_config.get('min_outputs', 10),  # 从20降到10
        cv_thresh=spray_config.get('cv_thresh', 0.1)  # 从0.05放宽到0.1
    )
    
    # 漏斗检测 - 使用更宽松的阈值，包括单笔交易检测
    funnel_config = config.get('funnel', {})
    funnel = detect_funneling(
        txs_df,
        min_unique_senders=funnel_config.get('min_unique_senders', 5),  # 从10降到5
        min_forward_ratio=funnel_config.get('min_forward_ratio', 0.5),  # 从0.6降到0.5
        min_inputs_single_tx=funnel_config.get('min_inputs_single_tx', 4),  # 单笔交易检测阈值（从5降到4）
        window_seconds=funnel_config.get('window_seconds', 3600*6)
    )
    
    # 混币检测 - 使用更宽松的阈值
    coinjoin_config = config.get('coinjoin', {})
    coinj = detect_coinjoin_like(
        txs_df,
        min_in=coinjoin_config.get('min_in', 3),  # 保持3
        min_out=coinjoin_config.get('min_out', 3),  # 保持3
        rel_tol=coinjoin_config.get('rel_tol', 0.05)  # 从0.01放宽到0.05（5%）
    )
    
    # 挖矿洗钱检测 - 使用更宽松的阈值
    mining_config = config.get('mining', {})
    mining = detect_mining_launder(
        txs_df,
        lookahead=mining_config.get('lookahead', 3),
        fanout_thresh=mining_config.get('fanout_thresh', 3)  # 从5降到3
    )
    
    scoreboard = combine_scores(spray, funnel, coinj, mining)
    return {'spray': spray, 'funnel': funnel, 'coinjoin': coinj, 'mining': mining, 'scoreboard': scoreboard}
