
import os
import networkx as nx
import matplotlib.pyplot as plt

def build_directory_tree(root_path, graph, parent=None):
    graph.add_node(root_path)
    if parent:
        graph.add_edge(parent, root_path)

    for item in sorted(os.listdir(root_path)):
        child_path = os.path.join(root_path, item)
        if os.path.isdir(child_path):  # Ignore files
            build_directory_tree(child_path, graph, root_path)

def hierarchy_pos(G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
    pos = {}
    def _hierarchy_pos(G, root, left, right, vert_loc, pos):
        children = list(G.successors(root))
        if not children:
            pos[root] = ((left + right) / 2, vert_loc)
        else:
            dx = (right - left) / len(children)
            nextx = left
            for child in children:
                pos = _hierarchy_pos(G, child, nextx, nextx + dx, vert_loc - vert_gap, pos)
                nextx += dx
            pos[root] = ((left + right) / 2, vert_loc)
        return pos
    return _hierarchy_pos(G, root, 0, width, vert_loc, pos)

# 🔧 Set your path here
start_path = "data/input/LCI_database/KBOB"

# Build the tree graph
G = nx.DiGraph()
build_directory_tree(start_path, G)

# Layout the tree
pos = hierarchy_pos(G, root=start_path)

# Draw clean nodes with small size and thin black border
plt.figure(figsize=(12, 5))
nx.draw_networkx_edges(G, pos, arrows=False, width=0.5)

nx.draw_networkx_nodes(
    G, pos,
    node_size=50,
    edgecolors='black',
    node_color='white',
    linewidths=0.5
)

plt.axis('off')
plt.title("Directory Structure (Minimal Tree View)", fontsize=12)
plt.tight_layout()

# Set output base path (no extension)
output_base = 'data/input/LCI_database/plots/kbob'
os.makedirs(os.path.dirname(output_base), exist_ok=True)

# Save as PNG
plt.savefig(f'{output_base}.png', dpi=400, bbox_inches='tight')

# Save as PDF
plt.savefig(f'{output_base}.pdf', bbox_inches='tight')

# Optional: display it
plt.show()