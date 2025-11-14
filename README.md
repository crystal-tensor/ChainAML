# Aegis (神盾) 链上反洗钱 (AML) PoC

这是一个概念验证 (PoC) 项目，用于演示基于《每日经济新闻》报道的先进反洗钱技术。

## 演示的检测器：

1.  **SprayDetector**: 检测“喷洒”行为（大额拆分）
2.  **FunnelDetector**: 检测“漏斗”行为（小额归集）
3.  **CoinjoinDetector**: 检测“混币”样式（等额输出）
4.  **MiningWashDetector**: 检测“挖矿洗白”（Coinbase资金+喷洒）

## 如何运行

1.  **安装依赖 (numpy):**
    ```bash
    pip install -r requirements.txt
    ```

2.  **运行演示:**
    ```bash
    python scripts/run_demo.py
    ```