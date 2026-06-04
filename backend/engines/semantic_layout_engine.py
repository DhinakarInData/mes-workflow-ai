import math


# ===================================
# NODE SIZE CONFIG
# ===================================

MIN_NODE_WIDTH = 220
MAX_NODE_WIDTH = 340

BASE_NODE_HEIGHT = 80
LINE_HEIGHT = 24

CHARS_PER_LINE = 24


# ===================================
# VERTICAL SPACING
# ===================================

VERTICAL_GAP = 90


# ===================================
# SEMANTIC REGIONS
# ===================================

MAIN_FLOW_X = 650

NO_FLOW_X = 980

ERROR_FLOW_X = 1280

LOOP_FLOW_X = 1550

REJECT_FLOW_X = 300


# ===================================
# CALCULATE NODE SIZE
# ===================================

def calculate_node_size(label):

    if label is None:
        label = ""

    text_length = len(label)

    line_count = max(
        1,
        math.ceil(
            text_length / CHARS_PER_LINE
        )
    )

    width = min(
        MAX_NODE_WIDTH,
        max(
            MIN_NODE_WIDTH,
            text_length * 7
        )
    )

    height = (
        BASE_NODE_HEIGHT
        + (line_count * LINE_HEIGHT)
    )

    return {

        "width": width,

        "height": height,

        "lines": line_count
    }


# ===================================
# FIND ROOT NODE
# ===================================

def find_root_node(graph):

    for node in graph.nodes.values():

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )

        if len(incoming) == 0:
            return node

    return None


# ===================================
# GET REGION X
# ===================================

def get_region_x(edge):

    # ===================================
    # CONDITIONAL NO
    # ===================================

    if (
        edge.edge_type == "CONDITIONAL"
        and edge.condition == "NO"
    ):

        return NO_FLOW_X


    # ===================================
    # ERROR FLOW
    # ===================================

    if edge.edge_type == "ERROR_FLOW":

        return ERROR_FLOW_X


    # ===================================
    # LOOPBACK
    # ===================================

    if edge.edge_type == "LOOPBACK":

        if edge.condition == "REJECTED":
            return REJECT_FLOW_X

        return LOOP_FLOW_X


    # ===================================
    # DEFAULT
    # ===================================

    return MAIN_FLOW_X


# ===================================
# BUILD SEMANTIC LAYOUT
# ===================================

def build_semantic_layout(graph):

    node_positions = {}

    visited = set()

    root_node = find_root_node(graph)

    if root_node is None:
        return {}


    # ===================================
    # QUEUE
    # ===================================

    queue = [

        (
            root_node.id,
            MAIN_FLOW_X,
            80
        )

    ]


    # ===================================
    # PROCESS GRAPH
    # ===================================

    while queue:

        (
            node_id,
            region_x,
            current_y
        ) = queue.pop(0)


        if node_id in visited:
            continue


        visited.add(node_id)

        node = graph.nodes[node_id]


        # ===================================
        # DYNAMIC SIZE
        # ===================================

        size = calculate_node_size(
            node.label
        )


        node_positions[node_id] = {

            "x": region_x,

            "y": current_y,

            "width": size["width"],

            "height": size["height"]
        }


        # ===================================
        # NEXT Y
        # ===================================

        next_y = (

            current_y
            + size["height"]
            + VERTICAL_GAP
        )


        # ===================================
        # OUTGOING EDGES
        # ===================================

        outgoing = graph.adjacency_map.get(
            node_id,
            []
        )


        for edge in outgoing:

            child_x = get_region_x(edge)

            queue.append(

                (
                    edge.target,
                    child_x,
                    next_y
                )

            )


    return node_positions


# ===================================
# PRINT REPORT
# ===================================

def print_layout_report(

    graph,
    node_positions
):

    print(
        "\n===== SEMANTIC LAYOUT REPORT =====\n"
    )

    for node_id, position in node_positions.items():

        node = graph.nodes[node_id]

        print(

            f"{node_id} | "

            f"{node.label} | "

            f"x={position['x']} | "

            f"y={position['y']} | "

            f"w={position['width']} | "

            f"h={position['height']}"
        )