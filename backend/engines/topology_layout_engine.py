from collections import deque

MAIN_X = 700
HORIZONTAL_GAP = 300
VERTICAL_GAP = 250


def build_topology_layout(graph):

    node_positions = {}

    levels = {}

    branch_lane = {}

    root = graph.get_start_node()

    if not root:
        return {}

    queue = deque(
        [
            (
                root.id,
                0
            )
        ]
    )

    levels[root.id] = 0

    branch_lane[root.id] = MAIN_X

    # ===================================
    # BFS LAYOUT
    # ===================================

    while queue:

        node_id, depth = queue.popleft()

        current_lane = branch_lane.get(
            node_id,
            MAIN_X
        )

        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )

        error_count = 0

        for edge in outgoing:

            print(
                node_id,
                "->",
                edge.target,
                edge.routing_role
            )

            # ===================================
            # IGNORE LOOPBACKS FOR DEPTH
            # ===================================

            if edge.routing_role == "LOOPBACK":
                continue

            child_lane = current_lane

            # ===================================
            # SUCCESS PATH
            # ===================================

            if edge.routing_role == "SUCCESS":

                child_lane = current_lane

            # ===================================
            # ERROR PATHS
            # ===================================

            elif edge.routing_role == "ERROR":

                error_count += 1

                child_lane = (
                    current_lane
                    + (
                        error_count
                        * HORIZONTAL_GAP
                    )
                )

            # ===================================
            # MAIN FLOW
            # ===================================

            elif edge.routing_role == "MAIN_FLOW":

                child_lane = current_lane

            print(
                edge.target,
                "lane=",
                child_lane
            )

            if edge.target not in levels:

                levels[edge.target] = (
                    depth + 1
                )

                branch_lane[
                    edge.target
                ] = child_lane

                queue.append(
                    (
                        edge.target,
                        depth + 1
                    )
                )

    # ===================================
    # BUILD POSITIONS
    # ===================================

    for node_id, node in graph.nodes.items():

        depth = levels.get(
            node_id,
            0
        )

        x = branch_lane.get(
            node_id,
            MAIN_X
        )

        # ===================================
        # KEEP DECISIONS CENTERED
        # ===================================

        if node.type == "DECISION":

            x = MAIN_X

        # ===================================
        # KEEP END CENTERED
        # ===================================

        if node.type == "END":

            x = MAIN_X
            
        # ===================================
        # KEEP MERGE CENTERED
        # ===================================

        if node.type == "MERGE":

            x = 500

        node_positions[node_id] = {

            "x": x,

            "y": depth * VERTICAL_GAP
        }

    return node_positions


def print_topology_layout(
    graph,
    node_positions
):

    print(
        "\n===== TOPOLOGY LAYOUT =====\n"
    )

    for node_id, pos in node_positions.items():

        print(
            node_id,
            pos
        )