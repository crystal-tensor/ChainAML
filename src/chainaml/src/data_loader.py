# src/data_loader.py
import json

def load_transactions(filepath="data/sample_txs.json"):
    """从JSON文件加载交易数据"""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Data file not found at '{filepath}'.")
        print("Please run 'python scripts/generate_sample_data.py' first.")
        return None