# src/chainaml/detectors/funnel_detector.py
from .base_detector import BaseDetector

class FunnelDetector(BaseDetector):
    """
    检测“漏斗”（Funneling）行为
    特征：
    1. 单一（或少量）输出
    2. 大量（如 > 20）输入
    3. 输入来源高度分散（PoC中简化为输入数量）
    """
    def __init__(self, config=None):
        default_config = {
            "min_inputs": 20,
            "max_outputs": 2
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)

    def detect(self, tx):
        """
        检测单个交易是否符合“漏斗”模式
        """
        n_inputs = len(tx.get('inputs', []))
        n_outputs = len(tx.get('outputs', []))

        if n_inputs >= self.config['min_inputs'] and n_outputs <= self.config['max_outputs']:
            alert = {
                "tx_id": tx['tx_id'],
                "detector": "FunnelDetector",
                "message": f"检测到“漏斗”行为：{n_inputs}个输入, {n_outputs}个输出",
                "severity": "HIGH",
                "details": {
                    "n_inputs": n_inputs,
                    "n_outputs": n_outputs
                }
            }
            self.alerts.append(alert)
            return True
        return False