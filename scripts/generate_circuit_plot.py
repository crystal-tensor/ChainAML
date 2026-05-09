import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

# Set font for Chinese
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def draw_circuit():
    fig, ax = plt.subplots(figsize=(14, 5))

    # Draw horizontal lines
    for y in [1, 2, 3]:
        ax.plot([0, 13.5], [y, y], color='#333333', lw=1.5, zorder=1)
    ax.plot([0, 13.5], [0, 0], color='#333333', lw=1.5, zorder=1) # classical bit line

    # Add labels on the left
    ax.text(-0.2, 3, 'q0 路径位 0', va='center', ha='right', fontsize=12)
    ax.text(-0.2, 2, 'q1 路径位 1', va='center', ha='right', fontsize=12)
    ax.text(-0.2, 1, 'q2 路径位 2', va='center', ha='right', fontsize=12)
    ax.text(-0.2, 0, 'c 经典位', va='center', ha='right', fontsize=12)

    # Helper to draw boxes
    def draw_box(x, y, w, h, text, facecolor, edgecolor):
        rect = patches.Rectangle((x - w/2, y - h/2), w, h, facecolor=facecolor, edgecolor=edgecolor, lw=1.5, zorder=3)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=11, zorder=4)

    # H gates
    for y in [1, 2, 3]:
        draw_box(1, y, 0.8, 0.6, 'H', '#d1ecf1', '#2b5b84')

    # Oracle 1
    draw_box(3.2, 2, 1.8, 2.6, 'Oracle\n标记高风险路径', '#ffe8d6', '#a0522d')

    # Diffuser 1
    draw_box(5.6, 2, 1.8, 2.6, '扩散算子\nH-X-MCZ-X-H', '#e9ecef', '#495057')

    # Oracle 2
    draw_box(8.0, 2, 1.8, 2.6, 'Oracle\n二次标记', '#ffe8d6', '#a0522d')

    # Diffuser 2
    draw_box(10.4, 2, 1.8, 2.6, '扩散算子\n二次放大', '#e9ecef', '#495057')

    # Measure gates
    for y in [1, 2, 3]:
        draw_box(12.5, y, 0.8, 0.6, 'M', '#fed8b1', '#2b5b84')
        # Draw arrow to classical bit line
        ax.annotate('', xy=(13.2, 0), xytext=(12.9, y),
                    arrowprops=dict(arrowstyle='->', color='#555555', lw=1.5))

    # Title
    ax.set_title('专利二：Grover 路径放大电路', fontsize=18, fontweight='bold', pad=20)

    # Bottom text
    ax.text(6.75, -0.8, '三个量子比特编码八条候选路径。Oracle 翻转目标相位，扩散算子放大其概率。', 
            ha='center', va='center', fontsize=12)

    ax.set_xlim(-1.5, 14)
    ax.set_ylim(-1.2, 4)
    ax.axis('off')

    plt.tight_layout()
    
    # Ensure directory exists
    out_dir = 'static/screenshots'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'patent2_grover_circuit_diagram_cn.png')
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    draw_circuit()