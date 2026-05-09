import matplotlib.pyplot as plt
import numpy as np
import os

# Set font for Chinese
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def draw_probability_plot():
    labels = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8']
    
    # Probabilities
    before_prob = [0.125] * 8
    
    # After Grover iteration (approximate values from the image)
    # Target P1 is amplified, others are suppressed.
    # If P1 is ~0.78, the remaining 7 share 0.22, so each is ~0.031.
    after_prob = [0.781] + [0.031] * 7
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Colors matching the image
    color_before = '#adb5bd' # Grey
    color_after = '#551a8b'  # Purple
    
    rects1 = ax.bar(x - width/2, before_prob, width, label='放大前', color=color_before)
    rects2 = ax.bar(x + width/2, after_prob, width, label='Grover 迭代后', color=color_after)
    
    # Customization
    ax.set_ylabel('概率')
    ax.set_title('专利二：候选路径概率放大')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Adjust y-axis limit to match image (~0.85)
    ax.set_ylim(0, 0.85)
    
    plt.tight_layout()
    
    # Ensure directory exists
    out_dir = 'static/screenshots'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'patent2_grover_circuit_cn.png')
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    draw_probability_plot()