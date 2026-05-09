# ChainAML-PoC: 多源协同量子链上反洗钱检测系统

ChainAML-PoC 是一个融合了图计算、仿生优化与量子计算技术的创新型链上反洗钱（AML）检测框架。本项目针对喷洒式转移、漏斗式归集、混币器分流及矿池洗钱等复杂手法，构建了从时序异常检测到拓扑路径追踪、再到量子干涉裁决与风险分类的闭环监测系统。

---

## 🚀 项目核心特性

### 1. 多源协同检测架构 (Multi-Source Synergy)
- **五类基础检测器**：集成喷洒（Spray）、漏斗（Funnel）、混币（CoinJoin）、矿池（Mining）与量子（Quantum）检测模块。
- **四步闭环流程**：
  1. **Phase I: Detection** - 时间共振检测（`hunt.py`），识别心跳式协同尖刺。
  2. **Phase II: Tracing** - 黏菌路径追踪（`slime_mold_sim.py`），基于仿生“用进废退”优化洗钱拓扑。
  3. **Phase III: Verdict** - 量子干涉裁决（`QSMA.py`），利用 Grover 扩散器放大高风险目标态。
  4. **Phase IV: Classification** - 风险分类与报告，输出交易级概率与证据链。

### 2. 创新算法实现
- **金丝雀水印 (Canary Watermark)**：利用 SHA-3 哈希链与量子态映射，为可疑资金轨迹打上不可篡改的可验证水印。
- **黏菌网络优化 (Physarum Optimization)**：模拟黏菌觅食机制，通过流量强化与闲置衰减，自适应发现隐蔽的资金转移主路径。
- **量子搜索与干涉 (Quantum Interference)**：在复杂组合空间中利用量子干涉相消噪声、放大满足约束（金额守恒、协同性）的目标组合。

### 3. 可视化与交互
- **融合指挥中心**：
  - `index2.html`：展示四步流程的实时动画与检测进程。
  - `AML.html`：提供 8 类算法的启用开关、权重调节与融合评分管理。
- **分类与详情页**：
  - `classification/<type>`：按类别展示异常交易列表与风险概率。
  - `detail/<type>`：深入展示特定检测类型的详细证据与图谱。

---

## 📂 项目结构

```
ChainAML-PoC/
├── web_app.py               # Flask 后端核心，提供 API 与页面路由
├── src/
│   └── chainaml/
│       ├── detectors/       # 检测算法库 (spray, funnel, coinjoin, mining, quantum)
│       └── pipeline.py      # 综合检测流水线
├── templates/
│   ├── index2.html          # 融合首页 (四步流程展示)
│   ├── AML.html             # 协同管理页面 (权重与融合控制)
│   ├── classification.html  # 分类列表页
│   └── detail.html          # 详情展示页
├── static/
│   └── screenshots/         # 自动生成的流程截图 (用于专利文档)
├── data/
│   └── sample_txs.json      # 模拟交易数据集
├── docs/
│   └── patents/             # 专利申请草案 (LaTeX)
├── hunt.py                  # 独立脚本：时间共振检测
├── slime_mold_sim.py        # 独立脚本：黏菌路径模拟
└── QSMA.py                  # 独立脚本：量子搜索模拟
```

---

## 🛠️ 安装与运行

### 环境依赖
- Python 3.8+
- 依赖库：`flask`, `pandas`, `networkx`, `numpy`, `qiskit`, `qiskit-aer`

### 快速启动
1. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
   *(注：需确保安装 qiskit 与 qiskit-aer 以支持量子模拟)*

2. **启动服务**：
   ```bash
   python web_app.py
   ```
   系统将自动寻找可用端口（默认 5000），并尝试关闭冲突进程。

3. **访问界面**：
   - **首页 (流程视图)**: `http://localhost:5000/` 或 `http://localhost:5000/index2`
   - **协同管理**: `http://localhost:5000/aml`
   - **分类列表**: `http://localhost:5000/classification/spray`

---

## 🧪 专利技术方案

本项目包含三项核心技术方案（已生成 LaTeX 草案）：
1. **多源协同量子时序检测**：结合时间分桶 Z 分数与频域共振，利用量子水印进行可验证追踪。
2. **黏菌-量子联合路径追踪**：利用仿生导通性演化与陷阱吸引机制，结合量子幅度放大锁定高风险路径。
3. **混币分流去匿名化**：基于金额守恒与流约束构造组合空间，利用量子干涉裁决实现混币去匿名与证据链重建。

---

## 📊 API 接口

- `GET /api/detections`: 获取所有检测类型的汇总结果。
- `GET /api/detection/<type>`: 获取指定类型（如 `spray`, `quantum`）的详细列表。
- `GET /api/transaction/<tx_id>`: 获取特定交易的原始数据与上下文。

---

## 📝 开发与贡献

- **状态**：PoC (概念验证) 阶段，已完成核心算法跑通与前端交互对接。
- **TODO**：
  - 接入真实链上数据流（目前使用 `sample_txs.json`）。
  - 优化量子模拟器的 qubit 规模以适配更大图谱。
  - 完善前端分类页面的分页与筛选功能。

---

**ChainAML Team** · *Bio-Quantum Synergy for Safer Blockchain*
