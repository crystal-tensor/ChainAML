from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import matplotlib.patches as patches

# Set font for Chinese
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def draw_graph():
    project_root = Path(__file__).resolve().parents[1]
    output_dir = project_root / 'static' / 'screenshots'
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / 'physarum_network_cn.png'

    # Define the graph
    G = nx.DiGraph()
    
    # Add edges
    edges = [
        ('S', 'A'), ('S', 'D'), ('S', 'F'),
        ('A', 'B'), ('A', 'D'), ('A', 'G'),
        ('B', 'C'),
        ('C', 'M1'),
        ('D', 'G'), ('D', 'H'),
        ('F', 'G'),
        ('G', 'X1'), ('G', 'M1'),
        ('X1', 'X2'),
        ('X2', 'Y2'),
        ('H', 'M1'), ('H', 'E'),
        ('M1', 'M2'),
        ('M2', 'Y1'), ('M2', 'Y2'), ('M2', 'E'),
        ('Y1', 'E'),
        ('Y2', 'E')
    ]
    G.add_edges_from(edges)
    
    # Define positions
    pos = {
        'S': (0, 4.5),
        'A': (1.5, 6.5),
        'B': (3, 8),
        'C': (4.5, 8.5),
        'M1': (6, 7.2),
        'M2': (8, 6.2),
        'Y1': (9.5, 7.5),
        'E': (11, 5),
        'D': (3, 4.5),
        'H': (5, 4),
        'Y2': (9.5, 3.5),
        'F': (1.5, 1.5),
        'G': (3.5, 1),
        'X1': (6, 2),
        'X2': (7.5, 1.5)
    }
    
    # Path definitions
    physarum_path = ['S', 'A', 'B', 'C', 'M1', 'M2', 'Y1', 'E']
    shortest_path = ['S', 'D', 'H', 'E']
    
    physarum_edges = list(zip(physarum_path[:-1], physarum_path[1:]))
    shortest_edges = list(zip(shortest_path[:-1], shortest_path[1:]))
    
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
    
    # Colors
    light_edge = '#d3dde4'
    green_edge = '#2e7d52'
    orange_edge = '#f47a57'
    dark_edge = '#264653'
    
    # Helper to draw the graph on a specific ax
    def draw_base_graph(ax, is_left):
        ax.set_axis_off()
        
        # Draw trap background for C
        circle = patches.Circle(pos['C'], radius=0.6, color='#bac3c9', alpha=0.7, zorder=0)
        ax.add_patch(circle)
        
        # Draw all nodes
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='white', edgecolors='#333333', 
                               node_size=800)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=12, font_color='#333333')
        
        # Determine edge colors and styles
        for u, v in G.edges():
            edge = (u, v)
            
            if is_left:
                if edge in physarum_edges:
                    color = green_edge
                    width = 3.5
                    style = 'solid'
                    alpha = 1.0
                elif edge in shortest_edges:
                    color = orange_edge
                    width = 3.5
                    style = 'dashed'
                    alpha = 1.0
                else:
                    color = light_edge
                    width = 1.5
                    style = 'solid'
                    alpha = 0.8
            else:
                if edge in physarum_edges:
                    color = dark_edge
                    width = 3.5
                    style = 'solid'
                    alpha = 1.0
                else:
                    color = light_edge
                    width = 1.5
                    style = 'solid'
                    alpha = 0.8
            
            nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], ax=ax,
                                   edge_color=color, width=width, style=style,
                                   arrowsize=20, alpha=alpha, node_size=800,
                                   connectionstyle='arc3,rad=0.0' if not style=='dashed' else 'arc3,rad=0.0')

    # Left plot
    draw_base_graph(ax1, True)
    ax1.set_title("黏菌导通性 vs 最短路径", fontsize=16, pad=20)
    
    # Right plot
    draw_base_graph(ax2, False)
    ax2.set_title("最高风险洗钱路径: P1", fontsize=16, pad=20)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    draw_graph()
