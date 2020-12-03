import itertools
import numpy as np

import dimod
from dwave.system import LeapHybridDQMSampler

def create_dqm(G1, G2):
    """Construct DQM based on two graphs
    
    Returns:
        DiscreteQuadraticModel
    """
    n = G1.number_of_nodes()
    if n != G2.number_of_nodes():
        raise ValueError

    G1_nodes = list(G1.nodes)
    G2_nodes = list(G2.nodes)

    dqm = dimod.DiscreteQuadraticModel()
    for node in G1.nodes:
        # Discrete variable for node i in graph G1, with cases representing the nodes in graph G2
        dqm.add_variable(n, node)

    # For all edges in G1, penalizes mappings to edges not in G2
    for e1 in G1.edges:
        for e2_indices in itertools.combinations(range(n), 2):
            e2 = (G2_nodes[e2_indices[0]], G2_nodes[e2_indices[1]])
            if e2 in G2.edges:
                continue
            # print(e1, e2)
            dqm.set_quadratic_case(e1[0], e2_indices[0], e1[1], e2_indices[1], 1)
            dqm.set_quadratic_case(e1[0], e2_indices[1], e1[1], e2_indices[0], 1)

    # For all edges in G2, penalizes mappings to edges not in G1
    for e2 in G2.edges:
        e2_indices = (G2_nodes.index(e2[0]), G2_nodes.index(e2[1]))
        for e1 in itertools.combinations(G1.nodes, 2):
            if e1 in G1.edges:
                continue
            dqm.set_quadratic_case(e1[0], e2_indices[0], e1[1], e2_indices[1], 1)
            dqm.set_quadratic_case(e1[0], e2_indices[1], e1[1], e2_indices[0], 1)

    # Add in constraints that each node in G2 is chosen once
    A = 1.0
    for node in G1.nodes:
        dqm.set_linear(node, np.repeat(-A,n))
    for itarget in range(n):
        for ivar,node1 in enumerate(G1_nodes):
            for node2 in G1_nodes[ivar+1:]:
                bias = dqm.get_quadratic_case(node1, itarget, node2, itarget)
                dqm.set_quadratic_case(node1, itarget, node2, itarget, bias + 2*A)

    return dqm

def find_isomorphism(G1, G2):
    """Search for isomorphism between two graphs

    Returns:
        If no isomorphism is found, returns None.  Otherwise, returns
        dict with keys as nodes from graph 1 and values as
        corresponding nodes from graph 2.
    """
    if G1.number_of_nodes() != G2.number_of_nodes():
        return None
    dqm = create_dqm(G1, G2)
    sampler = LeapHybridDQMSampler("hybrid_discrete_quadratic_model_version1")
    results = sampler.sample_dqm(dqm)

    best = results.first
    if best.energy == -G1.number_of_nodes():
        G2_nodes = list(G2.nodes)
        return {k: G2_nodes[i] for k,i in best.sample.items()}
    else:
        # Isomorphism not found
        return None


if __name__ == '__main__':
    from circuits import Circuit

    C_nand = Circuit("netlists/cmos_nand_1.txt")
    C_nor = Circuit("netlists/cmos_nor_1.txt")

    results = find_isomorphism(C_nand.G, C_nor.G)
    print(results)
