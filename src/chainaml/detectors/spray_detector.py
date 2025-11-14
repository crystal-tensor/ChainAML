# src/chainaml/detectors/spray_detector.py
from .base_detector import BaseDetector
from ..utils.analysis_helpers import calculate_amount_cv

class SprayDetector(BaseDetector):
    """
    检测“喷洒”（Spraying）行为
    特征：
    1. 单一（或少量）输入
    2. 大量（如 > 20）输出
    3. 输出金额高度相似（低CV值）
    """
    def __init__(self, config=None):
        default_config = {
            "min_outputs": 20,
            "max_inputs": 2,
            "max_amount_cv": 0.1 # CV值小于0.1，视为高度等额
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)

    def detect(self, tx):
        """
        检测单个交易是否符合“喷洒”模式
        """
        n_inputs = len(tx.get('inputs', []))
        n_outputs = len(tx.get('outputs', []))

        if n_inputs <= self.config['max_inputs'] and n_outputs >= self.config['min_outputs']:
            # 进一步检查金额
            output_amounts = [out['amount'] for out in tx['outputs']]
            cv = calculate_amount_cv(output_amounts)

            if cv <= self.config['max_amount_cv']:
                alert = {
                    "tx_id": tx['tx_id'],
                    "detector": "SprayDetector",
                    "message": f"检测到“喷洒”行为：{n_inputs}个输入, {n_outputs}个输出, 金额CV: {cv:.4f}",
                    "severity": "HIGH",
                    "details": {
                        "n_inputs": n_inputs,
                        "n_outputs": n_outputs,
                        "amount_cv": cv
                    }
                }
                self.alerts.append(alert)
                return True
        return False