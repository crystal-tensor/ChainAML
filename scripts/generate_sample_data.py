# scripts/generate_sample_data.py
import json
import random
import time
import argparse

def generate_address():
    """生成一个唯一的比特币风格地址"""
    return "bc1q" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=38))

def create_transaction(tx_id, inputs, outputs, is_coinbase=False):
    """创建标准交易结构"""
    # 将inputs和outputs转换为地址数组，金额单独存储
    input_addrs = [inp["from_addr"] for inp in inputs]
    output_addrs = [out["to_addr"] for out in outputs]
    output_amounts = [out["amount"] for out in outputs]
    
    return {
        "tx_id": f"tx_{tx_id}_{int(time.time())}",
        "ts": int(time.time()),
        "is_coinbase": is_coinbase,
        "inputs": input_addrs,
        "outputs": output_addrs,
        "output_amounts": output_amounts
    }

def generate_sample_data(total_txs=10000):
    """生成包含特定洗钱模式的交易数据"""
    transactions = []
    tx_counter = 0

    # 需要额外插入的“特定模式”交易数量：
    # 喷洒(1) + 漏斗(1) + CoinJoin-like(1) + 挖矿链(3) = 6
    SPECIAL_TX_COUNT = 6
    num_normal_txs = max(0, total_txs - SPECIAL_TX_COUNT)

    # --- 1. 正常交易 ---
    for _ in range(num_normal_txs):
        num_inputs = random.randint(1, 4)
        num_outputs = random.randint(1, 3)
        inputs = [{"from_addr": generate_address(), "amount": round(random.uniform(0.1, 5.0), 6)} for _ in range(num_inputs)]
        outputs = [{"to_addr": generate_address(), "amount": round(random.uniform(0.1, 2.0), 6)} for _ in range(num_outputs)]
        transactions.append(create_transaction(tx_counter, inputs, outputs))
        tx_counter += 1

    # --- 2. "喷洒" (Spraying) 交易 ---
    sprayer_addr = generate_address()
    spray_inputs = [{"from_addr": generate_address(), "amount": 100.0}]
    spray_outputs = []
    num_spray_outputs = 60
    total_amount = 100.0
    base_amount = total_amount / num_spray_outputs
    
    # 生成60个几乎相等的输出
    for i in range(num_spray_outputs):
        # 添加很小的随机变化，但保持总金额不变
        if i == num_spray_outputs - 1:
            # 最后一个输出调整到确保总金额正确
            amount = total_amount - sum([out["amount"] for out in spray_outputs])
        else:
            amount = round(base_amount + random.uniform(-0.001, 0.001), 6)
        spray_outputs.append({"to_addr": generate_address(), "amount": amount})
    transactions.append(create_transaction(tx_counter, spray_inputs, spray_outputs))
    tx_counter += 1
    print(f"Generated 'Spraying' transaction with {num_spray_outputs} outputs.")

    # --- 3. "漏斗" (Funneling) 交易 ---
    funnel_target_addr = generate_address()
    funnel_inputs = []
    num_funnel_inputs = 85
    total_funnel_amount = 0
    for _ in range(num_funnel_inputs):
        amount = round(random.uniform(0.1, 1.0), 6)
        total_funnel_amount += amount
        funnel_inputs.append({"from_addr": generate_address(), "amount": amount})
    funnel_outputs = [{"to_addr": funnel_target_addr, "amount": total_funnel_amount}]
    transactions.append(create_transaction(tx_counter, funnel_inputs, funnel_outputs))
    tx_counter += 1
    print(f"Generated 'Funneling' transaction with {num_funnel_inputs} inputs.")

    # --- 4. CoinJoin-like 交易 ---
    coinjoin_amount = 0.1  # 等额输出
    num_coinjoin_participants = 5
    cj_inputs = [{"from_addr": generate_address(), "amount": coinjoin_amount + round(random.uniform(0.001, 0.005), 6)} for _ in range(num_coinjoin_participants)]
    cj_outputs = [{"to_addr": generate_address(), "amount": coinjoin_amount} for _ in range(num_coinjoin_participants)]
    # 添加一个找零输出
    cj_outputs.append({"to_addr": generate_address(), "amount": round(random.uniform(0.001, 0.005), 6)})
    transactions.append(create_transaction(tx_counter, cj_inputs, cj_outputs))
    tx_counter += 1
    print(f"Generated 'CoinJoin-like' transaction with {num_coinjoin_participants} equal outputs of {coinjoin_amount}.")

    # --- 5. 挖矿"洗白" (Mining Wash) ---
    # a) Coinbase交易 (挖出新币)
    miner_addr = generate_address()
    coinbase_tx = create_transaction(tx_counter, [], [{"to_addr": miner_addr, "amount": 6.25}], is_coinbase=True)
    transactions.append(coinbase_tx)
    tx_counter += 1
    
    # b) 几跳正常转移
    intermediate_addr1 = generate_address()
    transfer1 = create_transaction(tx_counter, [{"from_addr": miner_addr, "amount": 6.25}], [{"to_addr": intermediate_addr1, "amount": 6.25}])
    transactions.append(transfer1)
    tx_counter += 1
    
    # c) 最后一跳进行大规模扇出（喷洒）
    wash_inputs = [{"from_addr": intermediate_addr1, "amount": 6.25}]
    wash_outputs = []
    num_wash_outputs = 50
    wash_total_amount = 6.25
    wash_base_amount = wash_total_amount / num_wash_outputs
    
    for i in range(num_wash_outputs):
        if i == num_wash_outputs - 1:
            # 最后一个输出调整到确保总金额正确
            amount = wash_total_amount - sum([out["amount"] for out in wash_outputs])
        else:
            amount = round(wash_base_amount + random.uniform(-0.0001, 0.0001), 6)
        wash_outputs.append({"to_addr": generate_address(), "amount": amount})
    wash_tx = create_transaction(tx_counter, wash_inputs, wash_outputs)
    transactions.append(wash_tx)
    tx_counter += 1
    print(f"Generated 'Mining Wash' chain: Coinbase -> Transfer -> Spray with {num_wash_outputs} outputs.")

    random.shuffle(transactions)

    with open("data/sample_txs.json", "w") as f:
        json.dump(transactions, f, indent=2)
    
    print(f"\nTotal {len(transactions)} transactions generated and saved to 'data/sample_txs.json'.")


if __name__ == "__main__":
    import os
    if not os.path.exists("data"):
        os.makedirs("data")
    parser = argparse.ArgumentParser(description="Generate synthetic blockchain transactions for AML PoC.")
    parser.add_argument("--total", type=int, default=10000, help="Total number of transactions to generate (including special pattern txs).")
    args = parser.parse_args()
    generate_sample_data(total_txs=args.total)