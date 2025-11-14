# src/chainaml/detectors/base_detector.py

class BaseDetector:
    """
    所有检测器的基类
    """
    def __init__(self, config=None):
        self.config = config or {}
        self.alerts = []

    def detect(self, *args, **kwargs):
        """
        子类必须实现此方法
        """
        raise NotImplementedError("Subclass must implement abstract method")

    def get_alerts(self):
        """
        返回检测到的警报
        """
        return self.alerts

    def clear_alerts(self):
        """
        清除警报列表
        """
        self.alerts = []