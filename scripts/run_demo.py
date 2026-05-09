#!/usr/bin/env python
        # scripts/run_demo.py
        import json
        import sys
        import os
        from collections import defaultdict

        # 将 src 目录添加到 Python 路径
        # __file__ 是 'ChainAML-PoC/scripts/run_demo.py'
        # os.path.dirname(__file__) 是 'ChainAML-PoC/scripts'
        # os.path.dirname(os.path.dirname(__file__)) 是 'ChainAML-PoC'
        # os.path.join(..., 'src') 是 'ChainAML-PoC/src'

        # 修正路径：我们希望将 'ChainAML-PoC' 的父目录添加到路径中，
        # 以便 'import src.chainaml' 能够工作，或者更好地，将 'src' 目录添加到路径中。
        # 让我们使用更健壮的方式：

        # '.../ChainAML-PoC/scripts/run_demo.py'
        script_path = os.path.abspath(__file__)
        # '.../ChainAML-PoC/scripts'
        script_dir = os.path.dirname(script_path)
        # '.../ChainAML-PoC'
        project_root = os.path.dirname(script_dir)
        # '.../ChainAML-PoC/src'
        src_dir = os.path.join(project_root, 'src')

        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        try:
            from chainaml.detectors.spray_detector import SprayDetector
            from chainaml.detectors.funnel_detector import FunnelDetector
            from chainaml.detectors.coinjoin_detector import CoinjoinDetector
            from chainaml.detectors.mining_detector import MiningWashDetector
        except ImportError as e:
            print(f"导入错误: {e}")
            print("请确保您在 'ChainAML-PoC' 目录的父目录中运行 'create_poc_project.py'")
            print(f"当前Python路径: {sys.path}")
            sys.exit(1)

        def load_transactions(filepath):
            """
            加载JSON格式的交易数据
            """
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except FileNotFoundError:
                print(f"错误：找不到示例数据文件 '{filepath}'")
                print("请确保 'sample/sample_txs.json' 文件存在。")
                sys.exit(1)
            except json.JSONDecodeError:
                print(f"错误：示例数据文件 '{filepath}' 格式不正确。")
                sys.exit(1)

        def build_tx_lookup(txs):
            """
            创建一个字典以便快速回溯交易
            """
            return {tx['tx_id']: tx for tx in txs}

        def main():
            print("="*50)
            print(" Aegis (神盾) 链上反洗钱 (AML) PoC 演示")
            print("="*50)

            # 定义数据文件路径
            base_dir = project_root
            data_file = os.path.join(base_dir, 'sample', 'sample_txs.json')

            print(f"正在加载示例数据: {data_file}
")
            transactions = load_transactions(data_file)
            tx_lookup = build_tx_lookup(transactions)

            print(f"已加载 {len(transactions)} 笔交易。开始初始化检测器...
")

            # 1. 初始化所有检测器
            spray_detector = SprayDetector()
            funnel_detector = FunnelDetector()
            coinjoin_detector = CoinjoinDetector()
            mining_detector = MiningWashDetector()

            all_alerts = []

            # 2. 遍历所有交易，应用检测器
            print("--- 开始逐笔交易扫描 ---")
            for tx in transactions:
                print(f"正在分析 TX: {tx['tx_id']}...")

                # 应用“逐笔”检测器
                spray_detector.detect(tx)
                funnel_detector.detect(tx)
                coinjoin_detector.detect(tx)

                # 应用需要回溯的检测器
                mining_detector.detect(tx, tx_lookup)

            # 3. 收集所有警报
            all_alerts.extend(spray_detector.get_alerts())
            all_alerts.extend(funnel_detector.get_alerts())
            all_alerts.extend(coinjoin_detector.get_alerts())
            all_alerts.extend(mining_detector.get_alerts())

            print("
--- 扫描完成 ---")

            # 5. 打印最终报告
            if not all_alerts:
                print("
未发现任何高风险洗钱模式。")
            else:
                print(f"
检测到 {len(all_alerts)} 个高风险警报！")
                print("="*50)
                print(" 警报详情：")
                print("="*50)
                for i, alert in enumerate(all_alerts, 1):
                    print(f"
[警报 {i}] - {alert['detector']} (严重性: {alert['severity']})")
                    print(f"  交易ID: {alert['tx_id']}")
                    print(f"  消息: {alert['message']}")

            print("
="*50)
            print("PoC 演示结束。")
            print("注意：本PoC仅演示了基于规则的启发式检测。")
            print("生产系统还需整合图谱分析(GNN)、地址聚类和链下情报。")
            print("="*50)

        if __name__ == "__main__":
            main()