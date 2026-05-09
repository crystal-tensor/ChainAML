import matplotlib.pyplot as plt
import numpy as np
import os

# Set font for Chinese
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def draw_path_recovery_plot():
    labels = ['真实路径覆盖率', 'Top-1 置信度']
    
    # Approximate values from the original image
    baseline_data = [0.0, 0.125]
    proposed_data = [1.0, 0.78]
    
    x = np.arange(len(labels))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(8, 4.5))
    
    # Colors matching the image
    color_baseline = '#f4a261' # Orange/Sandy
    color_proposed = '#2a9d8f' # Teal
    
    rects1 = ax.bar(x - width/2, baseline_data, width, label='基线方法', color=color_baseline)
    rects2 = ax.bar(x + width/2, proposed_data, width, label='本文方法', color=color_proposed)
    
    # Customization
    ax.set_title('专利二：路径恢复对比')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    
    # Adjust y-axis limit to match image
    ax.set_ylim(0, 1.05)
    
    plt.tight_layout()
    
    # Ensure directory exists
    out_dir = 'static/screenshots'
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'patent2_path_recovery_cn.png')
    
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {out_path}")

if __name__ == "__main__":
    draw_path_recovery_plot()