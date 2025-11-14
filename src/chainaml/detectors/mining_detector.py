# src/chainaml/detectors/mining_detector.py
from .base_detector import BaseDetector
from ..utils.analysis_helpers import calculate_amount_cv

class MiningWashDetector(BaseDetector):
    """
    检测“挖矿洗白”
    特征（PoC简化版）：
    1. 交易的输入来自一个Coinbase交易（即新挖出的币）
    2. 该交易本身是一个“喷洒”行为（大扇出 + 等额）
    """
    def __init__(self, config=None):
        default_config = {
            "min_spray_outputs": 5,
            "max_amount_cv": 0.1 
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)

    def detect(self, tx, tx_lookup):
        """
        检测单个交易是否符合“挖矿洗白”模式
        tx_lookup: 一个 {tx_id: tx_object} 的字典，用于回溯
        """
        inputs = tx.get('inputs', [])
        if not inputs:
            return False

        # 1. 检查输入是否来自Coinbase
        is_from_coinbase = False
        prev_tx_id_source = None
        for inp in inputs:
            prev_tx_id = inp.get('prev_tx_id')
            if prev_tx_id in tx_lookup and tx_lookup[prev_tx_id].get('is_coinbase', False):
                is_from_coinbase = True
                prev_tx_id_source = prev_tx_id
                break

        if not is_from_coinbase:
            return False

        # 2. 检查此交易是否为“喷洒”
        n_outputs = len(tx.get('outputs', []))
        if n_outputs >= self.config['min_spray_outputs']:
            output_amounts = [out['amount'] for out in tx['outputs']]
            cv = calculate_amount_cv(output_amounts)

            if cv <= self.config['max_amount_cv']:
                alert = {
                    "tx_id": tx['tx_id'],
                    "detector": "MiningWashDetector",
                    "message": f"检测到“挖矿洗白”：Coinbase资金（来自 {prev_tx_id_source}）被立刻“喷洒”为 {n_outputs} 笔等额输出 (CV: {cv:.4f})",
                    "severity": "HIGH",
                    "details": {
                        "n_outputs": n_outputs,
                        "amount_cv": cv,
                        "coinbase_source_tx": prev_tx_id_source
                    }
                }
                self.alerts.append(alert)
                return True
        return False