"""Utility code to plot graph of the CMOS NAND gate.

The resulting image is used in the README"""

import matplotlib.pyplot as plt
import numpy as np
import networkx as nx

from circuits import Circuit

C = Circuit("netlists/cmos_nand_1.txt")

f, ax = plt.subplots(figsize=0.75*np.array([6.4, 4.8]))
pos = nx.spring_layout(C.G, seed=5)
nx.draw(C.G, with_labels=True, pos=pos, node_color='orange')

plt.savefig("nand_graph.png", bbox_inches='tight', dpi=200)

# plt.show()
