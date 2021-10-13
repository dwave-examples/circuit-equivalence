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

import itertools
import numpy as np
import networkx as nx

# Ignore errors importing matplotlib.pyplot (may not be available in
# testing framework)
try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
except ImportError:
    pass

import dimod
from dwave.system import LeapHybridDQMSampler


def create_dqm(G1, G2):
    """Construct DQM based on two graphs
    
    Create discrete quadratic model to represent the problem of
    finding an isomorphism between the two graphs
    
    Args:
        G1 (networkx.Graph)
        G2 (networkx.Graph)
    
    Returns:
        DiscreteQuadraticModel
    """
    n = G1.number_of_nodes()
    if n != G2.number_of_nodes():
        raise ValueError

    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    dqm = dimod.DiscreteQuadraticModel()

    # In this formulation, the offset is equal to the number of nodes (multipled
    # by the penalty coefficient A, currently taken to be 1).  Note that in a
    # BQM formulation, the offset would be twice this number due to the need to
    # use a penalty model for each direction of the bijection constraint.
    dqm.offset = n

    for node in G1.nodes:
        # Discrete variable for node i in graph G1, with cases
        # representing the nodes in graph G2
        dqm.add_variable(n, node)

    # Set up the coefficients associated with the constraints that
    # each node in G2 is chosen once.  This represents the H_A
    # component of the energy function.

    for node in G1.nodes:
        dqm.set_linear(node, np.repeat(-1.0, n))
    for itarget in range(n):
        for ivar,node1 in enumerate(G1_nodes):
            for node2 in G1_nodes[ivar+1:]:
                dqm.set_quadratic_case(node1, itarget, node2, itarget, 2.0)

    # Set up the coefficients associated with the constraints that
    # selected edges must appear in both graphs, which is the H_B
    # component of the energy function.  The penalty coefficient B
    # controls the weight of H_B relative to H_A in the energy
    # function.  The value was selected by trial and error using
    # simple test problems.
    B = 2.0

    # For all edges in G1, penalizes mappings to edges not in G2
    for e1 in G1.edges:
        for e2_indices in itertools.combinations(range(n), 2):
            e2 = (G2_nodes[e2_indices[0]], G2_nodes[e2_indices[1]])
            if e2 in G2.edges:
                continue
            # In the DQM, the discrete variables represent nodes in
            # the first graph and are named according to the node
            # names.  The cases for each discrete variable represent
            # nodes in the second graph and are indices from 0..n-1
            dqm.set_quadratic_case(e1[0], e2_indices[0], e1[1], e2_indices[1], B)
            dqm.set_quadratic_case(e1[0], e2_indices[1], e1[1], e2_indices[0], B)

    # For all edges in G2, penalizes mappings to edges not in G1
    for e2 in G2.edges:
        e2_indices = (G2_nodes.index(e2[0]), G2_nodes.index(e2[1]))
        for e1 in itertools.combinations(G1.nodes, 2):
            if e1 in G1.edges:
                continue
            dqm.set_quadratic_case(e1[0], e2_indices[0], e1[1], e2_indices[1], B)
            dqm.set_quadratic_case(e1[0], e2_indices[1], e1[1], e2_indices[0], B)

    return dqm


def find_isomorphism(G1, G2):
    """Search for isomorphism between two graphs

    Args:
        G1 (networkx.Graph)
        G2 (networkx.Graph)

    Returns:
        If no isomorphism is found, returns None.  Otherwise, returns
        dict with keys as nodes from graph 1 and values as
        corresponding nodes from graph 2.
    """
    if G1.number_of_nodes() != G2.number_of_nodes():
        return None
    dqm = create_dqm(G1, G2)
    sampler = LeapHybridDQMSampler()
    results = sampler.sample_dqm(dqm, label='Example - Circuit Equivalence')

    best = results.first
    if np.isclose(best.energy, 0.0):
        G2_nodes = list(G2.nodes)
        return {k: G2_nodes[i] for k,i in best.sample.items()}
    else:
        # Isomorphism not found
        return None


