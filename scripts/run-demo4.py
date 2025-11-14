import json, pandas as pd
from pathlib import Path
import sys

base = Path(__file__).resolve().parents[1]
sys.path.append(str(base / "src"))
from chainaml.pipeline import run_all
data_path = base / "data" / "sample_txs.json"
sample_path = base / "sample" / "sample_txs.json"
txs_path = data_path if data_path.exists() else sample_path
df = pd.read_json(txs_path)
if 'ts' not in df.columns:
    df['ts'] = range(len(df))
res = run_all(df)

print("\n=== Combined Risk Scoreboard ===")
print(res['scoreboard'].to_string(index=False))