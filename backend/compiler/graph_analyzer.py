from collections import deque


# ===================================
# FIND ROOT NODES
# ===================================

def find_root_nodes(graph):

    roots = []


    for node_id in graph.nodes:

        if node_id not in graph.reverse_adjacency_map:

            roots.append(
                graph.get_node(node_id)
            )


    return roots


# ===================================
# FIND TERMINAL NODES
# ===================================

def find_terminal_nodes(graph):

    terminals = []


    for node_id in graph.nodes:

        if node_id not in graph.adjacency_map:

            terminals.append(
                graph.get_node(node_id)
            )


    return terminals


# ===================================
# FIND DECISION NODES
# ===================================

def find_decision_nodes(graph):

    result = []


    for node in graph.nodes.values():

        if node.type == "DECISION":

            result.append(node)


    return result


# ===================================
# FIND OUTGOING BRANCHES
# ===================================

def get_outgoing_branches(
    graph,
    node_id
):

    return graph.adjacency_map.get(
        node_id,
        []
    )


# ===================================
# FIND INCOMING BRANCHES
# ===================================

def get_incoming_branches(
    graph,
    node_id
):

    return graph.reverse_adjacency_map.get(
        node_id,
        []
    )


# ===================================
# DETECT MERGE NODES
# ===================================

def find_merge_nodes(graph):

    merge_nodes = []


    for node_id, incoming_edges in graph.reverse_adjacency_map.items():

        if len(incoming_edges) > 1:

            merge_nodes.append(

                graph.get_node(node_id)
            )


    return merge_nodes


# ===================================
# DETECT LOOPBACK EDGES
# ===================================

def find_loopback_edges(graph):

    result = []


    for edge in graph.edges:

        if edge.edge_type == "LOOPBACK":

            result.append(edge)


    return result


# ===================================
# BFS TRAVERSAL
# ===================================

def bfs_traversal(graph):

    visited = set()

    traversal_order = []


    start_node = graph.get_start_node()


    if not start_node:

        return traversal_order


    queue = deque([

        start_node.id
    ])


    while queue:

        current_id = queue.popleft()


        if current_id in visited:

            continue


        visited.add(current_id)

        traversal_order.append(current_id)


        outgoing_edges = graph.adjacency_map.get(
            current_id,
            []
        )


        for edge in outgoing_edges:

            queue.append(
                edge.target
            )


    return traversal_order


# ===================================
# PRINT GRAPH SUMMARY
# ===================================

def print_graph_summary(graph):

    print("\n===== GRAPH SUMMARY =====\n")


    print(
        "Total Nodes:",
        len(graph.nodes)
    )

    print(
        "Total Edges:",
        len(graph.edges)
    )


    print("\n===== ROOT NODES =====\n")


    for node in find_root_nodes(graph):

        print(node.id, "|", node.label)


    print("\n===== TERMINAL NODES =====\n")


    for node in find_terminal_nodes(graph):

        print(node.id, "|", node.label)


    print("\n===== DECISION NODES =====\n")


    for node in find_decision_nodes(graph):

        print(node.id, "|", node.label)


    print("\n===== MERGE NODES =====\n")


    for node in find_merge_nodes(graph):

        print(node.id, "|", node.label)


    print("\n===== LOOPBACK EDGES =====\n")


    for edge in find_loopback_edges(graph):

        print(

            edge.source,

            "->",

            edge.target
        )


    print("\n===== BFS TRAVERSAL =====\n")


    traversal = bfs_traversal(graph)


    for node_id in traversal:

        print(node_id)