def find_equivalence(C1, C2):
    """Search for equivalence between two circuits

    This requires that the corresponding graphs are isomorphic and
    that matched nodes are "equivalent".  In particular, transistor
    types must match.
    
    Args:
        C1 (Circuit)
        C2 (Circuit)
    
    Returns:
        If no equivalence is found, returns None.  Otherwise, returns
        dict with keys as nodes from graph 1 and values as
        corresponding nodes from graph 2.
    """
    if C1.G.number_of_nodes() != C2.G.number_of_nodes():
        return None
    dqm = create_dqm(C1.G, C2.G)
    sampler = LeapHybridDQMSampler()
    results = sampler.sample_dqm(dqm, label='Example - Circuit Equivalence')

    if not np.isclose(results.first.energy, 0.0):
        return None

    G2_nodes = list(C2.G.nodes)

    for sample, energy in results.data(fields=['sample','energy']):
        if np.isclose(energy, 0.0):
            # Now check that the transistor types match
            mapping = {k: G2_nodes[i] for k,i in sample.items()}
            valid = True
            for n1,n2 in mapping.items():
                if ('nMOS' in n1 and 'nMOS' not in n2) or ('pMOS' in n1 and 'pMOS' not in n2):
                    valid = False
                    break
            if valid:
                return mapping
        else:
            # Sample is not an isomorphism
            return None

    return None


def plot_graphs(G1, G2, node_mapping):
    """Plot graphs of two circuits

    The provided mapping specifies how nodes in graph 1 correspond to
    nodes in graph 2.  The nodes in each graph are colored using
    matching colors based on the specified mapping.

    Args:
        G1 (networkx.Graph)
        G2 (networkx.Graph)
        node_mapping (dict):
            Dictionary that defines the correspondence between nodes
            in graph 1 and nodes in graph 2.  The keys are names of
            nodes in graph 1, and the values are names of nodes in
            graph 2.
    """
    f, axes = plt.subplots(1, 2, figsize=[10,4.5])

    colors = itertools.cycle(mcolors.TABLEAU_COLORS)
    G1_colors = [c for c,i in zip(colors, G1.nodes)]
    G2_targets = [node_mapping[n] for n in G1.nodes]
    G2_colors = [G1_colors[G2_targets.index(n)] for n in G2.nodes]

    nx.draw(G1, with_labels=True, ax=axes[0], node_color=G1_colors)
    nx.draw(G2, with_labels=True, ax=axes[1], node_color=G2_colors)

    return axes


if __name__ == '__main__':
    import argparse

    from circuits import Circuit

    parser = argparse.ArgumentParser()
    parser.add_argument("netlist1", nargs='?', default="netlists/cmos_nand_1.txt", help="netlist file specifying first circuit (default: %(default)s)")
    parser.add_argument("netlist2", nargs='?', default="netlists/cmos_nand_2.txt", help="netlist file specifying second circuit (default: %(default)s)")
    parser.add_argument("--show-plot",  action='store_true', help="display plot of graphs of the circuits")
    parser.add_argument("--save-plot",  action='store_true', help="save plot of graphs of the circuits to file")

    args = parser.parse_args()

    C1 = Circuit(args.netlist1)
    C2 = Circuit(args.netlist2)

    results = find_equivalence(C1, C2)

    if results is None:
        print('No equivalence found')
    else:
        print('Circuits are equivalent:')
        for n1,n2 in results.items():
            print('  {} -> {}'.format(n1, n2))

        if args.show_plot or args.save_plot:
            axes = plot_graphs(C1.G, C2.G, results)
            axes[0].set_title(args.netlist1)
            axes[1].set_title(args.netlist2)

            if args.save_plot:
                filename = 'circuit_equivalence.png'
                plt.savefig(filename, bbox_inches='tight')
                print('Plot saved to:', filename)

            if args.show_plot:
                plt.show()
