from collections import deque


# ===================================
# IS CONNECTOR NODE
# ===================================

def is_connector_node(node):

    return node.type == "CONNECTOR"


# ===================================
# FIND ROOT NODES
# ===================================

def find_root_nodes(graph):

    root_nodes = []


    for node in graph.nodes.values():

        # ===================================
        # SKIP CONNECTORS
        # ===================================

        if is_connector_node(node):

            continue


        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )


        valid_incoming = []


        for edge in incoming:

            source_node = graph.nodes.get(
                edge.source
            )


            if (

                source_node and

                not is_connector_node(
                    source_node
                )
            ):

                valid_incoming.append(edge)


        if len(valid_incoming) == 0:

            root_nodes.append(node)


    return root_nodes


# ===================================
# FIND TERMINAL NODES
# ===================================

def find_terminal_nodes(graph):

    terminal_nodes = []


    for node in graph.nodes.values():

        # ===================================
        # SKIP CONNECTORS
        # ===================================

        if is_connector_node(node):

            continue


        outgoing = graph.adjacency_map.get(
            node.id,
            []
        )


        valid_outgoing = []


        for edge in outgoing:

            target_node = graph.nodes.get(
                edge.target
            )


            if (

                target_node and

                not is_connector_node(
                    target_node
                )
            ):

                valid_outgoing.append(edge)


        if len(valid_outgoing) == 0:

            terminal_nodes.append(node)


    return terminal_nodes


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

        node = graph.get_node(node_id)


        # ===================================
        # SKIP CONNECTORS
        # ===================================

        if is_connector_node(node):

            continue


        valid_incoming = []


        for edge in incoming_edges:

            source_node = graph.get_node(
                edge.source
            )


            if (

                source_node and

                not is_connector_node(
                    source_node
                )
            ):

                valid_incoming.append(edge)


        if len(valid_incoming) > 1:

            merge_nodes.append(node)


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

            target_node = graph.get_node(
                edge.target
            )


            # ===================================
            # SKIP CONNECTORS
            # ===================================

            if (

                target_node and

                is_connector_node(
                    target_node
                )
            ):

                connector_outgoing = (

                    graph.adjacency_map.get(
                        target_node.id,
                        []
                    )
                )


                for connector_edge in connector_outgoing:

                    queue.append(
                        connector_edge.target
                    )


            else:

                queue.append(
                    edge.target
                )


    return traversal_order

# ===================================
# FIND BRANCH NODES
# ===================================

def find_branch_nodes(graph):

    branch_nodes = []

    for node in graph.nodes.values():

        if is_connector_node(node):
            continue

        outgoing = graph.adjacency_map.get(
            node.id,
            []
        )

        if len(outgoing) > 1:

            branch_nodes.append(node)

    return branch_nodes

# ===================================
# GET BRANCH COUNT
# ===================================

def get_branch_count(
    graph,
    node_id
):

    outgoing = graph.adjacency_map.get(
        node_id,
        []
    )

    return len(outgoing)


# ===================================
# IS MERGE NODE
# ===================================

def is_merge_node(
    graph,
    node_id
):

    incoming = graph.reverse_adjacency_map.get(
        node_id,
        []
    )

    return len(incoming) > 1
# ===================================
# PRINT GRAPH SUMMARY
# ===================================
def find_error_nodes(graph):

    result = []

    for node in graph.nodes.values():

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )

        for edge in incoming:

            if edge.routing_role == "ERROR":

                result.append(node)
                break

    return result
# ===================================
# PRINT GRAPH SUMMARY
# ===================================

def print_graph_summary(graph):

    print(
        "\n===== GRAPH SUMMARY =====\n"
    )

    print(
        "Total Nodes:",
        len(graph.nodes)
    )

    print(
        "Total Edges:",
        len(graph.edges)
    )

    print(
        "\n===== ROOT NODES =====\n"
    )

    for node in find_root_nodes(graph):

        print(
            node.id,
            "|",
            node.label
        )

    print(
        "\n===== TERMINAL NODES =====\n"
    )

    for node in find_terminal_nodes(graph):

        print(
            node.id,
            "|",
            node.label
        )

    print(
        "\n===== DECISION NODES =====\n"
    )

    for node in find_decision_nodes(graph):

        print(
            node.id,
            "|",
            node.label
        )

    print(
        "\n===== MERGE NODES =====\n"
    )

    for node in find_merge_nodes(graph):

        print(
            node.id,
            "|",
            node.label
        )

    print(
        "\n===== BRANCH NODES =====\n"
    )

    for node in find_branch_nodes(graph):

        print(
            node.id,
            "|",
            node.label,
            "| Branches:",
            get_branch_count(
                graph,
                node.id
            )
        )

    print(
        "\n===== LOOPBACK EDGES =====\n"
    )

    for edge in find_loopback_edges(graph):

        print(

            edge.source,

            "->",

            edge.target
        )

    print(
        "\n===== BFS TRAVERSAL =====\n"
    )

    traversal = bfs_traversal(graph)

    for node_id in traversal:

        print(node_id)