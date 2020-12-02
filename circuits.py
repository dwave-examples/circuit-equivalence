from collections import namedtuple

import networkx as nx

Transistor = namedtuple('Transistor', 'name,drain,gate,source')

class Circuit:
    def __init__(self, netlist_file):
        with open(netlist_file, 'r') as f:
            self.netlist = _parse_netlist(f)
        self.G = _create_graph(self.netlist)

def _parse_netlist(file_obj):

    netlist = []
    for line in file_obj:
        if not ('nmos' in line or 'pmos' in line):
            continue
        values = line.split()
        netlist.append(Transistor._make(values[:4]))
    return netlist

def _create_graph(netlist):
    G = nx.Graph()
    for t in netlist:
        G.add_edges_from([(t.name, t.drain), (t.name, t.gate), (t.name, t.source)])
    return G


if __name__ == '__main__':
    C_nand = Circuit("netlists/cmos_nand_1.txt")
    C_nor = Circuit("netlists/cmos_nor_1.txt")
