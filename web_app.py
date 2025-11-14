"""
Web应用后端：提供反洗钱检测API和页面服务
"""

import os
import sys
import json
import pandas as pd
import socket
import subprocess
import time
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# 添加src目录到路径
base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir / "src"))

from chainaml.pipeline import run_all
from chainaml.detectors.quantum import detect_quantum_aml

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)

# 全局变量存储检测结果
detection_results = None
txs_data = None

def load_transactions():
    """加载交易数据"""
    global txs_data
    data_path = base_dir / "data" / "sample_txs.json"
    sample_path = base_dir / "sample" / "sample_txs.json"
    
    txs_path = data_path if data_path.exists() else sample_path
    if not txs_path.exists():
        return None
    
    with open(txs_path, 'r', encoding='utf-8') as f:
        txs_data = json.load(f)
    
    df = pd.DataFrame(txs_data)
    if 'ts' not in df.columns:
        df['ts'] = range(len(df))
    
    return df

def run_all_detections():
    """运行所有检测方法"""
    global detection_results
    
    df = load_transactions()
    if df is None:
        return None
    
    # 运行基础四类检测
    results = run_all(df)
    
    # 运行量子算法检测，限制返回50个结果
    quantum_results = detect_quantum_aml(
        df,
        results['spray'],
        results['funnel'],
        results['coinjoin'],
        results['mining'],
        max_results=50,
        min_risk_score=0.3
    )
    
    results['quantum'] = quantum_results
    
    # 转换为JSON可序列化格式，处理空DataFrame的情况
    def df_to_records(df):
        if df is None or df.empty:
            return []
        # 处理detection_type列（可能是list类型）
        df_copy = df.copy()
        if 'detection_type' in df_copy.columns:
            df_copy['detection_type'] = df_copy['detection_type'].apply(lambda x: x if isinstance(x, list) else [x] if x else [])
        return df_copy.to_dict('records')
    
    detection_results = {
        'spray': df_to_records(results['spray']),
        'funnel': df_to_records(results['funnel']),
        'coinjoin': df_to_records(results['coinjoin']),
        'mining': df_to_records(results['mining']),
        'quantum': df_to_records(results['quantum']),
        'scoreboard': df_to_records(results['scoreboard'])
    }
    
    return detection_results

@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/api/detections', methods=['GET'])
def get_detections():
    """获取所有检测结果"""
    if detection_results is None:
        run_all_detections()
    
    if detection_results is None:
        return jsonify({'error': '无法加载交易数据'}), 500
    
    return jsonify(detection_results)

@app.route('/api/detection/<detection_type>', methods=['GET'])
def get_detection_by_type(detection_type):
    """获取特定类型的检测结果"""
    if detection_results is None:
        run_all_detections()
    
    if detection_results is None:
        return jsonify({'error': '无法加载交易数据'}), 500
    
    if detection_type not in detection_results:
        return jsonify({'error': f'未知的检测类型: {detection_type}'}), 404
    
    return jsonify({
        'type': detection_type,
        'results': detection_results[detection_type]
    })

@app.route('/api/transaction/<tx_id>', methods=['GET'])
def get_transaction_details(tx_id):
    """获取交易详情"""
    if txs_data is None:
        df = load_transactions()
        if df is None:
            return jsonify({'error': '无法加载交易数据'}), 500
    
    # 在交易数据中查找
    for tx in txs_data:
        if tx.get('tx_id') == tx_id:
            return jsonify(tx)
    
    return jsonify({'error': '交易未找到'}), 404

@app.route('/detail/<detection_type>')
def detail_page(detection_type):
    """检测详情页面"""
    return render_template('detail.html', detection_type=detection_type)

def kill_port_processes(port):
    """尝试关闭占用指定端口的进程"""
    try:
        # 查找占用端口的进程
        result = subprocess.run(
            ['lsof', '-ti', f':{port}'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            killed_count = 0
            for pid in pids:
                try:
                    # 先尝试正常关闭
                    subprocess.run(['kill', pid], check=False, timeout=1)
                    time.sleep(0.2)
                    # 如果还在运行，强制关闭
                    subprocess.run(['kill', '-9', pid], check=False, timeout=1)
                    killed_count += 1
                except:
                    pass
            if killed_count > 0:
                print(f"已关闭占用端口{port}的进程 (共{killed_count}个)")
            return killed_count > 0
    except:
        pass
    return False

if __name__ == '__main__':
    # 启动时预加载检测结果
    print("正在加载交易数据并运行检测...")
    run_all_detections()
    print("检测完成，启动Web服务器...")
    
    # 直接使用5000端口
    port = 5000
    
    # 检查端口是否可用，如果被占用则尝试关闭占用进程
    # 对于AirPlay Receiver这种会自动重启的服务，需要多次尝试
    max_attempts = 10
    
    for attempt in range(max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # 尝试绑定端口
                s.bind(('', port))
                print(f"✓ 端口{port}可用")
                break
            except OSError:
                if attempt < max_attempts - 1:
                    if attempt == 0:
                        print(f"端口{port}被占用，正在尝试关闭占用进程...")
                    # 持续尝试关闭占用进程
                    kill_port_processes(port)
                    # 等待时间逐渐增加
                    wait_time = min(0.5 + attempt * 0.3, 2.0)
                    time.sleep(wait_time)
                else:
                    # 最后一次尝试：使用SO_REUSEADDR强制绑定
                    print(f"尝试强制绑定端口{port}...")
                    try:
                        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                        s.bind(('', port))
                        print(f"✓ 成功强制绑定端口{port}")
                        break
                    except OSError:
                        print(f"\n错误：无法绑定端口{port}。")
                        print(f"提示：在macOS上，可能是AirPlay Receiver占用了5000端口。")
                        print(f"解决方法：")
                        print(f"  1. 系统设置 -> 通用 -> AirDrop与隔空播放 -> 关闭AirPlay接收器")
                        print(f"  2. 或者手动运行: sudo lsof -ti:5000 | xargs kill -9")
                        sys.exit(1)
    
    print(f"\n服务器运行在:")
    print(f"  - http://localhost:{port}")
    print(f"  - http://127.0.0.1:{port}")
    print(f"\n注意：不要使用 http://0.0.0.0:{port} 访问，请使用 localhost 或 127.0.0.1\n")
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)

