# src/chainaml/detectors/coinjoin_detector.py
from .base_detector import BaseDetector
from ..utils.analysis_helpers import find_equal_outputs

class CoinjoinDetector(BaseDetector):
    """
    检测“混币”（CoinJoin）行为
    特征：
    1. 多输入 (如 > 2)
    2. 多输出 (如 > 2)
    3. 存在多组等额输出
    """
    def __init__(self, config=None):
        default_config = {
            "min_inputs": 3,
            "min_outputs": 3,
            "min_equal_output_groups": 1 # 至少有1组等额输出
        }
        if config:
            default_config.update(config)
        super().__init__(default_config)

    def detect(self, tx):
        """
        检测单个交易是否符合“CoinJoin”模式
        """
        n_inputs = len(tx.get('inputs', []))
        n_outputs = len(tx.get('outputs', []))

        if n_inputs >= self.config['min_inputs'] and n_outputs >= self.config['min_outputs']:
            # 检查等额输出
            equal_outputs = find_equal_outputs(tx['outputs'])

            if len(equal_outputs) >= self.config['min_equal_output_groups']:
                alert = {
                    "tx_id": tx['tx_id'],
                    "detector": "CoinjoinDetector",
                    "message": f"检测到“CoinJoin”样式：{n_inputs}输入, {n_outputs}输出. 发现等额组: {equal_outputs}",
                    "severity": "MEDIUM",
                    "details": {
                        "n_inputs": n_inputs,
                        "n_outputs": n_outputs,
                        "equal_groups": equal_outputs
                    }
                }
                self.alerts.append(alert)
                return True
        return False