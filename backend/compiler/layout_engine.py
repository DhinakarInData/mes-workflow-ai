# ===================================
# LANE POSITIONS
# ===================================

LANE_X_MAP = {

    "SYSTEM": 0,

    "MES": 300,

    "OPERATOR":600,

    "SUPERVISOR": 900,

    "QA": 1200
}


# ===================================
# BUILD LAYOUT
# ===================================

def build_layout(graph):

    node_positions = {}

    depth_map = {}

    visited = set()


    # ===================================
    # FIND ROOT NODE
    # ===================================

    root_node = None


    for node in graph.nodes.values():

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )


        if len(incoming) == 0:

            root_node = node

            break


    if root_node is None:

        return node_positions


    # ===================================
    # BFS TRAVERSAL
    # ===================================

    queue = [(root_node.id, 0)]


    while queue:

        node_id, depth = queue.pop(0)


        if node_id in visited:

            continue


        visited.add(node_id)

        depth_map[node_id] = depth


        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )


        for edge in outgoing:

            queue.append(
                (
                    edge.target,
                    depth + 1
                )
            )


    # ===================================
    # POSITION NODES
    # ===================================

    for node_id, depth in depth_map.items():

        node = graph.nodes[node_id]


        lane = node.lane.upper()

        if node.type == "CONNECTOR":

            x_position = 450

        else:

            x_position = LANE_X_MAP.get(
                lane,
                1250
            )
       


        # ===================================
        # GLOBAL DEPTH ALIGNMENT
        # ===================================

        y_position = depth * 220


        node_positions[node_id] = {

            "x": x_position,

            "y": y_position
        }


    return node_positions


# ===================================
# PRINT LAYOUT REPORT
# ===================================

if DEBUG_MODE:

    print_layout_report(
        graph,
        node_positions
    )

    print(
        "\n===== LAYOUT REPORT =====\n"
    )


    for node_id, position in node_positions.items():

        node = graph.nodes[node_id]


        print(

            f"{node_id} | "

            f"{node.label} | "

            f"lane={node.lane} | "

            f"x={position['x']} "

            f"y={position['y']}"
        )