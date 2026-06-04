from collections import defaultdict


# ===================================
# CALCULATE NODE DEPTHS
# ===================================

# ===================================
# CALCULATE NODE DEPTHS
# ===================================

def calculate_node_depths(graph):

    node_depths = {}

    visited = set()


    # ===================================
    # DFS
    # ===================================

    def dfs(

        node_id,

        current_depth
    ):

        # ===================================
        # PREVENT INFINITE LOOPS
        # ===================================

        if node_id in visited:

            return


        visited.add(node_id)


        # ===================================
        # STORE DEPTH
        # ===================================

        existing_depth = node_depths.get(
            node_id,
            -1
        )


        node_depths[node_id] = max(

            existing_depth,

            current_depth
        )


        # ===================================
        # OUTGOING EDGES
        # ===================================

        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )


        for edge in outgoing:

            dfs(

                edge.target,

                current_depth + 1
            )


    # ===================================
    # ROOT NODES
    # ===================================

    for node in graph.nodes.values():

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )


        if len(incoming) == 0:

            dfs(
                node.id,
                0
            )


    return node_depths

# ===================================
# GROUP NODES BY DEPTH
# ===================================

def build_depth_levels(graph):

    node_depths = calculate_node_depths(
        graph
    )


    levels = defaultdict(list)


    for node_id, depth in node_depths.items():

        levels[depth].append(
            graph.get_node(node_id)
        )


    return dict(levels)


# ===================================
# DETECT CYCLIC NODES
# ===================================

def detect_cycles(graph):

    visited = set()

    recursion_stack = set()

    cycles = []


    def dfs(node_id):

        visited.add(node_id)

        recursion_stack.add(node_id)


        outgoing_edges = graph.adjacency_map.get(
            node_id,
            []
        )


        for edge in outgoing_edges:

            target = edge.target


            # BACK EDGE

            if target in recursion_stack:

                cycles.append(

                    (node_id, target)
                )


            elif target not in visited:

                dfs(target)


        recursion_stack.remove(node_id)


    start_node = graph.get_start_node()


    if start_node:

        dfs(start_node.id)


    return cycles


# ===================================
# FIND HEAVY BRANCH NODES
# ===================================

def find_heavy_branch_nodes(graph):

    result = []


    for node_id, edges in graph.adjacency_map.items():

        if len(edges) >= 3:

            result.append(

                graph.get_node(node_id)
            )


    return result


# ===================================
# FIND TERMINAL BRANCHES
# ===================================

def find_terminal_branches(graph):

    result = []


    for node in graph.nodes.values():

        outgoing = graph.adjacency_map.get(
            node.id,
            []
        )


        if len(outgoing) == 0:

            result.append(node)


    return result


# ===================================
# PRINT TOPOLOGY REPORT
# ===================================

def print_topology_report(graph):

    print(
        "\n===== TOPOLOGY REPORT =====\n"
    )


    # ===================================
    # DEPTH LEVELS
    # ===================================

    levels = build_depth_levels(
        graph
    )


    print(
        "===== DEPTH LEVELS =====\n"
    )


    for depth, nodes in levels.items():

        print(f"Depth {depth}:")


        for node in nodes:

            print(

                "  ",

                node.id,

                "|",

                node.label
            )


    # ===================================
    # CYCLES
    # ===================================

    cycles = detect_cycles(graph)


    print(
        "\n===== CYCLES =====\n"
    )


    if len(cycles) == 0:

        print("No cycles detected")


    else:

        for source, target in cycles:

            print(

                source,

                "->",

                target
            )


    # ===================================
    # HEAVY BRANCH NODES
    # ===================================

    heavy_nodes = find_heavy_branch_nodes(
        graph
    )


    print(
        "\n===== HEAVY BRANCH NODES =====\n"
    )


    if len(heavy_nodes) == 0:

        print(
            "No heavy branch nodes"
        )


    else:

        for node in heavy_nodes:

            print(

                node.id,

                "|",

                node.label
            )


    # ===================================
    # TERMINAL BRANCHES
    # ===================================

    terminal_nodes = find_terminal_branches(
        graph
    )


    print(
        "\n===== TERMINAL BRANCHES =====\n"
    )


    for node in terminal_nodes:

        print(

            node.id,

            "|",

            node.label
        )