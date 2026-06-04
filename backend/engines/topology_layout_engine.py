from collections import deque
from compiler.graph_analyzer import (
    find_branch_nodes,
    find_merge_nodes
)

MAIN_X = 700
HORIZONTAL_GAP = 300
VERTICAL_GAP = 250


def build_topology_layout(graph):

    node_positions = {}

    levels = {}

    root = graph.get_start_node()

    if not root:
        return {}

    queue = deque([(root.id, 0)])

    levels[root.id] = 0

    while queue:

        node_id, depth = queue.popleft()

        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )

        for edge in outgoing:

            new_depth = depth + 1

            if (

                edge.target not in levels

                or

                new_depth > levels[edge.target]

            ):

                levels[edge.target] = new_depth

                queue.append(
                    (
                        edge.target,
                        new_depth
                    )
        )
    merge_nodes = {

        node.id

        for node in find_merge_nodes(graph)
    }

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

        if node_id in merge_nodes:

            x = MAIN_X

        elif len(incoming) == 1:

            parent_edge = incoming[0]

            parent_id = parent_edge.source

            siblings = graph.adjacency_map.get(
                parent_id,
                []
            )

            if len(siblings) > 1:

                index = siblings.index(
                    parent_edge
                )

                center = (

                    len(siblings) - 1

                ) / 2

                offset = (

                    index - center

                ) * HORIZONTAL_GAP

                x = MAIN_X + offset

        node_positions[node_id] = {

            "x": x,

            "y": depth * VERTICAL_GAP
        }
        print("\n===== DEPTHS =====\n")

    for node_id, depth in levels.items():

        print(
        node_id,
        "->",
        depth
    )

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