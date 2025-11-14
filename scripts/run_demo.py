# 模块顶层
import json, pandas as pd
from pathlib import Path
import sys

# 首先设置路径，然后导入模块
base = Path(__file__).resolve().parents[1]
sys.path.append(str(base / "src"))
from chainaml.pipeline import run_all
txs_path = base / "sample" / "sample_txs.json"
df = pd.read_json(txs_path)
res = run_all(df)

print("\n=== Combined Risk Scoreboard ===")
print(res['scoreboard'].to_string(index=False))
