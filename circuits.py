# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import namedtuple

import networkx as nx

Transistor = namedtuple('Transistor', 'name,drain,gate,source')


class Circuit:
    def __init__(self, netlist_file):
        """Create circuit definition from netlist file
        
        Args:
            netlist_file (str)
        """
        with open(netlist_file, 'r') as f:
            self.netlist = _parse_netlist(f)
        self.G = _create_graph(self.netlist)


def _parse_netlist(file_obj):
    """Parse netlist file
    
    Returns:
        list: list of Transistor instances
    """
    netlist = []
    for line in file_obj:
        if not ('nmos' in line or 'pmos' in line):
            continue
        values = line.split()
        netlist.append(Transistor(*values[:4]))
    return netlist


def _create_graph(netlist):
    """Construct graph from netlist
    
    Args:
        netlist (list):
            List of Transistor instances obtained from _parse_netlist
    
    Returns:
        networkx.Graph
    """
    G = nx.Graph()
    for t in netlist:
        G.add_edges_from([(t.name, t.drain), (t.name, t.gate), (t.name, t.source)])
    return G


if __name__ == '__main__':
    C_nand = Circuit("netlists/cmos_nand_1.txt")
    C_nor = Circuit("netlists/cmos_nor_1.txt")
