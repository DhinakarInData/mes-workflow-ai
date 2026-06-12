from engines.topology_layout_engine import (
    build_topology_layout
    
)
# ===================================
# SEMANTIC LAYOUT ENGINE
# ===================================

MAIN_X = 700

LEFT_X = 400

RIGHT_X = 1000

VERTICAL_GAP = 260


def build_semantic_layout(graph):

    node_positions = {}

    levels = {}

    visited = set()

    root = graph.get_start_node()

    if not root:
        return node_positions

    queue = [(root.id, 0)]

    levels[root.id] = 0

    while queue:

        node_id, depth = queue.pop(0)

        if node_id in visited:
            continue

        visited.add(node_id)

        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )

        for edge in outgoing:

            target = edge.target

            if target not in levels:

                levels[target] = depth + 1

                queue.append(
                    (
                        target,
                        depth + 1
                    )
                )

    # ===================================
    # POSITION NODES
    # ===================================

    for node_id, node in graph.nodes.items():

        depth = levels.get(
            node_id,
            0
        )

        x = MAIN_X

        incoming = graph.reverse_adjacency_map.get(
            node_id,
            []
        )

        if len(incoming) == 1:

            parent_edge = incoming[0]

            label = (
                parent_edge.edge_label
                or
                parent_edge.condition
                or ""
            ).lower()

            if label in [

                "no",
                "not applicable",
                "does not comply"

            ]:

                x = LEFT_X

            elif label in [

                "yes",
                "applicable",
                "comply",
                "option 1",
                "option 2",
                "option 3",
                "option 4"

            ]:

                x = RIGHT_X

        # ===================================
        # MERGE DETECTION
        # ===================================

        if len(incoming) > 1:

            x = MAIN_X

        node_positions[node_id] = {

            "x": x,
            "y": depth * VERTICAL_GAP
        }

    return node_positions


# ===================================
# REPORT
# ===================================

def print_layout_report(
    graph,
    node_positions
):

    print(
        "\n===== LAYOUT REPORT =====\n"
    )

    for node_id, pos in node_positions.items():

        node = graph.nodes[node_id]

        print(

            f"{node.step_number} | "

            f"{node.label} | "

            f"x={pos['x']} "

            f"y={pos['y']}"
        )
        
        
def build_layout(graph):

    return build_semantic_layout(
        graph
    )