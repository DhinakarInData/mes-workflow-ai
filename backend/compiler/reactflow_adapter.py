from compiler.routing_engine import (
    get_routing_config,
    is_restart_loop
)
from compiler.fds_numbering_engine import (
    build_fds_display_step_numbers
)
from models.workflow_models import (
    WorkflowEdge,
    WorkflowNode
)


MAIN_X = 700
GLOBAL_RETURN_BUS_X = 2060
RETURN_BUS_GAP = 260
ERROR_COLUMN_X = 1120
HORIZONTAL_GAP = 340
ERROR_BRANCH_START_OFFSET = 90
ERROR_BRANCH_VERTICAL_GAP = 170
POST_ERROR_MAIN_GAP = 105
CONNECTOR_TRIGGER_DISTANCE = 900
CONNECTOR_PAGE_BAND_HEIGHT = 1400
CONNECTOR_SOURCE_OFFSET_X = 130
CONNECTOR_TARGET_OFFSET_X = 130
CONNECTOR_OFFSET_Y = 0
ENABLE_REFERENCE_CONNECTORS = False
SIDE_TERMINAL_MIN_GAP = 85
SIDE_TERMINAL_MAX_GAP = 150
SIDE_TERMINAL_CLEARANCE = 65
SIDE_COLUMN_TOLERANCE = 24
LOCAL_RETRY_MAX_VERTICAL_SPAN = 900
RESTART_LANE_NODE_CLEARANCE = 35
RENDER_COLLISION_PADDING = 16
RESTART_OUTER_BUS_RESERVATION_PADDING = 160
TERMINAL_CONDITIONS = {
    "NO",
    "END WORKFLOW",
    "FINISH",
    "COMPLETE"
}

VISUAL_PASS_THROUGH_RESPONSE_ACTORS = {
    "QA",
    "SUPERVISOR"
}

VISUAL_PASS_THROUGH_RESPONSE_LABELS = {
    "APPROVED",
    "APPROVE",
    "OK",
    "ACCEPTED",
    "CONTINUE",
    "PROCESS CAN CONTINUE"
}

LINKED_WORKFLOW_KEYWORDS = [
    "LINKED WORKFLOW",
    "DEVIATION WORKFLOW",
    "LAUNCH DEVIATION",
    "REFERENCE WORKFLOW"
]

CORRECTION_RETURN_KEYWORDS = [
    "ASK FOR CORRECTION",
    "CORRECTION",
    "REWORK",
    "REVIEW",
    "REJECTS DISPOSAL"
]

NEXT_RESTART_LABEL_KEYWORDS = [
    "NEXT EQUIPMENT",
    "PREPARE",
    "SELECTION",
    "CONTINUE"
]

REWORK_OUTCOME_LABEL_KEYWORDS = [
    "REJECT",
    "REJECTED",
    "NOT CORRECT",
    "INCORRECT",
    "REWORK",
    "UPDATE",
    "CORRECTION"
]


def connector_label_from_index(
    index
):

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    label = ""

    value = index

    while value > 0:

        value -= 1

        label = letters[value % 26] + label

        value //= 26

    return label


def calculate_global_return_bus_x(
    graph,
    node_positions
):

    if not node_positions:

        return GLOBAL_RETURN_BUS_X

    forward_positions = [
        position["x"]
        for node_id, position in node_positions.items()
        if (
            graph.get_node(node_id)
            and graph.get_node(node_id).type != "MERGE"
        )
    ]

    if not forward_positions:

        return GLOBAL_RETURN_BUS_X

    rightmost_x = max(
        forward_positions
    )

    return max(
        GLOBAL_RETURN_BUS_X,
        rightmost_x + RETURN_BUS_GAP
    )
# ===================================
# ESTIMATE NODE SIZE
# ===================================

def estimate_node_size(label):

    if not label:

        return 220, 100


    char_count = len(label)


    # ===================================
    # WIDTH
    # ===================================

    width = min(

        max(
            220,
            char_count * 7
        ),

        420
    )


    # ===================================
    # LINES
    # ===================================

    line_count = (

        char_count // 24
    ) + 1


    # ===================================
    # HEIGHT
    # ===================================

    height = max(

        100,

        line_count * 32
    )


    return width, height


def build_node_display_label(
    node,
    display_step_number
):

    if node.type in [
        "START",
        "END"
    ]:

        return node.label

    if display_step_number:

        return f"{display_step_number}: {node.label}"

    return node.label


def get_node_visual_type(node):

    label = (
        node.label
        or ""
    ).upper()

    if (
        node.type == "SYSTEM_ACTIVITY"
        and any(
            keyword in label
            for keyword in LINKED_WORKFLOW_KEYWORDS
        )
    ):

        return "LINKED_WORKFLOW"

    return None


def is_local_retry_loop(
    graph,
    edge,
    node_positions
):

    if not (
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
        or (
            edge.edge_type == "CONDITIONAL"
            and is_restart_loop(
                edge
            )
        )
    ):

        return False

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return False

    if target_position.get("y", 0) >= source_position.get("y", 0):

        return False

    source_node = graph.get_node(
        edge.source
    )

    target_node = graph.get_node(
        edge.target
    )

    if not source_node or not target_node:

        return False

    if source_node.group == "ERROR_HANDLING":

        return False

    x_distance = abs(
        source_position.get("x", 0)
        - target_position.get("x", 0)
    )

    y_distance = abs(
        source_position.get("y", 0)
        - target_position.get("y", 0)
    )

    same_column_retry = (
        x_distance <= SIDE_COLUMN_TOLERANCE
        and y_distance <= LOCAL_RETRY_MAX_VERTICAL_SPAN
    )

    side_correction_retry = (
        source_node.type == "MANUAL_ACTIVITY"
        and target_node.type in [
            "SYSTEM_CHECK",
            "SYSTEM_ACTIVITY",
            "MANUAL_ACTIVITY"
        ]
        and x_distance <= HORIZONTAL_GAP * 2.2
        and y_distance <= 900
    )

    if not (
        same_column_retry
        or side_correction_retry
    ):

        return False

    return (
        source_node.type in [
            "SYSTEM_ACTIVITY",
            "MANUAL_ACTIVITY"
        ]
        and target_node.type in [
            "SYSTEM_CHECK",
            "SYSTEM_ACTIVITY",
            "MANUAL_ACTIVITY"
        ]
    )


def edge_vertical_interval(
    node_positions,
    edge
):

    source_position = node_positions.get(
        edge.source,
        {}
    )

    target_position = node_positions.get(
        edge.target,
        {}
    )

    source_y = source_position.get(
        "y",
        0
    )

    target_y = target_position.get(
        "y",
        0
    )

    return (
        min(source_y, target_y),
        max(source_y, target_y)
    )


def intervals_overlap(
    first_interval,
    second_interval,
    padding=0
):

    return not (
        first_interval[1] + padding < second_interval[0]
        or second_interval[1] + padding < first_interval[0]
    )


def estimate_node_half_width(node):

    if not node:

        return 110

    node_width, _ = estimate_node_size(
        node.label
    )

    if node.type == "CONNECTOR":

        node_width = 44

    return node_width / 2


def estimate_node_half_height(node):

    if not node:

        return 50

    _, node_height = estimate_node_size(
        node.label
    )

    if node.type == "CONNECTOR":

        node_height = 44

    return node_height / 2


def node_bounds(
    graph,
    node_positions,
    node_id,
    padding=0
):

    node = graph.get_node(
        node_id
    )

    position = node_positions.get(
        node_id
    )

    if not node or not position:

        return None

    half_width = estimate_node_half_width(
        node
    )

    half_height = estimate_node_half_height(
        node
    )

    return {
        "left": position.get("x", 0) - half_width - padding,
        "right": position.get("x", 0) + half_width + padding,
        "top": position.get("y", 0) - half_height - padding,
        "bottom": position.get("y", 0) + half_height + padding
    }


def render_node_bounds(
    render_node_by_id,
    render_positions,
    node_id,
    padding=RENDER_COLLISION_PADDING
):

    node = render_node_by_id.get(
        node_id
    )

    position = render_positions.get(
        node_id
    )

    if not node or not position:

        return None

    half_width = estimate_node_half_width(
        node
    )

    half_height = estimate_node_half_height(
        node
    )

    return {
        "left": position.get("x", 0) - half_width - padding,
        "right": position.get("x", 0) + half_width + padding,
        "top": position.get("y", 0) - half_height - padding,
        "bottom": position.get("y", 0) + half_height + padding
    }


def bounds_overlap(
    first,
    second
):

    if not first or not second:

        return False

    return not (
        first["right"] < second["left"]
        or second["right"] < first["left"]
        or first["bottom"] < second["top"]
        or second["bottom"] < first["top"]
    )


def segment_intersects_bounds(
    start_x,
    start_y,
    end_x,
    end_y,
    bounds
):

    if not bounds:

        return False

    if abs(start_x - end_x) < 1:

        x = start_x

        if not (
            bounds["left"] <= x <= bounds["right"]
        ):

            return False

        segment_top = min(
            start_y,
            end_y
        )

        segment_bottom = max(
            start_y,
            end_y
        )

        return not (
            segment_bottom < bounds["top"]
            or segment_top > bounds["bottom"]
        )

    if abs(start_y - end_y) < 1:

        y = start_y

        if not (
            bounds["top"] <= y <= bounds["bottom"]
        ):

            return False

        segment_left = min(
            start_x,
            end_x
        )

        segment_right = max(
            start_x,
            end_x
        )

        return not (
            segment_right < bounds["left"]
            or segment_left > bounds["right"]
        )

    return False


def orthogonal_lane_collision_count(
    graph,
    node_positions,
    edge,
    lane_x,
    padding=28
):

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return 0

    source_x = source_position.get(
        "x",
        0
    )

    source_y = source_position.get(
        "y",
        0
    )

    target_x = target_position.get(
        "x",
        0
    )

    target_y = target_position.get(
        "y",
        0
    )

    path_segments = [
        (
            source_x,
            source_y,
            lane_x,
            source_y
        ),
        (
            lane_x,
            source_y,
            lane_x,
            target_y
        ),
        (
            lane_x,
            target_y,
            target_x,
            target_y
        )
    ]

    collisions = 0

    for node_id, node in graph.nodes.items():

        if node_id in [
            edge.source,
            edge.target
        ]:

            continue

        if node.type in [
            "MERGE",
            "CONNECTOR"
        ]:

            continue

        bounds = node_bounds(
            graph,
            node_positions,
            node_id,
            padding
        )

        if any(
            segment_intersects_bounds(
                *segment,
                bounds
            )
            for segment in path_segments
        ):

            collisions += 1

    return collisions


def choose_lower_collision_restart_side(
    graph,
    edge,
    node_positions,
    left_lane_x,
    right_lane_x
):

    left_collisions = orthogonal_lane_collision_count(
        graph,
        node_positions,
        edge,
        left_lane_x
    )

    right_collisions = orthogonal_lane_collision_count(
        graph,
        node_positions,
        edge,
        right_lane_x
    )

    if left_collisions == right_collisions:

        return None

    return (
        "left"
        if left_collisions < right_collisions
        else "right"
    )


def restart_left_occupied_right_x(
    graph,
    node_positions,
    edge
):

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return None

    min_y = min(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    max_y = max(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    source_x = source_position.get(
        "x",
        MAIN_X
    )

    occupied_right = None

    for node_id, position in node_positions.items():

        if node_id in [
            edge.source,
            edge.target
        ]:

            continue

        node = graph.get_node(
            node_id
        )

        if not node or node.type in [
            "MERGE",
            "CONNECTOR"
        ]:

            continue

        node_x = position.get(
            "x",
            0
        )

        node_y = position.get(
            "y",
            0
        )

        if not (
            min_y <= node_y <= max_y
        ):

            continue

        if node_x >= source_x - 80:

            continue

        node_right = (
            node_x
            + estimate_node_half_width(
                node
            )
        )

        occupied_right = max(
            occupied_right
            if occupied_right is not None
            else node_right,
            node_right
        )

    if occupied_right is None:

        return None

    return occupied_right + RESTART_LANE_NODE_CLEARANCE


def restart_left_occupied_left_x(
    graph,
    node_positions,
    edge
):

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return None

    min_y = min(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    max_y = max(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    source_x = source_position.get(
        "x",
        MAIN_X
    )

    occupied_left = None

    for node_id, position in node_positions.items():

        if node_id in [
            edge.source,
            edge.target
        ]:

            continue

        node = graph.get_node(
            node_id
        )

        if not node or node.type in [
            "MERGE",
            "CONNECTOR"
        ]:

            continue

        node_x = position.get(
            "x",
            0
        )

        node_y = position.get(
            "y",
            0
        )

        if not (
            min_y <= node_y <= max_y
        ):

            continue

        if node_x >= source_x - 80:

            continue

        node_left = (
            node_x
            - estimate_node_half_width(
                node
            )
        )

        occupied_left = min(
            occupied_left
            if occupied_left is not None
            else node_left,
            node_left
        )

    if occupied_left is None:

        return None

    return occupied_left - RESTART_LANE_NODE_CLEARANCE


def restart_right_occupied_right_x(
    graph,
    node_positions,
    edge
):

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return None

    min_y = min(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    max_y = max(
        source_position.get(
            "y",
            0
        ),
        target_position.get(
            "y",
            0
        )
    )

    source_x = source_position.get(
        "x",
        MAIN_X
    )

    occupied_right = None

    for node_id, position in node_positions.items():

        if node_id in [
            edge.source,
            edge.target
        ]:

            continue

        node = graph.get_node(
            node_id
        )

        if not node or node.type in [
            "MERGE",
            "CONNECTOR"
        ]:

            continue

        node_x = position.get(
            "x",
            0
        )

        node_y = position.get(
            "y",
            0
        )

        if not (
            min_y <= node_y <= max_y
        ):

            continue

        if node_x <= source_x + 80:

            continue

        node_right = (
            node_x
            + estimate_node_half_width(
                node
            )
        )

        occupied_right = max(
            occupied_right
            if occupied_right is not None
            else node_right,
            node_right
        )

    if occupied_right is None:

        return None

    return occupied_right + RESTART_LANE_NODE_CLEARANCE


def get_numeric_suffix(value):

    digits = "".join(
        character
        for character in str(value or "")
        if character.isdigit()
    )

    if not digits:

        return None

    return int(digits)


def build_display_step_numbers(
    nodes,
    edges=None,
    node_positions=None
):

    return build_fds_display_step_numbers(
        nodes,
        edges,
        node_positions
    )

    display_numbers = {}

    visible_nodes = [
        node
        for node in nodes
        if node.type != "MERGE"
    ]

    node_positions = node_positions or {}

    manual_sequence = []

    for node in visible_nodes:

        if node.type == "MANUAL_ACTIVITY":

            position = node_positions.get(
                node.id,
                {}
            )

            manual_sequence.append(
                (
                    position.get(
                        "y",
                        0
                    ),
                    position.get(
                        "x",
                        0
                    ),
                    node.id
                )
            )

    manual_sequence.sort()

    manual_base_by_id = {}

    for index, (_, _, node_id) in enumerate(
        manual_sequence,
        start=1
    ):

        base_number = f"A{index}"

        manual_base_by_id[node_id] = base_number

        display_numbers[node_id] = base_number

    if not manual_sequence:

        for node in visible_nodes:

            display_numbers[node.id] = (
                node.step_number
                or node.id
            )

        return display_numbers

    visible_manuals = [
        (
            y,
            x,
            node_id,
            manual_base_by_id[node_id]
        )
        for y, x, node_id in manual_sequence
    ]

    substep_counts = {}

    def non_manual_order_priority(node):

        if node.type in [
            "SYSTEM_CHECK",
            "RESPONSE",
            "DECISION"
        ]:

            return 0

        return 1

    incoming_edges_by_target = {}

    for edge in (edges or []):

        if (
            edge.edge_type == "LOOPBACK"
            or edge.routing_role == "LOOPBACK"
        ):

            continue

        incoming_edges_by_target.setdefault(
            edge.target,
            []
        ).append(edge)

    def base_from_display_number(display_number):

        if not display_number:

            return None

        return str(display_number).split(
            ".",
            1
        )[0]

    def nearest_manual_before(node_id):

        position = node_positions.get(
            node_id,
            {}
        )

        node_y = position.get(
            "y",
            0
        )

        node_x = position.get(
            "x",
            0
        )

        candidates = [
            item
            for item in visible_manuals
            if (
                item[0] < node_y
                or (
                    item[0] == node_y
                    and item[1] <= node_x
                )
            )
        ]

        if not candidates:

            candidates = visible_manuals[:1]

        return max(
            candidates,
            key=lambda item: (
                item[0],
                item[1]
            )
        )[3]

    def incoming_base_number(node_id):

        node_position = node_positions.get(
            node_id,
            {}
        )

        node_y = node_position.get(
            "y",
            0
        )

        candidates = []

        for edge in incoming_edges_by_target.get(
            node_id,
            []
        ):

            source_display_number = display_numbers.get(
                edge.source
            )

            source_base_number = base_from_display_number(
                source_display_number
            )

            if not source_base_number:

                continue

            source_position = node_positions.get(
                edge.source,
                {}
            )

            source_y = source_position.get(
                "y",
                0
            )

            candidates.append(
                (
                    source_y <= node_y,
                    source_y,
                    source_position.get(
                        "x",
                        0
                    ),
                    source_base_number
                )
            )

        if not candidates:

            return None

        return max(
            candidates,
            key=lambda item: (
                item[0],
                item[1],
                item[2]
            )
        )[3]

    ordered_non_manual_nodes = sorted(
        [
            node
            for node in visible_nodes
            if node.type not in [
                "MANUAL_ACTIVITY",
                "START",
                "END"
            ]
        ],
        key=lambda node: (
            node_positions.get(
                node.id,
                {}
            ).get(
                "y",
                0
            ),
            non_manual_order_priority(
                node
            ),
            node_positions.get(
                node.id,
                {}
            ).get(
                "x",
                0
            )
        )
    )

    for node in ordered_non_manual_nodes:

        base_number = (
            incoming_base_number(
                node.id
            )
            or nearest_manual_before(
                node.id
            )
        )

        substep_counts[base_number] = (
            substep_counts.get(
                base_number,
                0
            ) + 1
        )

        display_numbers[node.id] = (
            f"{base_number}.{substep_counts[base_number]}"
        )

    for node in visible_nodes:

        if node.id in display_numbers:

            continue

        if node.type == "START":

            display_numbers[node.id] = "START"

            continue

        if node.type == "END":

            display_numbers[node.id] = "END"

            continue

        display_numbers[node.id] = (
            node.step_number
            or node.id
        )

    return display_numbers

# ===================================
# BUILD REACTFLOW NODES
# ===================================

def make_error_label(label):

    if not label:

        return "Error"

    return label.replace(
        "_",
        " "
    ).title()


def is_terminal_end_edge(
    graph,
    edge
):

    target_node = graph.get_node(
        edge.target
    )

    if not target_node or target_node.type != "END":

        return False

    if edge.edge_type != "CONDITIONAL":

        return False

    label = (
        edge.edge_label
        or edge.condition
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )

    return label in TERMINAL_CONDITIONS


def is_response_terminal_option_edge(
    graph,
    edge
):

    target_node = graph.get_node(
        edge.target
    )

    source_node = graph.get_node(
        edge.source
    )

    if not target_node or not source_node:

        return False

    if target_node.type != "END":

        return False

    if source_node.type != "RESPONSE":

        return False

    if edge.edge_type != "CONDITIONAL":

        return False

    outgoing = [
        outgoing_edge
        for outgoing_edge in graph.adjacency_map.get(
            edge.source,
            []
        )
        if outgoing_edge.edge_type == "CONDITIONAL"
    ]

    return len(
        outgoing
    ) > 1


def normalize_condition_label(edge):

    return (
        edge.edge_label
        or edge.condition
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )


def is_rework_outcome_label(edge):

    normalized_label = normalize_condition_label(
        edge
    )

    return any(
        keyword in normalized_label
        for keyword in REWORK_OUTCOME_LABEL_KEYWORDS
    )


def non_loopback_render_edges(
    graph,
    node_id
):

    return [
        edge
        for edge in graph.adjacency_map.get(
            node_id,
            []
        )
        if edge.edge_type != "LOOPBACK"
        and edge.routing_role != "LOOPBACK"
    ]


def non_loopback_render_incoming_edges(
    graph,
    node_id
):

    return [
        edge
        for edge in graph.reverse_adjacency_map.get(
            node_id,
            []
        )
        if edge.edge_type != "LOOPBACK"
        and edge.routing_role != "LOOPBACK"
    ]


def is_visual_pass_through_response(
    graph,
    node
):

    if not node or node.type != "RESPONSE":

        return False

    if (
        node.response_actor or ""
    ).upper() not in VISUAL_PASS_THROUGH_RESPONSE_ACTORS:

        return False

    incoming_edges = non_loopback_render_incoming_edges(
        graph,
        node.id
    )

    outgoing_edges = non_loopback_render_edges(
        graph,
        node.id
    )

    all_outgoing_edges = graph.adjacency_map.get(
        node.id,
        []
    )

    if (
        len(incoming_edges) != 1
        or len(outgoing_edges) != 1
        or len(all_outgoing_edges) != 1
    ):

        return False

    outgoing_edge = outgoing_edges[0]

    target_node = graph.get_node(
        outgoing_edge.target
    )

    if not target_node or target_node.type in {
        "END",
        "MERGE",
        "RESPONSE"
    }:

        return False

    if outgoing_edge.routing_role not in {
        "SUCCESS",
        "LOCAL_CONTINUATION",
        "MAIN_FLOW"
    }:

        return False

    return normalize_condition_label(
        outgoing_edge
    ) in VISUAL_PASS_THROUGH_RESPONSE_LABELS


def infer_response_option_label(
    graph,
    edge
):

    explicit_label = (
        edge.edge_label
        or edge.condition
    )

    if explicit_label:

        return explicit_label

    source_node = graph.get_node(
        edge.source
    )

    if not source_node or source_node.type != "RESPONSE":

        return None

    sibling_labels = {
        normalize_condition_label(
            sibling_edge
        )
        for sibling_edge in graph.adjacency_map.get(
            edge.source,
            []
        )
        if sibling_edge is not edge
    }

    is_retry_option = (
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
    )

    if (
        is_retry_option
        and "NO" in sibling_labels
        and "YES" not in sibling_labels
    ):

        return "YES"

    if (
        "YES" in sibling_labels
        and "NO" not in sibling_labels
    ):

        return "NO"

    if is_retry_option:

        return "RETRY"

    return None


def is_correction_return_edge(edge):

    label = normalize_condition_label(
        edge
    )

    return any(
        keyword in label
        for keyword in CORRECTION_RETURN_KEYWORDS
    )


def is_retry_error_label(edge):

    label = normalize_condition_label(
        edge
    )

    return is_retry_error_text(
        label
    )


def is_retry_error_text(label):

    if not label:

        return False

    label = label.strip().upper().replace(
        "_",
        " "
    )

    exact_success_or_restart_labels = [
        "YES",
        "NO",
        "VALID",
        "PASS",
        "APPROVED",
        "COMPLETE",
        "FINISH"
    ]

    if label in exact_success_or_restart_labels:

        return False

    success_or_restart_keywords = [
        "WITHIN",
        "NEXT",
        "CONTINUE",
        "MORE MATERIAL"
    ]

    if any(
        keyword in label
        for keyword in success_or_restart_keywords
    ):

        return False

    retry_keywords = [
        "INVALID",
        "INCORRECT",
        "MISMATCH",
        "NOT",
        "REQUIRED",
        "REJECT",
        "FAIL",
        "ERROR",
        "BLOCK",
        "DUE",
        "EXPIRED",
        "BELOW",
        "ABOVE",
        "CORRECTION",
        "SHORT",
        "EXCESS"
    ]

    return any(
        keyword in label
        for keyword in retry_keywords
    )


def is_success_outcome_label(edge):

    label = normalize_condition_label(
        edge
    )

    if not label:

        return False

    success_labels = [
        "VALID",
        "CORRECT",
        "YES",
        "PASS",
        "APPROVED",
        "ACCEPTED",
        "COMPLETE",
        "FINISH"
    ]

    if label in success_labels:

        return True

    success_keywords = [
        "WITHIN",
        "COMPLY",
        "AVAILABLE"
    ]

    return any(
        keyword in label
        for keyword in success_keywords
    )


def get_next_system_activity_index(graph):

    next_index = 1

    for node_id in graph.nodes:

        if node_id.startswith("SA"):

            try:

                next_index = max(
                    next_index,
                    int(node_id[2:]) + 1
                )

            except ValueError:

                pass

    return next_index


def is_direct_error_return_edge(
    graph,
    edge,
    node_positions
):

    source_node = graph.get_node(
        edge.source
    )

    if not source_node:

        return False

    target_node = graph.get_node(
        edge.target
    )

    if source_node.type not in [
        "RESPONSE",
        "DECISION"
    ]:

        return False

    if (
        source_node.type == "RESPONSE"
        and source_node.response_actor
        and source_node.response_actor != "SYSTEM"
    ):

        return False

    if (
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
    ):

        if not is_retry_error_label(
            edge
        ):

            return False

    elif edge.edge_type == "CONDITIONAL":

        routing = get_routing_config(
            edge
        )

        if routing["routing_type"] != "RIGHT_EXTERNAL":

            return False

    else:

        return False

    if is_correction_return_edge(edge):

        return False

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return False

    target_is_visible_error_branch = (
        target_node
        and target_node.type == "SYSTEM_ACTIVITY"
        and (
            target_node.group == "ERROR_HANDLING"
            or target_position["x"] > source_position["x"] + 80
        )
    )

    if target_is_visible_error_branch:

        return False

    return target_position["y"] < source_position["y"]


def is_next_restart_helper_node(
    graph,
    node_id
):

    node = graph.get_node(
        node_id
    )

    if not node or node.type != "SYSTEM_ACTIVITY":

        return False

    label = (
        node.label
        or ""
    ).upper()

    if not all(
        keyword in label
        for keyword in [
            "NEXT",
            "EQUIPMENT"
        ]
    ) and not (
        "SELECTION" in label
        and "EQUIPMENT" in label
    ):

        return False

    outgoing = graph.adjacency_map.get(
        node_id,
        []
    )

    if len(outgoing) != 1:

        return False

    outgoing_edge = outgoing[0]

    return (
        outgoing_edge.edge_type == "LOOPBACK"
        or outgoing_edge.routing_role == "LOOPBACK"
    )


def is_side_terminal_end_edge(
    graph,
    edge,
    node_positions
):

    target_node = graph.get_node(
        edge.target
    )

    if not target_node or target_node.type != "END":

        return False

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return False

    return abs(
        source_position.get(
            "x",
            0
        ) - target_position.get(
            "x",
            0
        )
    ) > 80


def is_side_terminal_outcome_end_edge(
    graph,
    edge,
    node_positions
):

    target_node = graph.get_node(
        edge.target
    )

    if not target_node or target_node.type != "END":

        return False

    for incoming_edge in graph.reverse_adjacency_map.get(
        edge.source,
        []
    ):

        if is_side_terminal_outcome_render_edge(
            graph,
            incoming_edge,
            node_positions
        ):

            return True

    return False


def build_visual_terminal_node(
    target_node,
    edge
):

    return WorkflowNode(

        id=f"{target_node.id}__{edge.source}_END",

        type="END",

        label=target_node.label,

        step_number=target_node.step_number,

        lane=target_node.lane,

        group=target_node.group,

        metadata={
            "visual_terminal_for": target_node.id,
            "source_node_id": edge.source
        }
    )


def make_connector_node(
    connector_id,
    connector_label,
    edge,
    connector_role
):

    return WorkflowNode(

        id=connector_id,

        type="CONNECTOR",

        label=connector_label,

        step_number=connector_label,

        lane="REFERENCE",

        group="CONNECTOR",

        metadata={
            "connector_role": connector_role,
            "semantic_source": edge.source,
            "semantic_target": edge.target
        }
    )


def position_visual_terminal_node(
    source_position,
    render_nodes,
    render_positions,
    force_side=False
):

    source_x = source_position["x"]
    source_y = source_position["y"]

    if force_side:

        if source_x < MAIN_X:

            return {
                "x": source_x,
                "y": (
                    source_y
                    + SIDE_TERMINAL_MIN_GAP
                    + 20
                )
            }

        return {
            "x": source_x + HORIZONTAL_GAP,
            "y": source_y
        }

    if (
        source_x > MAIN_X + 80
        or source_x < MAIN_X - 80
    ):

        next_same_column_y = None

        for node in render_nodes:

            if node.type in [
                "END",
                "MERGE"
            ]:

                continue

            position = render_positions.get(
                node.id
            )

            if not position:

                continue

            if abs(
                position.get(
                    "x",
                    0
                ) - source_x
            ) > SIDE_COLUMN_TOLERANCE:

                continue

            candidate_y = position.get(
                "y",
                0
            )

            if candidate_y <= source_y:

                continue

            if (
                next_same_column_y is None
                or candidate_y < next_same_column_y
            ):

                next_same_column_y = candidate_y

        terminal_gap = SIDE_TERMINAL_MAX_GAP

        if next_same_column_y is not None:

            available_gap = (
                next_same_column_y
                - source_y
            )

            terminal_gap = min(
                SIDE_TERMINAL_MAX_GAP,
                max(
                    SIDE_TERMINAL_MIN_GAP,
                    available_gap - SIDE_TERMINAL_CLEARANCE
                )
            )

        return {
            "x": source_x,
            "y": source_y + terminal_gap
        }

    return {
        "x": source_x,
        "y": source_y + 220
    }


def resolve_visual_terminal_overlaps(
    render_nodes,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    def can_place(
        node_id,
        candidate_position
    ):

        current_position = dict(
            render_positions.get(
                node_id,
                {}
            )
        )

        if not current_position:

            return False

        render_positions[node_id] = {
            **current_position,
            **candidate_position
        }

        candidate_bounds = render_node_bounds(
            render_node_by_id,
            render_positions,
            node_id
        )

        render_positions[node_id] = current_position

        if not candidate_bounds:

            return False

        for other_id, other_node in render_node_by_id.items():

            if other_id == node_id:

                continue

            if other_node.type in [
                "MERGE",
                "CONNECTOR"
            ]:

                continue

            other_bounds = render_node_bounds(
                render_node_by_id,
                render_positions,
                other_id
            )

            if bounds_overlap(
                candidate_bounds,
                other_bounds
            ):

                return False

        return True

    for node in render_nodes:

        if node.type != "END":

            continue

        source_node_id = node.metadata.get(
            "source_node_id"
        )

        if not source_node_id:

            continue

        source_position = render_positions.get(
            source_node_id
        )

        terminal_position = render_positions.get(
            node.id
        )

        if not source_position or not terminal_position:

            continue

        terminal_bounds = render_node_bounds(
            render_node_by_id,
            render_positions,
            node.id
        )

        overlaps = False

        for other_id, other_node in render_node_by_id.items():

            if other_id in [
                node.id,
                source_node_id
            ]:

                continue

            if other_node.type in [
                "MERGE",
                "CONNECTOR"
            ]:

                continue

            other_bounds = render_node_bounds(
                render_node_by_id,
                render_positions,
                other_id
            )

            if bounds_overlap(
                terminal_bounds,
                other_bounds
            ):

                overlaps = True

                break

        if not overlaps:

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        source_y = source_position.get(
            "y",
            0
        )

        side_direction = (
            -1
            if source_x < MAIN_X
            else 1
        )

        candidates = [
            {
                "x": source_x + (side_direction * HORIZONTAL_GAP),
                "y": source_y
            },
            {
                "x": source_x + (side_direction * (HORIZONTAL_GAP + 120)),
                "y": source_y
            },
            {
                "x": source_x,
                "y": source_y + SIDE_TERMINAL_MIN_GAP
            },
            {
                "x": source_x,
                "y": source_y + SIDE_TERMINAL_MAX_GAP + 80
            }
        ]

        for candidate in candidates:

            if can_place(
                node.id,
                candidate
            ):

                render_positions[node.id] = {
                    **terminal_position,
                    **candidate
                }

                break


def is_connector_eligible_edge(
    edge,
    source_position,
    target_position
):

    if not source_position or not target_position:

        return False

    if edge.metadata.get(
        "render_expanded_error"
    ):

        return False

    vertical_distance = abs(
        source_position.get(
            "y",
            0
        ) - target_position.get(
            "y",
            0
        )
    )

    source_page_band = int(
        source_position.get(
            "y",
            0
        ) // CONNECTOR_PAGE_BAND_HEIGHT
    )

    target_page_band = int(
        target_position.get(
            "y",
            0
        ) // CONNECTOR_PAGE_BAND_HEIGHT
    )

    crosses_page_band = (
        source_page_band != target_page_band
    )

    if (
        vertical_distance < CONNECTOR_TRIGGER_DISTANCE
        and not crosses_page_band
    ):

        return False

    if edge.edge_type == "LOOPBACK":

        return True

    if edge.routing_role == "LOOPBACK":

        return True

    if (
        edge.edge_type == "CONDITIONAL"
        and is_restart_loop(edge)
    ):

        return True

    if (
        edge.edge_type == "CONDITIONAL"
        and edge.routing_role == "ERROR"
        and is_correction_return_edge(edge)
    ):

        return True

    return False


def make_connector_edge(
    source,
    target,
    edge,
    connector_label,
    segment,
    semantic_source=None,
    semantic_target=None
):

    return WorkflowEdge(

        source=source,

        target=target,

        edge_type=edge.edge_type,

        condition=(
            edge.condition
            if segment == "to_reference"
            else None
        ),

        routing_role=edge.routing_role,

        edge_label=(
            edge.edge_label
            if segment == "to_reference"
            else None
        ),

        metadata={
            **edge.metadata,
            "connector_segment": segment,
            "connector_label": connector_label,
            "semantic_source": semantic_source,
            "semantic_target": semantic_target,
            "routing_type_override": "CONNECTOR_STUB"
        }
    )


def split_long_connector_edges(
    render_nodes,
    render_edges,
    render_positions
):

    connector_nodes = []

    connector_edges = []

    next_connector_index = 1

    for edge in render_edges:

        source_position = render_positions.get(
            edge.source
        )

        target_position = render_positions.get(
            edge.target
        )

        if not is_connector_eligible_edge(
            edge,
            source_position,
            target_position
        ):

            connector_edges.append(edge)

            continue

        connector_label = connector_label_from_index(
            next_connector_index
        )

        next_connector_index += 1

        source_connector_id = f"REF_OUT_{connector_label}_{edge.source}_{edge.target}"

        target_connector_id = f"REF_IN_{connector_label}_{edge.source}_{edge.target}"

        connector_nodes.append(
            make_connector_node(
                source_connector_id,
                connector_label,
                edge,
                "out"
            )
        )

        connector_nodes.append(
            make_connector_node(
                target_connector_id,
                connector_label,
                edge,
                "in"
            )
        )

        source_is_right_of_target = (
            source_position.get(
                "x",
                0
            ) > target_position.get(
                "x",
                0
            )
        )

        source_connector_x = source_position.get(
            "x",
            0
        ) + (
            -CONNECTOR_SOURCE_OFFSET_X
            if source_is_right_of_target
            else CONNECTOR_SOURCE_OFFSET_X
        )

        target_connector_x = target_position.get(
            "x",
            0
        ) + (
            CONNECTOR_TARGET_OFFSET_X
            if source_is_right_of_target
            else -CONNECTOR_TARGET_OFFSET_X
        )

        render_positions[source_connector_id] = {
            "x": source_connector_x,
            "y": source_position.get(
                "y",
                0
            ) + CONNECTOR_OFFSET_Y
        }

        render_positions[target_connector_id] = {
            "x": target_connector_x,
            "y": target_position.get(
                "y",
                0
            ) + CONNECTOR_OFFSET_Y
        }

        connector_edges.append(
            make_connector_edge(
                edge.source,
                source_connector_id,
                edge,
                connector_label,
                "to_reference",
                semantic_target=edge.target
            )
        )

        connector_edges.append(
            make_connector_edge(
                target_connector_id,
                edge.target,
                edge,
                connector_label,
                "from_reference",
                semantic_source=edge.source
            )
        )

    render_nodes.extend(
        connector_nodes
    )

    return connector_edges


def build_render_model(
    graph,
    node_positions
):

    merge_retry_outgoing = {}

    for edge in graph.edges:

        source_node = graph.get_node(
            edge.source
        )

        if source_node and source_node.type == "MERGE":

            merge_retry_outgoing[edge.source] = edge

    collapsed_restart_helpers = set()

    collapsed_restart_edges = []

    visual_pass_through_response_ids = {
        node.id
        for node in graph.nodes.values()
        if is_visual_pass_through_response(
            graph,
            node
        )
    }

    visual_pass_through_edges = []

    for response_id in visual_pass_through_response_ids:

        incoming_edge = non_loopback_render_incoming_edges(
            graph,
            response_id
        )[0]

        outgoing_edge = non_loopback_render_edges(
            graph,
            response_id
        )[0]

        visual_pass_through_edges.append(
            WorkflowEdge(
                source=incoming_edge.source,
                target=outgoing_edge.target,
                edge_type="SEQUENCE",
                routing_role=outgoing_edge.routing_role,
                metadata={
                    **incoming_edge.metadata,
                    **outgoing_edge.metadata,
                    "collapsed_pass_through_response": True,
                    "hidden_response_id": response_id,
                    "semantic_source": incoming_edge.source,
                    "semantic_target": outgoing_edge.target
                }
            )
        )

    for edge in graph.edges:

        if not is_next_restart_helper_node(
            graph,
            edge.target
        ):

            continue

        helper_edges = graph.adjacency_map.get(
            edge.target,
            []
        )

        if not helper_edges:

            continue

        helper_edge = helper_edges[0]

        collapsed_restart_helpers.add(
            edge.target
        )

        collapsed_restart_edges.append(
            WorkflowEdge(

                source=edge.source,

                target=helper_edge.target,

                edge_type="LOOPBACK",

                condition="NEXT_EQUIPMENT",

                routing_role="LOOPBACK",

                edge_label=(
                    edge.edge_label
                    or edge.condition
                ),

                metadata={
                    "collapsed_restart_helper": True,
                    "helper_node_id": edge.target
                }
            )
        )

    render_nodes = [
        node
        for node in graph.nodes.values()
        if (
            node.type != "MERGE"
            and node.id not in collapsed_restart_helpers
            and node.id not in visual_pass_through_response_ids
        )
    ]

    render_positions = dict(
        node_positions
    )

    for hidden_node_id in visual_pass_through_response_ids:

        render_positions.pop(
            hidden_node_id,
            None
        )

    render_edges = []

    visual_terminal_ids = set()

    next_sa_index = get_next_system_activity_index(
        graph
    )

    error_count_by_source = {}

    direct_error_total_by_source = {}

    for edge in graph.edges:

        target_node = graph.get_node(
            edge.target
        )

        if target_node and target_node.type == "MERGE":

            merge_retry_edge = merge_retry_outgoing.get(
                edge.target
            )

            if merge_retry_edge:

                edge = WorkflowEdge(

                    source=edge.source,

                    target=merge_retry_edge.target,

                    edge_type=merge_retry_edge.edge_type,

                    condition=(
                        edge.condition
                        or edge.edge_label
                        or merge_retry_edge.condition
                    ),

                    routing_role=merge_retry_edge.routing_role,

                    edge_label=(
                        edge.edge_label
                        or edge.condition
                        or merge_retry_edge.edge_label
                    ),

                    metadata={
                        **edge.metadata,
                        **merge_retry_edge.metadata,
                        "collapsed_merge": True,
                        "virtual_merge_id": edge.target
                    }
                )

        if is_direct_error_return_edge(
            graph,
            edge,
            node_positions
        ):

            direct_error_total_by_source[edge.source] = (
                direct_error_total_by_source.get(
                    edge.source,
                    0
                ) + 1
            )

    expanded_error_nodes_by_source = {}

    for edge in graph.edges:

        if (
            edge.source in visual_pass_through_response_ids
            or edge.target in visual_pass_through_response_ids
        ):

            continue

        target_node = graph.get_node(
            edge.target
        )

        if target_node and target_node.type == "MERGE":

            merge_retry_edge = merge_retry_outgoing.get(
                edge.target
            )

            if merge_retry_edge:

                merge_collapsed_edge = WorkflowEdge(

                    source=edge.source,

                    target=merge_retry_edge.target,

                    edge_type=merge_retry_edge.edge_type,

                    condition=(
                        edge.condition
                        or edge.edge_label
                        or merge_retry_edge.condition
                    ),

                    routing_role=merge_retry_edge.routing_role,

                    edge_label=(
                        edge.edge_label
                        or edge.condition
                        or merge_retry_edge.edge_label
                    ),

                    metadata={
                        **edge.metadata,
                        **merge_retry_edge.metadata,
                        "collapsed_merge": True,
                        "virtual_merge_id": edge.target
                    }
                )

                if is_direct_error_return_edge(
                    graph,
                    merge_collapsed_edge,
                    node_positions
                ):

                    edge = merge_collapsed_edge

                else:

                    edge = merge_collapsed_edge

        if edge.target in collapsed_restart_helpers:

            continue

        if edge.source in collapsed_restart_helpers:

            continue

        if not (
            (
                edge.routing_role == "ERROR"
                and edge.edge_type == "CONDITIONAL"
            )
            or is_direct_error_return_edge(
                graph,
                edge,
                node_positions
            )
        ):

            continue

        if is_direct_error_return_edge(
            graph,
            edge,
            node_positions
        ):

            continue

        source_position = node_positions.get(
            edge.source
        )

        target_position = node_positions.get(
            edge.target
        )

        if not source_position or not target_position:

            continue

        if target_position.get("x", 0) <= source_position.get("x", 0) + 80:

            continue

        error_count_by_source[edge.source] = (
            error_count_by_source.get(
                edge.source,
                0
            ) + 1
        )

    for edge in graph.edges:

        target_node = graph.get_node(
            edge.target
        )

        if target_node and target_node.type == "MERGE":

            merge_retry_edge = merge_retry_outgoing.get(
                edge.target
            )

            if merge_retry_edge:

                merge_collapsed_edge = WorkflowEdge(

                    source=edge.source,

                    target=merge_retry_edge.target,

                    edge_type=merge_retry_edge.edge_type,

                    condition=(
                        edge.condition
                        or edge.edge_label
                        or merge_retry_edge.condition
                    ),

                    routing_role=merge_retry_edge.routing_role,

                    edge_label=(
                        edge.edge_label
                        or edge.condition
                        or merge_retry_edge.edge_label
                    ),

                    metadata={
                        **edge.metadata,
                        **merge_retry_edge.metadata,
                        "collapsed_merge": True,
                        "virtual_merge_id": edge.target
                    }
                )

                if is_direct_error_return_edge(
                    graph,
                    merge_collapsed_edge,
                    node_positions
                ):

                    edge = merge_collapsed_edge

                else:

                    edge = merge_collapsed_edge

        if edge.target in collapsed_restart_helpers:

            continue

        if edge.source in collapsed_restart_helpers:

            continue

        if (
            is_side_terminal_end_edge(
                graph,
                edge,
                node_positions
            )
            or is_side_terminal_outcome_end_edge(
                graph,
                edge,
                node_positions
            )
        ):

            force_side_terminal = is_side_terminal_outcome_end_edge(
                graph,
                edge,
                node_positions
            )

            target_node = graph.get_node(
                edge.target
            )

            visual_terminal_node = build_visual_terminal_node(
                target_node,
                edge
            )

            if visual_terminal_node.id not in visual_terminal_ids:

                visual_terminal_ids.add(
                    visual_terminal_node.id
                )

                render_nodes.append(
                    visual_terminal_node
                )

                source_position = node_positions[
                    edge.source
                ]

                render_positions[visual_terminal_node.id] = (
                    position_visual_terminal_node(
                        source_position,
                        render_nodes,
                        render_positions,
                        force_side_terminal
                    )
                )

            render_edges.append(
                WorkflowEdge(

                    source=edge.source,

                    target=visual_terminal_node.id,

                    edge_type=edge.edge_type,

                    condition=edge.condition,

                    routing_role=edge.routing_role,

                    edge_label=edge.edge_label,

                    metadata={
                        **edge.metadata,
                        "visual_terminal_edge": True,
                        "semantic_target": edge.target
                    }
                )
            )

            continue

        if is_direct_error_return_edge(
            graph,
            edge,
            node_positions
        ):

            error_count_by_source[edge.source] = (
                error_count_by_source.get(
                    edge.source,
                    0
                ) + 1
            )

            branch_index = error_count_by_source[
                edge.source
            ]

            error_node_id = f"SA{next_sa_index}"

            next_sa_index += 1

            label = make_error_label(
                edge.edge_label
                or edge.condition
            )

            source_position = node_positions[
                edge.source
            ]

            direct_error_total = direct_error_total_by_source.get(
                edge.source,
                1
            )

            error_node_y = (
                source_position["y"]
                if direct_error_total <= 1
                else source_position["y"]
                + (
                    (branch_index - 1)
                    * ERROR_BRANCH_VERTICAL_GAP
                )
            )

            render_nodes.append(
                WorkflowNode(

                    id=error_node_id,

                    type="SYSTEM_ACTIVITY",

                    label=label,

                    step_number=error_node_id,

                    lane="ERROR",

                    group="ERROR_HANDLING"
                )
            )

            render_positions[error_node_id] = {
                "x": ERROR_COLUMN_X,
                "y": error_node_y
            }

            expanded_error_nodes_by_source.setdefault(
                edge.source,
                []
            ).append(
                error_node_id
            )

            render_edges.append(
                WorkflowEdge(

                    source=edge.source,

                    target=error_node_id,

                    edge_type="CONDITIONAL",

                    condition=edge.condition,

                    routing_role="ERROR",

                    edge_label=edge.edge_label,

                    metadata=edge.metadata
                )
            )

            render_edges.append(
                WorkflowEdge(

                    source=error_node_id,

                    target=edge.target,

                    edge_type="LOOPBACK",

                    routing_role="LOOPBACK",

                    metadata={
                        "render_expanded_error": True
                    }
                )
            )

            continue

        render_edges.append(edge)

    render_edges.extend(
        visual_pass_through_edges
    )

    apply_expanded_error_section_spacing(
        graph,
        render_positions,
        expanded_error_nodes_by_source
    )

    resolve_render_position_collisions(
        render_nodes,
        render_edges,
        render_positions
    )

    resolve_remaining_render_overlaps(
        render_nodes,
        render_edges,
        render_positions
    )

    align_expanded_error_nodes_to_sources(
        graph,
        render_positions,
        expanded_error_nodes_by_source
    )

    apply_expanded_error_section_spacing(
        graph,
        render_positions,
        expanded_error_nodes_by_source
    )

    render_edges.extend(
        collapsed_restart_edges
    )

    split_collapsed_response_option_branches(
        render_nodes,
        render_edges,
        render_positions
    )

    move_mixed_response_side_branches_left(
        render_nodes,
        render_edges,
        render_positions
    )

    move_left_owned_success_branch_nodes_left(
        render_nodes,
        render_edges,
        render_positions
    )

    move_left_owned_correction_branches_left(
        render_nodes,
        render_edges,
        render_positions
    )

    enforce_rendered_error_target_stack(
        render_nodes,
        render_edges,
        render_positions
    )

    compact_left_business_branch_chains(
        render_nodes,
        render_edges,
        render_positions
    )

    resolve_visual_terminal_overlaps(
        render_nodes,
        render_positions
    )

    if ENABLE_REFERENCE_CONNECTORS:

        render_edges = split_long_connector_edges(
            render_nodes,
            render_edges,
            render_positions
        )

    return render_nodes, render_edges, render_positions


def align_expanded_error_nodes_to_sources(
    graph,
    render_positions,
    expanded_error_nodes_by_source
):

    for source_id, error_node_ids in expanded_error_nodes_by_source.items():

        source_position = render_positions.get(
            source_id
        )

        if not source_position:

            continue

        visible_error_node_ids = [
            node_id
            for node_id in error_node_ids
            if node_id in render_positions
        ]

        if not visible_error_node_ids:

            continue

        has_source_side_branch = any(
            edge.routing_role == "SIDE_BRANCH"
            for edge in graph.adjacency_map.get(
                source_id,
                []
            )
        )

        for index, node_id in enumerate(
            visible_error_node_ids
        ):

            render_positions[node_id]["y"] = (
                source_position.get(
                    "y",
                    0
                )
                + (
                    index
                    + (
                        1
                        if has_source_side_branch
                        else 0
                    )
                    * ERROR_BRANCH_VERTICAL_GAP
                )
            )


def apply_expanded_error_section_spacing(
    graph,
    render_positions,
    expanded_error_nodes_by_source
):

    if not expanded_error_nodes_by_source:

        return

    sources = sorted(
        expanded_error_nodes_by_source,
        key=lambda source_id: render_positions.get(
            source_id,
            {}
        ).get(
            "y",
            0
        )
    )

    for source_id in sources:

        source_position = render_positions.get(
            source_id
        )

        if not source_position:

            continue

        error_node_ids = [
            node_id
            for node_id in expanded_error_nodes_by_source[source_id]
            if node_id in render_positions
        ]

        if len(error_node_ids) <= 1:

            continue

        next_main_targets = []

        for edge in graph.adjacency_map.get(
            source_id,
            []
        ):

            if edge.routing_role not in [
                "SUCCESS",
                "MAIN_FLOW"
            ]:

                continue

            target_position = render_positions.get(
                edge.target
            )

            if not target_position:

                continue

            if target_position.get(
                "y",
                0
            ) <= source_position.get(
                "y",
                0
            ):

                continue

            next_main_targets.append(
                (
                    target_position["y"],
                    edge.target
                )
            )

        if not next_main_targets:

            continue

        current_next_y, _ = min(
            next_main_targets
        )

        error_section_bottom = max(
            render_positions[node_id]["y"]
            for node_id in error_node_ids
        )

        required_next_y = (
            error_section_bottom
            + POST_ERROR_MAIN_GAP
        )

        shift_y = required_next_y - current_next_y

        if shift_y <= 0:

            continue

        excluded_nodes = set(
            error_node_ids
        )

        for node_id, position in render_positions.items():

            if node_id in excluded_nodes:

                continue

            if position.get(
                "y",
                0
            ) < current_next_y:

                continue

            position["y"] = (
                position["y"]
                + shift_y
            )


def enforce_rendered_error_target_stack(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    def can_place_error_target(
        target_id,
        candidate_x,
        candidate_y
    ):

        current_position = dict(
            render_positions.get(
                target_id,
                {}
            )
        )

        if not current_position:

            return False

        render_positions[target_id] = {
            **current_position,
            "x": candidate_x,
            "y": candidate_y
        }

        candidate_bounds = render_node_bounds(
            render_node_by_id,
            render_positions,
            target_id
        )

        render_positions[target_id] = current_position

        if not candidate_bounds:

            return False

        for node_id in render_node_by_id:

            if node_id == target_id:

                continue

            if node_id not in render_positions:

                continue

            node = render_node_by_id.get(
                node_id
            )

            if not node or node.type in [
                "MERGE",
                "CONNECTOR"
            ]:

                continue

            other_bounds = render_node_bounds(
                render_node_by_id,
                render_positions,
                node_id
            )

            if bounds_overlap(
                candidate_bounds,
                other_bounds
            ):

                return False

        return True

    error_targets_by_source = {}

    for edge in render_edges:

        if edge.routing_role != "ERROR":

            continue

        source_position = render_positions.get(
            edge.source
        )

        target_position = render_positions.get(
            edge.target
        )

        target_node = render_node_by_id.get(
            edge.target
        )

        if not source_position or not target_position or not target_node:

            continue

        if target_node.type != "SYSTEM_ACTIVITY":

            continue

        if target_position.get(
            "x",
            MAIN_X
        ) <= source_position.get(
            "x",
            MAIN_X
        ) + 80:

            continue

        error_targets_by_source.setdefault(
            edge.source,
            []
        ).append(
            edge.target
        )

    for source_id, target_ids in error_targets_by_source.items():

        source_position = render_positions.get(
            source_id
        )

        if not source_position:

            continue

        has_side_branch = any(
            edge.source == source_id
            and edge.routing_role == "SIDE_BRANCH"
            for edge in render_edges
        )

        unique_target_ids = []

        for target_id in target_ids:

            if target_id not in unique_target_ids:

                unique_target_ids.append(
                    target_id
                )

        unique_target_ids.sort(
            key=lambda node_id: render_positions.get(
                node_id,
                {}
            ).get(
                "y",
                source_position.get(
                    "y",
                    0
                )
            )
        )

        for index, target_id in enumerate(
            unique_target_ids
        ):

            stack_offset = (
                1
                if has_side_branch
                and len(unique_target_ids) > 1
                else 0
            )

            candidate_y = (
                source_position.get(
                    "y",
                    0
                )
                + (
                    index
                    + stack_offset
                )
                * ERROR_BRANCH_VERTICAL_GAP
            )

            candidate_x = max(
                source_position.get(
                    "x",
                    MAIN_X
                ) + HORIZONTAL_GAP,
                ERROR_COLUMN_X
            )

            if can_place_error_target(
                target_id,
                candidate_x,
                candidate_y
            ):

                render_positions[target_id]["x"] = candidate_x

            render_positions[target_id]["y"] = (
                candidate_y
            )


def rendered_non_loopback_incoming(render_edges, node_id):

    return [
        edge
        for edge in render_edges
        if edge.target == node_id
        and edge.routing_role != "LOOPBACK"
        and edge.edge_type != "LOOPBACK"
    ]


def is_shared_rejoin_target(
    render_edges,
    edge
):

    incoming = rendered_non_loopback_incoming(
        render_edges,
        edge.target
    )

    if len(
        incoming
    ) < 2:

        return False

    return any(
        incoming_edge.source != edge.source
        and incoming_edge.routing_role in [
            "SUCCESS",
            "MAIN_FLOW",
            "LOCAL_CONTINUATION"
        ]
        for incoming_edge in incoming
    )


def collect_render_side_branch_chain(
    render_node_by_id,
    render_edges,
    start_id,
    stop_at_shared=True
):

    branch_nodes = set()
    queue = [
        start_id
    ]

    while queue:

        node_id = queue.pop(
            0
        )

        if node_id in branch_nodes:

            continue

        node = render_node_by_id.get(
            node_id
        )

        if not node or node.type in [
            "MERGE",
            "END"
        ]:

            continue

        incoming = rendered_non_loopback_incoming(
            render_edges,
            node_id
        )

        if (
            stop_at_shared
            and node_id != start_id
            and len(
                incoming
            ) > 1
        ):

            continue

        if (
            node_id != start_id
            and incoming
            and any(
                edge.source not in branch_nodes
                for edge in incoming
            )
        ):

            continue

        branch_nodes.add(
            node_id
        )

        for edge in render_edges:

            if edge.source != node_id:

                continue

            if edge.routing_role == "LOOPBACK" or edge.edge_type == "LOOPBACK":

                continue

            if edge.routing_role not in [
                "MAIN_FLOW",
                "SUCCESS",
                "SIDE_BRANCH",
                "LOCAL_CONTINUATION"
            ]:

                continue

            queue.append(
                edge.target
            )

    return branch_nodes


def move_mixed_response_side_branches_left(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    for source_id in {
        edge.source
        for edge in render_edges
    }:

        source_node = render_node_by_id.get(
            source_id
        )

        source_position = render_positions.get(
            source_id
        )

        if not source_node or source_node.type != "RESPONSE" or not source_position:

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        right_error_exists = any(
            edge.source == source_id
            and edge.routing_role == "ERROR"
            and render_positions.get(
                edge.target,
                {}
            ).get(
                "x",
                MAIN_X
            ) > source_x + 80
            for edge in render_edges
        )

        if not right_error_exists:

            continue

        for edge in render_edges:

            if edge.source != source_id or edge.routing_role != "SIDE_BRANCH":

                continue

            target_position = render_positions.get(
                edge.target
            )

            if not target_position:

                continue

            if target_position.get(
                "x",
                MAIN_X
            ) <= source_x:

                continue

            branch_nodes = {
                edge.target
            }

            target_left_x = source_x - HORIZONTAL_GAP
            delta_x = target_left_x - target_position.get(
                "x",
                target_left_x
            )

            for node_id in branch_nodes:

                if node_id in render_positions:

                    render_positions[node_id]["x"] += delta_x


def target_returns_to_left_owned_section(
    render_edges,
    source_id,
    target_id,
    source_x,
    render_positions
):

    for edge in render_edges:

        if edge.source != target_id:

            continue

        if edge.routing_role != "LOOPBACK" and edge.edge_type != "LOOPBACK":

            continue

        target_position = render_positions.get(
            edge.target
        )

        if not target_position:

            continue

        if target_position.get(
            "x",
            MAIN_X
        ) <= source_x + SIDE_COLUMN_TOLERANCE:

            return True

    return False


def move_left_owned_correction_branches_left(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    for edge in render_edges:

        if edge.routing_role != "ERROR":

            continue

        source_node = render_node_by_id.get(
            edge.source
        )

        target_node = render_node_by_id.get(
            edge.target
        )

        source_position = render_positions.get(
            edge.source
        )

        target_position = render_positions.get(
            edge.target
        )

        if not source_node or not target_node or not source_position or not target_position:

            continue

        if source_node.type != "RESPONSE":

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        target_x = target_position.get(
            "x",
            MAIN_X
        )

        if source_x >= MAIN_X:

            continue

        if target_x < MAIN_X:

            continue

        if not target_returns_to_left_owned_section(
            render_edges,
            edge.source,
            edge.target,
            source_x,
            render_positions
        ):

            continue

        branch_nodes = collect_render_side_branch_chain(
            render_node_by_id,
            render_edges,
            edge.target
        )

        target_left_x = source_x - HORIZONTAL_GAP
        delta_x = target_left_x - target_x

        for node_id in branch_nodes:

            if node_id in render_positions:

                render_positions[node_id]["x"] += delta_x


def move_left_owned_success_branch_nodes_left(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    for edge in render_edges:

        if edge.routing_role not in [
            "SUCCESS",
            "LOCAL_CONTINUATION"
        ]:

            continue

        source_node = render_node_by_id.get(
            edge.source
        )

        target_node = render_node_by_id.get(
            edge.target
        )

        source_position = render_positions.get(
            edge.source
        )

        target_position = render_positions.get(
            edge.target
        )

        if not source_node or not target_node or not source_position or not target_position:

            continue

        if source_node.type != "RESPONSE":

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        target_x = target_position.get(
            "x",
            MAIN_X
        )

        if source_x >= MAIN_X or target_x <= source_x:

            continue

        incoming = rendered_non_loopback_incoming(
            render_edges,
            edge.target
        )

        if len(incoming) != 1:

            continue

        branch_nodes = collect_render_side_branch_chain(
            render_node_by_id,
            render_edges,
            edge.target
        )

        if not branch_nodes:

            continue

        delta_x = source_x - target_x

        for node_id in branch_nodes:

            if node_id in render_positions:

                render_positions[node_id]["x"] += delta_x


def split_collapsed_response_option_branches(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    for source_id in {
        edge.source
        for edge in render_edges
    }:

        source_node = render_node_by_id.get(
            source_id
        )

        source_position = render_positions.get(
            source_id
        )

        if not source_node or source_node.type != "RESPONSE" or not source_position:

            continue

        option_edges = [
            edge
            for edge in render_edges
            if (
                edge.source == source_id
                and edge.routing_role in [
                    "SUCCESS",
                    "SIDE_BRANCH",
                    "LOCAL_CONTINUATION"
                ]
                and edge.edge_type != "LOOPBACK"
            )
        ]

        if len(
            option_edges
        ) < 2:

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        collapsed_edges = [
            edge
            for edge in option_edges
            if (
                edge.target in render_positions
                and abs(
                    render_positions[edge.target].get(
                        "x",
                        MAIN_X
                    )
                    - source_x
                ) <= SIDE_COLUMN_TOLERANCE
            )
        ]

        if len(
            collapsed_edges
        ) < 2:

            continue

        side_edges = [
            edge
            for edge in collapsed_edges
            if edge.routing_role in [
                "SIDE_BRANCH",
                "LOCAL_CONTINUATION"
            ]
        ]

        if not side_edges:

            side_edges = collapsed_edges[1:]

        for index, edge in enumerate(
            side_edges
        ):

            if is_shared_rejoin_target(
                render_edges,
                edge
            ):

                continue

            branch_nodes = {
                edge.target
            }

            if not branch_nodes:

                continue

            direction = (
                -1
                if index % 2 == 0
                else 1
            )

            target_x = source_x + (
                direction * HORIZONTAL_GAP
            )

            current_x = render_positions[edge.target].get(
                "x",
                source_x
            )

            delta_x = target_x - current_x

            for node_id in branch_nodes:

                if node_id in render_positions:

                    render_positions[node_id]["x"] += delta_x


def compact_left_business_branch_chains(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    for edge in render_edges:

        if edge.routing_role != "SIDE_BRANCH":

            continue

        source_node = render_node_by_id.get(
            edge.source
        )

        source_position = render_positions.get(
            edge.source
        )

        target_position = render_positions.get(
            edge.target
        )

        if not source_node or source_node.type != "RESPONSE":

            continue

        if not source_position or not target_position:

            continue

        source_x = source_position.get(
            "x",
            MAIN_X
        )

        if target_position.get(
            "x",
            MAIN_X
        ) >= source_x:

            continue

        right_error_exists = any(
            sibling.source == edge.source
            and sibling.routing_role == "ERROR"
            and render_positions.get(
                sibling.target,
                {}
            ).get(
                "x",
                MAIN_X
            ) > source_x + 80
            for sibling in render_edges
        )

        if not right_error_exists:

            continue

        branch_nodes = collect_render_side_branch_chain(
            render_node_by_id,
            render_edges,
            edge.target
        )

        if edge.target in render_positions:

            render_positions[edge.target]["y"] = source_position.get(
                "y",
                0
            )

        queue = [
            edge.target
        ]

        visited = set()

        while queue:

            node_id = queue.pop(
                0
            )

            if node_id in visited:

                continue

            visited.add(
                node_id
            )

            current_y = render_positions.get(
                node_id,
                {}
            ).get(
                "y"
            )

            if current_y is None:

                continue

            for outgoing_edge in render_edges:

                if outgoing_edge.source != node_id:

                    continue

                if outgoing_edge.target not in branch_nodes:

                    continue

                if outgoing_edge.routing_role == "LOOPBACK" or outgoing_edge.edge_type == "LOOPBACK":

                    continue

                target_position = render_positions.get(
                    outgoing_edge.target
                )

                if not target_position:

                    continue

                target_position["y"] = current_y + 190

                queue.append(
                    outgoing_edge.target
                )


def render_collision_priority(
    node
):

    if not node:

        return 9

    if node.type in [
        "START",
        "END",
        "MERGE",
        "CONNECTOR"
    ]:

        return 0

    if node.type in [
        "RESPONSE",
        "DECISION",
        "SYSTEM_CHECK",
        "MANUAL_ACTIVITY"
    ]:

        return 1

    if node.group == "ERROR_HANDLING":

        return 4

    if node.type == "SYSTEM_ACTIVITY":

        return 3

    return 2


def render_incoming_roles(
    render_edges
):

    incoming_roles = {}

    for edge in render_edges:

        incoming_roles.setdefault(
            edge.target,
            []
        ).append(
            edge.routing_role
        )

    return incoming_roles


def same_source_right_error_targets(
    render_edges,
    render_node_by_id,
    render_positions
):

    protected = set()

    edges_by_source = {}

    for edge in render_edges:

        edges_by_source.setdefault(
            edge.source,
            []
        ).append(
            edge
        )

    for source_id, edges in edges_by_source.items():

        source = render_node_by_id.get(
            source_id
        )

        source_position = render_positions.get(
            source_id
        )

        if not source or source.type != "RESPONSE" or not source_position:

            continue

        targets = []

        for edge in edges:

            target = render_node_by_id.get(
                edge.target
            )

            target_position = render_positions.get(
                edge.target
            )

            if not target or not target_position:

                continue

            if edge.routing_role != "ERROR":

                continue

            if target.type != "SYSTEM_ACTIVITY":

                continue

            if target_position.get(
                "x",
                MAIN_X
            ) < source_position.get(
                "x",
                MAIN_X
            ):

                continue

            targets.append(
                edge.target
            )

        if len(
            targets
        ) < 2:

            continue

        protected.update(
            targets
        )

    return protected


def same_source_expanded_error_targets(
    render_edges,
    render_node_by_id,
    render_positions
):

    targets_by_source = {}

    for edge in render_edges:

        if edge.routing_role != "ERROR":

            continue

        target_node = render_node_by_id.get(
            edge.target
        )

        if not target_node or target_node.group != "ERROR_HANDLING":

            continue

        if (
            edge.source not in render_positions
            or edge.target not in render_positions
        ):

            continue

        targets_by_source.setdefault(
            edge.source,
            []
        ).append(
            edge.target
        )

    protected = set()

    for targets in targets_by_source.values():

        if len(targets) > 1:

            protected.update(
                targets
            )

    return protected


def is_render_branch_node(
    node,
    incoming_roles
):

    if not node:

        return False

    roles = incoming_roles.get(
        node.id,
        []
    )

    return (
        node.group == "ERROR_HANDLING"
        or any(
            role in [
                "ERROR",
                "SIDE_BRANCH"
            ]
            for role in roles
        )
    ) and not any(
        role in [
            "MAIN_FLOW",
            "LOCAL_CONTINUATION"
        ]
        for role in roles
    )


def render_collision_at(
    render_node_by_id,
    render_positions,
    node_id,
    candidate_x,
    candidate_y,
    occupied
):

    node = render_node_by_id.get(
        node_id
    )

    if not node:

        return None

    original_position = render_positions.get(
        node_id,
        {}
    )

    old_x = original_position.get(
        "x",
        candidate_x
    )

    old_y = original_position.get(
        "y",
        candidate_y
    )

    original_position["x"] = candidate_x

    original_position["y"] = candidate_y

    candidate_bounds = render_node_bounds(
        render_node_by_id,
        render_positions,
        node_id,
        padding=RENDER_COLLISION_PADDING
    )

    original_position["x"] = old_x

    original_position["y"] = old_y

    for bounds in occupied.values():

        if bounds_overlap(
            candidate_bounds,
            bounds
        ):

            return bounds

    return None


def render_branch_x_candidates(
    node,
    render_positions
):

    position = render_positions.get(
        node.id,
        {}
    )

    current_x = position.get(
        "x",
        MAIN_X
    )

    direction = (
        1
        if current_x >= MAIN_X
        else -1
    )

    candidates = [
        current_x,
        current_x + (
            direction * HORIZONTAL_GAP
        ),
        current_x - (
            direction * HORIZONTAL_GAP
        ),
        MAIN_X + (
            direction * HORIZONTAL_GAP
        ),
        MAIN_X - (
            direction * HORIZONTAL_GAP
        )
    ]

    unique_candidates = []

    for candidate in candidates:

        if candidate in unique_candidates:

            continue

        unique_candidates.append(
            candidate
        )

    return unique_candidates


def render_node_overlap_pairs(
    render_nodes,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    node_ids = [
        node.id
        for node in render_nodes
        if (
            node.id in render_positions
            and node.type not in [
                "CONNECTOR",
                "MERGE"
            ]
        )
    ]

    overlaps = []

    for index, first_id in enumerate(
        node_ids
    ):

        first_bounds = render_node_bounds(
            render_node_by_id,
            render_positions,
            first_id,
            padding=RENDER_COLLISION_PADDING
        )

        for second_id in node_ids[index + 1:]:

            second_bounds = render_node_bounds(
                render_node_by_id,
                render_positions,
                second_id,
                padding=RENDER_COLLISION_PADDING
            )

            if bounds_overlap(
                first_bounds,
                second_bounds
            ):

                overlaps.append(
                    (
                        first_id,
                        second_id
                    )
                )

    return overlaps


def candidate_overlaps_render_nodes(
    render_node_by_id,
    render_positions,
    node_id,
    candidate_x,
    candidate_y,
    excluded_node_ids=None
):

    excluded_node_ids = set(
        excluded_node_ids
        or []
    )

    candidate_bounds = None

    node = render_node_by_id.get(
        node_id
    )

    if not node:

        return True

    position = render_positions.get(
        node_id,
        {}
    )

    old_x = position.get(
        "x",
        candidate_x
    )

    old_y = position.get(
        "y",
        candidate_y
    )

    position["x"] = candidate_x

    position["y"] = candidate_y

    candidate_bounds = render_node_bounds(
        render_node_by_id,
        render_positions,
        node_id,
        padding=RENDER_COLLISION_PADDING
    )

    position["x"] = old_x

    position["y"] = old_y

    for other_id in render_node_by_id:

        if (
            other_id == node_id
            or other_id in excluded_node_ids
            or other_id not in render_positions
        ):

            continue

        other_node = render_node_by_id.get(
            other_id
        )

        if other_node and other_node.type in [
            "CONNECTOR",
            "MERGE"
        ]:

            continue

        other_bounds = render_node_bounds(
            render_node_by_id,
            render_positions,
            other_id,
            padding=RENDER_COLLISION_PADDING
        )

        if bounds_overlap(
            candidate_bounds,
            other_bounds
        ):

            return True

    return False


def choose_overlap_movable_node(
    render_node_by_id,
    first_id,
    second_id
):

    first_node = render_node_by_id.get(
        first_id
    )

    second_node = render_node_by_id.get(
        second_id
    )

    first_priority = render_collision_priority(
        first_node
    )

    second_priority = render_collision_priority(
        second_node
    )

    if first_priority > second_priority:

        return first_id

    if second_priority > first_priority:

        return second_id

    return (
        first_id
        if first_id > second_id
        else second_id
    )


def resolve_remaining_render_overlaps(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    incoming_roles = render_incoming_roles(
        render_edges
    )

    protected_error_columns = same_source_right_error_targets(
        render_edges,
        render_node_by_id,
        render_positions
    )

    protected_error_columns.update(
        same_source_expanded_error_targets(
            render_edges,
            render_node_by_id,
            render_positions
        )
    )

    max_iterations = max(
        4,
        len(render_nodes) * 2
    )

    for _ in range(max_iterations):

        overlaps = render_node_overlap_pairs(
            render_nodes,
            render_positions
        )

        if not overlaps:

            return []

        moved_any = False

        for first_id, second_id in overlaps:

            movable_id = choose_overlap_movable_node(
                render_node_by_id,
                first_id,
                second_id
            )

            movable_node = render_node_by_id.get(
                movable_id
            )

            position = render_positions.get(
                movable_id
            )

            if not movable_node or not position:

                continue

            candidate_x_values = (
                render_branch_x_candidates(
                    movable_node,
                    render_positions
                )
                if is_render_branch_node(
                    movable_node,
                    incoming_roles
                )
                and movable_id not in protected_error_columns
                else [
                    position.get(
                        "x",
                        MAIN_X
                    )
                ]
            )

            for candidate_x in candidate_x_values:

                if candidate_overlaps_render_nodes(
                    render_node_by_id,
                    render_positions,
                    movable_id,
                    candidate_x,
                    position.get(
                        "y",
                        0
                    )
                ):

                    continue

                position["x"] = candidate_x

                moved_any = True

                break

            if moved_any:

                break

            _, node_height = estimate_node_size(
                movable_node.label
            )

            position["y"] = (
                position.get(
                    "y",
                    0
                )
                + node_height
                + 34
            )

            moved_any = True

            break

        if not moved_any:

            break

    return render_node_overlap_pairs(
        render_nodes,
        render_positions
    )


def resolve_render_position_collisions(
    render_nodes,
    render_edges,
    render_positions
):

    render_node_by_id = {
        node.id: node
        for node in render_nodes
    }

    incoming_roles = render_incoming_roles(
        render_edges
    )

    protected_error_columns = same_source_right_error_targets(
        render_edges,
        render_node_by_id,
        render_positions
    )

    ordered_node_ids = sorted(
        [
            node.id
            for node in render_nodes
            if node.id in render_positions
        ],
        key=lambda node_id: (
            render_positions.get(
                node_id,
                {}
            ).get(
                "y",
                0
            ),
            render_collision_priority(
                render_node_by_id.get(
                    node_id
                )
            ),
            render_positions.get(
                node_id,
                {}
            ).get(
                "x",
                0
            )
        )
    )

    occupied = {}

    for node_id in ordered_node_ids:

        node = render_node_by_id.get(
            node_id
        )

        if not node:

            continue

        position = render_positions.get(
            node_id
        )

        if not position:

            continue

        resolved = False

        if is_render_branch_node(
            node,
            incoming_roles
        ) and node_id not in protected_error_columns:

            for candidate_x in render_branch_x_candidates(
                node,
                render_positions
            ):

                if render_collision_at(
                    render_node_by_id,
                    render_positions,
                    node_id,
                    candidate_x,
                    position.get(
                        "y",
                        0
                    ),
                    occupied
                ):

                    continue

                position["x"] = candidate_x

                resolved = True

                break

        if not resolved:

            collision = render_collision_at(
                render_node_by_id,
                render_positions,
                node_id,
                position.get(
                    "x",
                    0
                ),
                position.get(
                    "y",
                    0
                ),
                occupied
            )

            guard = 0

            while collision and guard < len(render_nodes):

                guard += 1

                _, node_height = estimate_node_size(
                    node.label
                )

                position["y"] = (
                    collision["bottom"]
                    + (
                        node_height / 2
                    )
                    + 34
                )

                collision = render_collision_at(
                    render_node_by_id,
                    render_positions,
                    node_id,
                    position.get(
                        "x",
                        0
                    ),
                    position.get(
                        "y",
                        0
                    ),
                    occupied
                )

        occupied[node_id] = render_node_bounds(
            render_node_by_id,
            render_positions,
            node_id,
            padding=RENDER_COLLISION_PADDING
        )


def build_reactflow_nodes(

    nodes,

    node_positions,

    edges=None
):

    reactflow_nodes = []

    error_activity_targets = set()

    node_by_id = {
        node.id: node
        for node in nodes
    }

    outgoing_edges_by_source = {}

    for edge in (edges or []):

        outgoing_edges_by_source.setdefault(
            edge.source,
            []
        ).append(edge)

    for edge in (edges or []):

        target_node = node_by_id.get(
            edge.target
        )

        if not target_node or target_node.type != "SYSTEM_ACTIVITY":

            continue

        source_node = node_by_id.get(
            edge.source
        )

        source_position = node_positions.get(
            edge.source,
            {}
        )

        target_position = node_positions.get(
            edge.target,
            {}
        )

        if (
            edge.routing_role == "ERROR"
            and
            target_position.get("x", 0)
            > source_position.get("x", 0) + 80
        ):

            error_activity_targets.add(
                edge.target
            )

            continue

        target_has_retry_loopback = any(
            (
                outgoing_edge.edge_type == "LOOPBACK"
                or outgoing_edge.routing_role == "LOOPBACK"
                or str(
                    outgoing_edge.target
                ).startswith("MERGE")
            )
            for outgoing_edge in outgoing_edges_by_source.get(
                edge.target,
                []
            )
        )

        source_is_system_response = (
            source_node
            and source_node.type == "RESPONSE"
            and (
                not source_node.response_actor
                or source_node.response_actor == "SYSTEM"
            )
        )

        if (
            source_is_system_response
            and target_has_retry_loopback
            and not is_success_outcome_label(
                edge
            )
            and (
                edge.routing_role in [
                    "ERROR",
                    "SIDE_BRANCH"
                ]
                or is_retry_error_label(
                    edge
                )
            )
        ):

            error_activity_targets.add(
                edge.target
            )

    for node in nodes:

        if node.type != "SYSTEM_ACTIVITY":

            continue

        has_retry_return = any(
            (
                outgoing_edge.edge_type == "LOOPBACK"
                or outgoing_edge.routing_role == "LOOPBACK"
                or str(
                    outgoing_edge.target
                ).startswith("MERGE")
            )
            for outgoing_edge in outgoing_edges_by_source.get(
                node.id,
                []
            )
        )

        if (
            has_retry_return
            and is_retry_error_text(
                node.label
            )
        ):

            error_activity_targets.add(
                node.id
            )

    display_step_numbers = build_display_step_numbers(
        nodes,
        edges,
        node_positions
    )


    for node in nodes:

        if node.type == "MERGE":

            continue

        position = node_positions.get(

            node.id,

            {
                "x": 0,
                "y": 0
            }
        )

        display_step_number = display_step_numbers.get(
            node.id,
            node.step_number
        )

        display_label = build_node_display_label(
            node,
            display_step_number
        )

        if node.type == "CONNECTOR":

            display_label = node.label

        is_error_activity = (
            node.id in error_activity_targets
            and node.type == "SYSTEM_ACTIVITY"
        ) or (
            node.group == "ERROR_HANDLING"
            and node.type == "SYSTEM_ACTIVITY"
        )

        node_width, node_height = estimate_node_size(
            display_label
        )

        visual_type = get_node_visual_type(
            node
        )

        if node.type == "CONNECTOR":

            node_width = 44

            node_height = 44

        reactflow_node = {

            "id": node.id,

            "type": node.type.lower(),

            "position": {

                "x": position["x"],

                "y": position["y"]
            },

            "data": {

                "label": node.label,

                "step_number": node.step_number,

                "display_step_number": display_step_number,

                "display_label": display_label,

                "lane": node.lane,

                "group": node.group,

                "actor": node.actor,
                "response_actor": node.response_actor,

                "event_type": node.event_type,

                "is_error_activity": is_error_activity,

                "metadata": node.metadata,

                "visual_type": visual_type,

                "width": node_width,

                "height": node_height,
            }
        }


        reactflow_nodes.append(
            reactflow_node
        )


    return reactflow_nodes


# ===================================
# GET EDGE STYLE
# ===================================

def get_edge_style(routing_type):

    edge_color = "#6B7280"

    animated = False


    # ===================================
    # STRAIGHT FLOW
    # ===================================

    if routing_type in [
        "STRAIGHT",
        "VERTICAL"
    ]:

        edge_color = "#16A34A"


    # ===================================
    # RIGHT BRANCH
    # ===================================

    elif routing_type in [
        "RIGHT_BRANCH",
        "DOWN"
    ]:

        edge_color = "#16A34A"


    # ===================================
    # ERROR BRANCH
    # ===================================

    elif routing_type in [
        "ERROR_BRANCH",
        "RIGHT_EXTERNAL"
    ]:

        edge_color = "#DC2626"


    # ===================================
    # OUTER LOOP
    # ===================================

    elif routing_type in [
        "OUTER_RIGHT_LOOP",
        "OUTER_LOOP",
        "LOCAL_RETRY_LOOP"
    ]:

        edge_color = "#2563EB"

        animated = True


    elif routing_type == "RESTART_FLOW":

        edge_color = "#0F766E"

        animated = False

    elif routing_type == "SUCCESS_REJOIN":

        edge_color = "#16A34A"

        animated = False

    elif routing_type == "REVIEW_BRANCH":

        edge_color = "#7C3AED"

        animated = False

    elif routing_type == "BUSINESS_BRANCH":

        edge_color = "#7C3AED"

        animated = False

    elif routing_type == "TERMINAL_BRANCH":

        edge_color = "#7C3AED"

        animated = False


    # ===================================
    # BOTTOM LOOP
    # ===================================

    elif routing_type in [
        "BOTTOM_RETURN_LOOP",
        "BOTTOM_LOOP"
    ]:

        edge_color = "#7C3AED"

        animated = True


    # ===================================
    # CONNECTOR FLOW
    # ===================================

    elif routing_type == "CONNECTOR_FLOW":

        edge_color = "#EA580C"

        animated = True

    elif routing_type == "CONNECTOR_STUB":

        edge_color = "#111827"

        animated = False


    elif routing_type == "MERGE_JOIN":

        edge_color = "#6B7280"


    return {

        "edge_color": edge_color,

        "animated": animated
    }


def get_source_handle(routing_type):

    if routing_type == "CONNECTOR_STUB":

        return "right"

    if routing_type == "REVIEW_BRANCH":

        return "restart"

    if routing_type == "SUCCESS_REJOIN":

        return "restart"

    if routing_type == "BUSINESS_BRANCH":

        return "error"

    if routing_type == "TERMINAL_BRANCH":

        return "error"

    if routing_type in [
        "RIGHT_EXTERNAL",
        "MERGE_JOIN"
    ]:

        return "error"

    if routing_type in [
        "OUTER_LOOP",
        "LOCAL_RETRY_LOOP",
        "BOTTOM_LOOP",
        "LEFT_RETURN"
    ]:

        return "error"

    if routing_type == "RESTART_FLOW":

        return "restart"

    return "success"


def get_target_handle(routing_type):

    if routing_type == "CONNECTOR_STUB":

        return "left"

    if routing_type == "REVIEW_BRANCH":

        return "loopback"

    if routing_type == "SUCCESS_REJOIN":

        return "return"

    if routing_type == "BUSINESS_BRANCH":

        return "loopback"

    if routing_type == "TERMINAL_BRANCH":

        return "loopback"

    if routing_type == "RIGHT_EXTERNAL":

        return "loopback"

    if routing_type in [
        "OUTER_LOOP",
        "LOCAL_RETRY_LOOP"
    ]:

        return "return"

    if routing_type in [
        "BOTTOM_LOOP",
        "LEFT_RETURN",
        "RESTART_FLOW"
    ]:

        return "loopback"

    return "target"
    

# ===================================
# BUILD REACTFLOW EDGES
# ===================================

def build_render_edges(
    graph,
    edges
):

    merge_outgoing = {}

    merge_incoming = []

    normal_edges = []

    for edge in edges:

        target_node = graph.get_node(
            edge.target
        )

        source_node = graph.get_node(
            edge.source
        )

        if target_node and target_node.type == "MERGE":

            merge_incoming.append(edge)

            continue

        if source_node and source_node.type == "MERGE":

            merge_outgoing[edge.source] = edge

            continue

        normal_edges.append(edge)

    collapsed_edges = []

    for edge in merge_incoming:

        merge_edge = merge_outgoing.get(
            edge.target
        )

        if not merge_edge:

            continue

        collapsed_edges.append(
            WorkflowEdge(

                source=edge.source,

                target=merge_edge.target,

                edge_type=merge_edge.edge_type,

                condition=(
                    edge.condition
                    or edge.edge_label
                    or merge_edge.condition
                ),

                routing_role=merge_edge.routing_role,

                edge_label=(
                    edge.edge_label
                    or edge.condition
                    or merge_edge.edge_label
                ),

                metadata={
                    **edge.metadata,
                    **merge_edge.metadata,
                    "collapsed_merge": True,
                    "virtual_merge_id": edge.target
                }
            )
        )

    return normal_edges + collapsed_edges


def is_backward_render_edge(
    edge,
    node_positions
):

    source_position = node_positions.get(
        edge.source
    )

    target_position = node_positions.get(
        edge.target
    )

    if not source_position or not target_position:

        return False

    return target_position["y"] < source_position["y"]


def is_response_restart_render_edge(
    graph,
    edge,
    node_positions
):

    source_node = graph.get_node(
        edge.source
    )

    target_node = graph.get_node(
        edge.target
    )

    if not source_node or not target_node:

        return False

    if source_node.type != "RESPONSE":

        return False

    if (
        edge.edge_type != "LOOPBACK"
        and edge.routing_role != "LOOPBACK"
    ):

        return False

    if target_node.type in [
        "MERGE",
        "END"
    ]:

        return False

    return is_backward_render_edge(
        edge,
        node_positions
    )


def has_local_continuation_from_source(
    graph,
    edge
):

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        if outgoing_edge is edge:

            continue

        if outgoing_edge.routing_role == "LOCAL_CONTINUATION":

            return True

    return False


def restart_flow_side(
    graph,
    edge,
    node_positions
):

    if not is_response_restart_render_edge(
        graph,
        edge,
        node_positions
    ):

        return "left"

    source_position = node_positions.get(
        edge.source,
        {}
    )

    target_position = node_positions.get(
        edge.target,
        {}
    )

    vertical_distance = abs(
        source_position.get(
            "y",
            0
        )
        - target_position.get(
            "y",
            0
        )
    )

    start_position = next(
        (
            node_positions.get(
                node_id,
                {}
            )
            for node_id, node in graph.nodes.items()
            if node.type == "START"
        ),
        {}
    )

    spine_x = start_position.get(
        "x",
        source_position.get(
            "x",
            0
        )
    )

    source_x = source_position.get(
        "x",
        0
    )

    target_x = target_position.get(
        "x",
        0
    )

    same_side_retry = (
        abs(
            source_x - target_x
        ) < 100
        and abs(
            source_x - spine_x
        ) > 120
    )

    left_lane_x = min(
        source_x,
        target_x
    ) - 260

    right_lane_x = max(
        source_x,
        target_x
    ) + 260

    cleaner_side = choose_lower_collision_restart_side(
        graph,
        edge,
        node_positions,
        left_lane_x,
        right_lane_x
    )

    if same_side_retry:

        return (
            cleaner_side
            or (
                "right"
                if source_x > spine_x
                else "left"
            )
        )

    if (
        vertical_distance > 520
        and abs(
            source_x - target_x
        ) < 100
    ):

        return cleaner_side or "left"

    if not has_local_continuation_from_source(
        graph,
        edge
    ):

        return cleaner_side or "left"

    if cleaner_side:

        return cleaner_side

    if source_x > target_x:

        return "right"

    return "left"


def target_top_is_occupied(
    graph,
    edge,
    node_positions,
    render_edges
):

    target_position = node_positions.get(
        edge.target,
        {}
    )

    target_x = target_position.get(
        "x",
        MAIN_X
    )

    target_y = target_position.get(
        "y",
        0
    )

    for incoming_edge in render_edges:

        if incoming_edge is edge:

            continue

        if incoming_edge.target != edge.target:

            continue

        if incoming_edge.edge_type == "LOOPBACK":

            continue

        source_position = node_positions.get(
            incoming_edge.source,
            {}
        )

        incoming_source_x = source_position.get(
            "x",
            target_x
        )

        incoming_source_y = source_position.get(
            "y",
            target_y
        )

        is_top_aligned_incoming = (
            incoming_source_y < target_y
            and abs(
                incoming_source_x - target_x
            ) < 90
        )

        if is_top_aligned_incoming:

            return True

    return False


def target_side_is_competed(
    graph,
    edge,
    node_positions,
    render_edges
):

    source_position = node_positions.get(
        edge.source,
        {}
    )

    target_position = node_positions.get(
        edge.target,
        {}
    )

    source_x = source_position.get(
        "x",
        MAIN_X
    )

    target_x = target_position.get(
        "x",
        MAIN_X
    )

    if abs(
        source_x - target_x
    ) < 90:

        return False

    current_side = (
        "left"
        if source_x < target_x
        else "right"
    )

    for incoming_edge in render_edges:

        if incoming_edge is edge:

            continue

        if incoming_edge.target != edge.target:

            continue

        if incoming_edge.edge_type == "LOOPBACK":

            continue

        incoming_source_position = node_positions.get(
            incoming_edge.source,
            {}
        )

        incoming_source_x = incoming_source_position.get(
            "x",
            target_x
        )

        if abs(
            incoming_source_x - target_x
        ) < 90:

            continue

        incoming_side = (
            "left"
            if incoming_source_x < target_x
            else "right"
        )

        if incoming_side == current_side:

            return True

    return False


def cleaner_side_target_handle(
    graph,
    edge,
    node_positions,
    render_edges
):

    source_position = node_positions.get(
        edge.source,
        {}
    )

    target_position = node_positions.get(
        edge.target,
        {}
    )

    source_x = source_position.get(
        "x",
        MAIN_X
    )

    target_x = target_position.get(
        "x",
        MAIN_X
    )

    if (
        target_side_is_competed(
            graph,
            edge,
            node_positions,
            render_edges
        )
        and not target_top_is_occupied(
            graph,
            edge,
            node_positions,
            render_edges
        )
    ):

        return "target"

    if not target_top_is_occupied(
        graph,
        edge,
        node_positions,
        render_edges
    ):

        return "target"

    if abs(
        source_x - target_x
    ) < 90:

        return "target"

    return (
        "return"
        if source_x > target_x
        else "loopback"
    )


def target_has_local_return_lane(
    graph,
    edge,
    node_positions,
    render_edges
):

    for outgoing_edge in render_edges:

        if outgoing_edge.source != edge.target:

            continue

        if is_local_retry_loop(
            graph,
            outgoing_edge,
            node_positions
        ):

            return True

    return False


def source_has_incoming_rework_lane(
    graph,
    edge,
    node_positions,
    render_edges
):

    source_position = node_positions.get(
        edge.source,
        {}
    )

    source_y = source_position.get(
        "y",
        0
    )

    for incoming_edge in render_edges:

        if incoming_edge.target != edge.source:

            continue

        incoming_source = graph.get_node(
            incoming_edge.source
        )

        if not incoming_source:

            continue

        incoming_source_position = node_positions.get(
            incoming_edge.source,
            {}
        )

        if incoming_source_position.get(
            "y",
            source_y
        ) <= source_y:

            continue

        incoming_config = get_routing_config(
            incoming_edge
        )

        is_rework_routing = incoming_config.get(
            "routing_type"
        ) in [
            "RESTART_FLOW",
            "REVIEW_BRANCH"
        ]

        is_response_loopback_rework = (
            incoming_source.type == "RESPONSE"
            and incoming_edge.edge_type == "LOOPBACK"
            and not is_restart_loop(
                incoming_edge
            )
        )

        if not (
            is_rework_routing
            or is_response_loopback_rework
        ):

            continue

        return True

    return False


def rework_target_handle(
    graph,
    edge,
    node_positions,
    render_edges
):

    if target_has_local_return_lane(
        graph,
        edge,
        node_positions,
        render_edges
    ):

        source_position = node_positions.get(
            edge.source,
            {}
        )

        target_position = node_positions.get(
            edge.target,
            {}
        )

        if abs(
            source_position.get(
                "x",
                MAIN_X
            )
            - target_position.get(
                "x",
                MAIN_X
            )
        ) < 90:

            return "loopback"

        return (
            "return"
            if source_position.get(
                "x",
                MAIN_X
            ) >= target_position.get(
                "x",
                MAIN_X
            )
            else "loopback"
        )

    return cleaner_side_target_handle(
        graph,
        edge,
        node_positions,
        render_edges
    )


def branch_reaches_terminal_end(
    graph,
    start_id
):

    visited = set()

    queue = [
        start_id
    ]

    while queue:

        node_id = queue.pop(0)

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        node = graph.get_node(
            node_id
        )

        if node and node.type == "END":

            return True

        for outgoing_edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if outgoing_edge.edge_type == "LOOPBACK":

                continue

            if is_restart_loop(
                outgoing_edge
            ):

                continue

            queue.append(
                outgoing_edge.target
            )

    return False


def is_side_terminal_outcome_render_edge(
    graph,
    edge,
    node_positions
):

    if edge.routing_role != "ERROR":

        return False

    source_node = graph.get_node(
        edge.source
    )

    target_node = graph.get_node(
        edge.target
    )

    if not source_node or not target_node:

        return False

    if source_node.type != "RESPONSE":

        return False

    if target_node.type in [
        "END",
        "MERGE",
        "MANUAL_ACTIVITY"
    ]:

        return False

    source_position = node_positions.get(
        edge.source,
        {}
    )

    if source_position.get(
        "x",
        MAIN_X
    ) > MAIN_X - 120:

        return False

    return branch_reaches_terminal_end(
        graph,
        edge.target
    )


def build_reactflow_edges(
    graph,
    node_positions,
    edges
):

    reactflow_edges = []

    error_branch_counts = {}

    business_branch_counts = {}

    review_branch_counts = {}

    total_error_branches_by_source = {}

    total_business_branches_by_source = {}

    total_review_branches_by_source = {}

    error_branch_positions_by_source = {}

    business_branch_positions_by_source = {}

    review_branch_positions_by_source = {}

    outer_loop_counts = {}

    outer_loop_totals_by_target = {}

    outer_loop_max_source_y_by_target = {}

    outer_loop_max_source_width_by_target = {}

    outer_loop_right_bus_x_by_target = {}

    outer_loop_totals_by_bus_group = {}

    outer_loop_max_source_y_by_bus_group = {}

    outer_loop_max_source_width_by_bus_group = {}

    outer_loop_right_bus_x_by_bus_group = {}

    outer_loop_bus_lane_index_by_bus_group = {}

    outer_loop_max_right_lane_x_by_target = {}

    outer_loop_max_right_lane_index_by_target = {}

    outer_loop_right_lane_reservations = []

    right_restart_intervals = []

    allocated_right_restart_lanes = []

    global_return_bus_x = calculate_global_return_bus_x(
        graph,
        node_positions
    )

    
    render_edges = build_render_edges(
        graph,
        edges
    )

    render_edges = [
        edge
        for edge in render_edges
        if edge.source in node_positions
        and edge.target in node_positions
    ]

    error_branch_owner_by_node = {}

    for edge in render_edges:

        if (
            edge.routing_role == "ERROR"
            and get_routing_config(edge)["routing_type"] == "RIGHT_EXTERNAL"
        ):

            source_node = graph.get_node(
                edge.source
            )

            if source_node and source_node.type == "RESPONSE":

                error_branch_owner_by_node[edge.target] = edge.source

    def outer_loop_bus_group_key(edge):

        return (
            error_branch_owner_by_node.get(
                edge.source
            )
            or edge.source,
            edge.target,
            "OUTER_LOOP"
        )

    outer_loop_bus_intervals = []

    for edge in render_edges:

        routing = get_routing_config(
            edge
        )

        routing_type = routing["routing_type"]

        if is_response_restart_render_edge(
            graph,
            edge,
            node_positions
        ):

            routing_type = "RESTART_FLOW"

        if (
            edge.edge_type == "CONDITIONAL"
            and is_restart_loop(edge)
            and is_backward_render_edge(
                edge,
                node_positions
            )
        ):

            routing_type = "RESTART_FLOW"

        if routing_type != "RESTART_FLOW":

            continue

        if restart_flow_side(
            graph,
            edge,
            node_positions
        ) != "right":

            continue

        right_restart_intervals.append(
            {
                "edge": edge,
                "interval": edge_vertical_interval(
                    node_positions,
                    edge
                )
            }
        )

    for edge in render_edges:

        routing = get_routing_config(
            edge
        )

        if (
            edge.routing_role == "ERROR"
            and routing["routing_type"] == "RIGHT_EXTERNAL"
        ):

            total_error_branches_by_source[edge.source] = (
                total_error_branches_by_source.get(
                    edge.source,
                    0
                ) + 1
            )

            target_position = node_positions.get(
                edge.target,
                {}
            )

            error_branch_positions_by_source.setdefault(
                edge.source,
                []
            ).append(
                (
                    target_position.get(
                        "x",
                        0
                    ),
                    target_position.get(
                        "y",
                        0
                    )
                )
            )

        if (
            edge.edge_type == "CONDITIONAL"
            and edge.routing_role == "ERROR"
            and is_correction_return_edge(edge)
            and not is_backward_render_edge(
                edge,
                node_positions
            )
        ):

            total_business_branches_by_source[edge.source] = (
                total_business_branches_by_source.get(
                    edge.source,
                    0
                ) + 1
            )

        if (
            edge.routing_role == "ERROR"
            and (
                is_backward_render_edge(
                    edge,
                    node_positions
                )
                or (
                    node_positions.get(
                        edge.target,
                        {}
                    ).get(
                        "x",
                        0
                    )
                    < node_positions.get(
                        edge.source,
                        {}
                    ).get(
                        "x",
                        0
                    )
                )
            )
        ):

            total_review_branches_by_source[edge.source] = (
                total_review_branches_by_source.get(
                    edge.source,
                    0
                ) + 1
            )

            target_position = node_positions.get(
                edge.target,
                {}
            )

            review_branch_positions_by_source.setdefault(
                edge.source,
                []
            ).append(
                (
                    target_position.get(
                        "x",
                        0
                    ),
                    target_position.get(
                        "y",
                        0
                    )
                )
            )

            target_position = node_positions.get(
                edge.target,
                {}
            )

            business_branch_positions_by_source.setdefault(
                edge.source,
                []
            ).append(
                (
                    target_position.get(
                        "x",
                        0
                    ),
                    target_position.get(
                        "y",
                        0
                    )
                )
            )

    error_branch_layout_by_source = {}

    for source, positions in error_branch_positions_by_source.items():

        unique_x = {
            position[0]
            for position in positions
        }

        unique_y = {
            position[1]
            for position in positions
        }

        error_branch_layout_by_source[source] = (
            "horizontal"
            if (
                len(positions) > 1
                and len(unique_x) > 1
                and len(unique_y) == 1
            )
            else "vertical"
        )

    business_branch_layout_by_source = {}

    for source, positions in business_branch_positions_by_source.items():

        unique_x = {
            position[0]
            for position in positions
        }

        unique_y = {
            position[1]
            for position in positions
        }

        business_branch_layout_by_source[source] = (
            "horizontal"
            if (
                len(positions) > 1
                and len(unique_x) > 1
                and len(unique_y) == 1
            )
            else "vertical"
        )

    for edge in render_edges:

        routing = get_routing_config(
            edge
        )

        routing_type = routing["routing_type"]

        if is_response_restart_render_edge(
            graph,
            edge,
            node_positions
        ):

            routing_type = "RESTART_FLOW"

        if (
            routing_type == "OUTER_LOOP"
            and is_local_retry_loop(
                graph,
                edge,
                node_positions
            )
        ):

            routing_type = "LOCAL_RETRY_LOOP"

        if routing_type not in [
            "OUTER_LOOP",
            "BOTTOM_LOOP",
            "LEFT_RETURN"
        ]:

            continue

        source_position = node_positions.get(
            edge.source,
            {}
        )

        bus_group_key = outer_loop_bus_group_key(
            edge
        )

        outer_loop_totals_by_target[edge.target] = (
            outer_loop_totals_by_target.get(
                edge.target,
                0
            ) + 1
        )

        outer_loop_max_source_y_by_target[edge.target] = max(
            outer_loop_max_source_y_by_target.get(
                edge.target,
                source_position.get(
                    "y",
                    0
                )
            ),
            source_position.get(
                "y",
                0
            )
        )

        outer_loop_max_source_width_by_target[edge.target] = max(
            outer_loop_max_source_width_by_target.get(
                edge.target,
                0
            ),
            estimate_node_half_width(
                graph.get_node(
                    edge.source
                )
            ) * 2
        )

        outer_loop_totals_by_bus_group[bus_group_key] = (
            outer_loop_totals_by_bus_group.get(
                bus_group_key,
                0
            ) + 1
        )

        outer_loop_max_source_y_by_bus_group[bus_group_key] = max(
            outer_loop_max_source_y_by_bus_group.get(
                bus_group_key,
                source_position.get(
                    "y",
                    0
                )
            ),
            source_position.get(
                "y",
                0
            )
        )

        outer_loop_max_source_width_by_bus_group[bus_group_key] = max(
            outer_loop_max_source_width_by_bus_group.get(
                bus_group_key,
                0
            ),
            estimate_node_half_width(
                graph.get_node(
                    edge.source
                )
            ) * 2
        )

        target_position = node_positions.get(
            edge.target,
            {}
        )

        source_x = source_position.get(
            "x",
            0
        )

        target_x = target_position.get(
            "x",
            0
        )

        source_y = source_position.get(
            "y",
            0
        )

        target_y = target_position.get(
            "y",
            0
        )

        source_node = graph.get_node(
            edge.source
        )

        target_node = graph.get_node(
            edge.target
        )

        source_handle_x = (
            source_x
            + estimate_node_half_width(
                source_node
            )
        )

        target_handle_x = (
            target_x
            + estimate_node_half_width(
                target_node
            )
        )

        is_error_retry_return = (
            target_y < source_y
            and (
                edge.metadata.get(
                    "render_expanded_error"
                )
                or (
                    source_node
                    and source_node.type == "SYSTEM_ACTIVITY"
                )
                or source_x > target_x + 60
            )
        )

        if is_error_retry_return:

            outer_loop_right_bus_x_by_target[edge.target] = max(
                outer_loop_right_bus_x_by_target.get(
                    edge.target,
                    0
                ),
                max(
                    source_handle_x,
                    target_handle_x
                ) + 46
            )

            outer_loop_right_bus_x_by_bus_group[bus_group_key] = max(
                outer_loop_right_bus_x_by_bus_group.get(
                    bus_group_key,
                    0
                ),
                max(
                    source_handle_x,
                    target_handle_x
                ) + 46
            )

            outer_loop_bus_intervals.append(
                {
                    "bus_group_key": bus_group_key,
                    "target": edge.target,
                    "side": "right",
                    "interval": (
                        min(
                            source_y,
                            target_y
                        ),
                        max(
                            source_y,
                            target_y
                        )
                    )
                }
            )

    grouped_outer_loop_bus_intervals = {}

    for interval in outer_loop_bus_intervals:

        group_key = (
            interval["side"],
            interval["bus_group_key"]
        )

        existing_interval = grouped_outer_loop_bus_intervals.get(
            group_key
        )

        if existing_interval:

            existing_interval["interval"] = (
                min(
                    existing_interval["interval"][0],
                    interval["interval"][0]
                ),
                max(
                    existing_interval["interval"][1],
                    interval["interval"][1]
                )
            )

        else:

            grouped_outer_loop_bus_intervals[group_key] = {
                **interval
            }

    allocated_outer_loop_bus_lanes = {}

    for interval in sorted(
        grouped_outer_loop_bus_intervals.values(),
        key=lambda item: (
            item["side"],
            item["interval"][0],
            item["interval"][1],
            item["bus_group_key"],
            item["target"]
        )
    ):

        bus_group_key = interval["bus_group_key"]

        side = interval["side"]

        if bus_group_key in outer_loop_bus_lane_index_by_bus_group:

            continue

        lanes = allocated_outer_loop_bus_lanes.setdefault(
            side,
            []
        )

        for lane_index, lane_intervals in enumerate(
            lanes,
            start=1
        ):

            if any(
                intervals_overlap(
                    interval["interval"],
                    existing_interval,
                    padding=24
                )
                for existing_interval in lane_intervals
            ):

                continue

            outer_loop_bus_lane_index_by_bus_group[bus_group_key] = lane_index

            lane_intervals.append(
                interval["interval"]
            )

            break

        else:

            lanes.append(
                [
                    interval["interval"]
                ]
            )

            outer_loop_bus_lane_index_by_bus_group[bus_group_key] = len(
                lanes
            )

    for interval in grouped_outer_loop_bus_intervals.values():

        if interval["side"] != "right":

            continue

        bus_group_key = interval["bus_group_key"]

        target_id = interval["target"]

        target_clear_lane_x = (
            outer_loop_right_bus_x_by_target.get(
                target_id,
                0
            )
            + 132
            if outer_loop_right_bus_x_by_target.get(
                target_id
            )
            else 0
        )

        base_lane_x = max(
            outer_loop_right_bus_x_by_bus_group.get(
                bus_group_key,
                0
            ),
            target_clear_lane_x
        )

        if not base_lane_x:

            continue

        lane_index = outer_loop_bus_lane_index_by_bus_group.get(
            bus_group_key,
            1
        )

        lane_x = base_lane_x + (
            96 * (
                lane_index - 1
            )
        )

        outer_loop_max_right_lane_x_by_target[target_id] = max(
            outer_loop_max_right_lane_x_by_target.get(
                target_id,
                0
            ),
            lane_x
        )

        outer_loop_right_lane_reservations.append(
            {
                "interval": interval["interval"],
                "lane_x": lane_x,
                "bus_group_key": bus_group_key,
                "target": target_id
            }
        )

        outer_loop_max_right_lane_index_by_target[target_id] = max(
            outer_loop_max_right_lane_index_by_target.get(
                target_id,
                1
            ),
            lane_index
        )

    for index, edge in enumerate(render_edges):
            
        # ===================================
        # ROUTING METADATA
        # =
            routing = get_routing_config(edge)

            routing_type = routing["routing_type"]

            lane_offset = routing["lane_offset"]

            if edge.metadata.get(
                "routing_type_override"
            ):

                routing_type = edge.metadata[
                    "routing_type_override"
                ]

                lane_offset = 0

            source_position = node_positions.get(
                edge.source,
                {}
            )

            target_position = node_positions.get(
                edge.target,
                {}
            )

            bus_group_key = outer_loop_bus_group_key(
                edge
            )

            if (
                routing_type == "OUTER_LOOP"
                and is_local_retry_loop(
                    graph,
                    edge,
                    node_positions
                )
            ):

                routing_type = "LOCAL_RETRY_LOOP"

                lane_offset = 0

            if is_terminal_end_edge(
                graph,
                edge
            ):

                routing_type = "DOWN"

                lane_offset = 0

            if is_response_terminal_option_edge(
                graph,
                edge
            ):

                routing_type = "TERMINAL_BRANCH"

                lane_offset = 1

            if (
                edge.metadata.get(
                    "visual_terminal_edge"
                )
                and target_position.get(
                    "x",
                    0
                ) > source_position.get(
                    "x",
                    0
                ) + 80
            ):

                routing_type = "TERMINAL_BRANCH"

                lane_offset = 1

            if (
                edge.edge_type == "CONDITIONAL"
                and is_restart_loop(edge)
                and is_backward_render_edge(
                    edge,
                    node_positions
                )
            ):

                routing_type = "RESTART_FLOW"

                lane_offset = 0

            if is_response_restart_render_edge(
                graph,
                edge,
                node_positions
            ):

                routing_type = "RESTART_FLOW"

                lane_offset = 0

            if (
                edge.edge_type == "CONDITIONAL"
                and edge.routing_role == "SUCCESS"
                and abs(
                    source_position.get(
                        "x",
                        0
                    )
                    - target_position.get(
                        "x",
                        0
                    )
                ) > 80
            ):

                routing_type = "SUCCESS_REJOIN"

                lane_offset = 0

            if (
                edge.edge_type == "CONDITIONAL"
                and graph.get_node(edge.source)
                and graph.get_node(edge.source).type == "RESPONSE"
                and graph.get_node(edge.target)
                and graph.get_node(edge.target).type in {
                    "MANUAL_ACTIVITY",
                    "SYSTEM_ACTIVITY",
                    "SYSTEM_CHECK"
                }
                and is_rework_outcome_label(
                    edge
                )
                and abs(
                    source_position.get(
                        "x",
                        0
                    )
                    - target_position.get(
                        "x",
                        0
                    )
                ) > 80
            ):

                routing_type = "REVIEW_BRANCH"

                lane_offset = 0

            if (
                edge.edge_type == "CONDITIONAL"
                and edge.routing_role == "ERROR"
                and is_correction_return_edge(edge)
                and is_backward_render_edge(
                    edge,
                    node_positions
                )
            ):

                routing_type = "REVIEW_BRANCH"

                lane_offset = 0

            if (
                edge.edge_type == "CONDITIONAL"
                and edge.routing_role == "ERROR"
                and (
                    (
                        is_correction_return_edge(edge)
                        and graph.get_node(edge.target)
                        and graph.get_node(edge.target).type == "MANUAL_ACTIVITY"
                    )
                    or is_side_terminal_outcome_render_edge(
                        graph,
                        edge,
                        node_positions
                    )
                )
                and not is_backward_render_edge(
                    edge,
                    node_positions
                )
            ):

                if is_side_terminal_outcome_render_edge(
                    graph,
                    edge,
                    node_positions
                ):

                    routing_type = "TERMINAL_BRANCH"

                    lane_offset = 1

                else:

                    routing_type = "BUSINESS_BRANCH"

                    business_branch_counts[edge.source] = (
                        business_branch_counts.get(
                            edge.source,
                            0
                        ) + 1
                    )

                    lane_offset = business_branch_counts[
                        edge.source
                    ]

            if (
                edge.routing_role == "ERROR"
                and routing_type == "RIGHT_EXTERNAL"
                and target_position.get(
                    "x",
                    0
                ) < source_position.get(
                    "x",
                    0
                )
            ):

                routing_type = "REVIEW_BRANCH"

                lane_offset = 0

        # ERROR BRANCH SEPARATION

            if (
                edge.routing_role == "ERROR"
                and routing_type == "RIGHT_EXTERNAL"
            ):

                error_branch_counts[edge.source] = (
                    error_branch_counts.get(
                        edge.source,
                        0
                    ) + 1
                )

                lane_offset = error_branch_counts[
                    edge.source
                ]

            if routing_type == "REVIEW_BRANCH":

                review_branch_counts[edge.source] = (
                    review_branch_counts.get(
                        edge.source,
                        0
                    ) + 1
                )

                lane_offset = review_branch_counts[
                    edge.source
                ]

            if routing_type in [
                "OUTER_LOOP",
                "BOTTOM_LOOP",
                "LEFT_RETURN"
            ]:

                outer_loop_counts[edge.target] = (
                    outer_loop_counts.get(
                        edge.target,
                        0
                    ) + 1
                )

                lane_offset = outer_loop_counts[
                    edge.target
                ]

            if edge.metadata.get(
                "routing_type_override"
            ):

                routing_type = edge.metadata[
                    "routing_type_override"
                ]

                lane_offset = 0


        # ===================================
        # STYLE
        # ===================================

            style_config = get_edge_style(
            routing_type
        )


            edge_color = style_config["edge_color"]

            animated = style_config["animated"]

            source_handle = get_source_handle(
            routing_type
        )

            target_handle = get_target_handle(
            routing_type
        )

            if routing_type == "BUSINESS_BRANCH":

                if target_position.get(
                    "x",
                    0
                ) < source_position.get(
                    "x",
                    0
                ):

                    source_handle = "restart"
                    target_handle = "return"

                else:

                    source_handle = "error"
                    target_handle = "loopback"

            restart_side = restart_flow_side(
                graph,
                edge,
                node_positions
            )

            local_retry_side = "right"

            if routing_type == "LOCAL_RETRY_LOOP":

                local_retry_interval = edge_vertical_interval(
                    node_positions,
                    edge
                )

                source_x = source_position.get(
                    "x",
                    MAIN_X
                )

                target_x = target_position.get(
                    "x",
                    MAIN_X
                )

                is_left_owned_retry = (
                    source_x < MAIN_X
                    and target_x < MAIN_X
                )

                is_right_owned_retry = (
                    source_x > MAIN_X
                    and target_x > MAIN_X
                )

                local_retry_span = abs(
                    source_position.get(
                        "y",
                        0
                    )
                    - target_position.get(
                        "y",
                        0
                    )
                )

                local_retry_lane_distance = (
                    56
                    if local_retry_span <= 420
                    else 260
                )

                right_local_retry_lane_distance = (
                    56
                    if local_retry_span <= 420
                    else 420
                )

                cleaner_local_retry_side = choose_lower_collision_restart_side(
                    graph,
                    edge,
                    node_positions,
                    min(
                        source_x,
                        target_x
                    ) - local_retry_lane_distance,
                    max(
                        source_x,
                        target_x
                    ) + right_local_retry_lane_distance
                )

                if is_left_owned_retry:

                    local_retry_side = (
                        cleaner_local_retry_side
                        or "right"
                    )

                elif is_right_owned_retry:

                    local_retry_side = (
                        cleaner_local_retry_side
                        or "left"
                    )

                elif cleaner_local_retry_side:

                    local_retry_side = cleaner_local_retry_side

                elif any(
                    intervals_overlap(
                        local_retry_interval,
                        restart_interval["interval"],
                        padding=18
                    )
                    for restart_interval in right_restart_intervals
                ):

                    local_retry_side = "left"

                else:

                    local_retry_side = "right"

            restart_lane_index = 1

            if (
                routing_type == "RESTART_FLOW"
                and restart_side == "right"
            ):

                restart_interval = edge_vertical_interval(
                    node_positions,
                    edge
                )

                for lane_index, lane_intervals in enumerate(
                    allocated_right_restart_lanes,
                    start=1
                ):

                    if any(
                        intervals_overlap(
                            restart_interval,
                            existing_interval,
                            padding=18
                        )
                        for existing_interval in lane_intervals
                    ):

                        continue

                    restart_lane_index = lane_index

                    lane_intervals.append(
                        restart_interval
                    )

                    break

                else:

                    allocated_right_restart_lanes.append(
                        [
                            restart_interval
                        ]
                    )

                    restart_lane_index = len(
                        allocated_right_restart_lanes
                    )

            if (
                routing_type == "RESTART_FLOW"
                and restart_side == "right"
            ):

                source_handle = "error"

                target_handle = "return"

            if (
                routing_type == "RESTART_FLOW"
                and graph.get_node(edge.source)
                and graph.get_node(edge.source).type == "RESPONSE"
                and graph.get_node(edge.target)
                and graph.get_node(edge.target).type == "MANUAL_ACTIVITY"
                and target_position.get(
                    "y",
                    0
                ) < source_position.get(
                    "y",
                    0
                )
                and not is_restart_loop(edge)
            ):

                target_handle = rework_target_handle(
                    graph,
                    edge,
                    node_positions,
                    render_edges
                )

            if (
                routing_type == "RESTART_FLOW"
                and target_handle == "target"
                and target_top_is_occupied(
                    graph,
                    edge,
                    node_positions,
                    render_edges
                )
            ):

                target_handle = (
                    "return"
                    if source_position.get(
                        "x",
                        MAIN_X
                    ) > target_position.get(
                        "x",
                        MAIN_X
                    )
                    else "loopback"
                )

            if (
                routing_type == "LOCAL_RETRY_LOOP"
                and local_retry_side == "left"
            ):

                source_handle = "restart"

                target_handle = "loopback"

            if (
                routing_type == "LOCAL_RETRY_LOOP"
                and source_has_incoming_rework_lane(
                    graph,
                    edge,
                    node_positions,
                    render_edges
                )
            ):

                source_handle = "top_retry"

                target_handle = "target"

            if routing_type == "SUCCESS_REJOIN":

                source_node = graph.get_node(
                    edge.source
                )

                is_response_non_pass_through_branch = (
                    source_node
                    and source_node.type == "RESPONSE"
                    and normalize_condition_label(
                        edge
                    ) not in VISUAL_PASS_THROUGH_RESPONSE_LABELS
                )

                if (
                    target_position.get(
                        "y",
                        0
                    ) > source_position.get(
                        "y",
                        0
                    )
                    and not has_local_continuation_from_source(
                        graph,
                        edge
                    )
                ):

                    source_handle = "success"

                    target_handle = cleaner_side_target_handle(
                        graph,
                        edge,
                        node_positions,
                        render_edges
                    )

                    if (
                        is_response_non_pass_through_branch
                        and abs(
                            target_position.get(
                                "x",
                                0
                            )
                            - source_position.get(
                                "x",
                                0
                            )
                        ) > 80
                    ):

                        source_handle = "restart"

                        target_handle = "target"

                elif target_position.get(
                    "y",
                    0
                ) > source_position.get(
                    "y",
                    0
                ):

                    source_handle = (
                        "error"
                        if target_position.get(
                            "x",
                            0
                        ) > source_position.get(
                            "x",
                            0
                        )
                        else "restart"
                    )

                    target_handle = "target"

                elif target_position.get(
                    "x",
                    0
                ) > source_position.get(
                    "x",
                    0
                ) + 80:

                    source_handle = "error"

                    target_handle = "loopback"

                elif target_position.get(
                    "x",
                    0
                ) > source_position.get(
                    "x",
                    0
                ):

                    source_handle = "error"

                    target_handle = "loopback"

                else:

                    source_handle = "restart"

                    target_handle = "return"

            if (
                routing_type in [
                    "BUSINESS_BRANCH",
                    "SUCCESS_REJOIN",
                    "REVIEW_BRANCH"
                ]
                and target_position.get(
                    "y",
                    0
                ) > source_position.get(
                    "y",
                    0
                )
                and target_handle in [
                    "loopback",
                    "return"
                ]
                and target_side_is_competed(
                    graph,
                    edge,
                    node_positions,
                    render_edges
                )
                and not target_top_is_occupied(
                    graph,
                    edge,
                    node_positions,
                    render_edges
                )
            ):

                target_handle = "target"

            if (
                routing_type == "RESTART_FLOW"
                and graph.get_node(edge.source)
                and graph.get_node(edge.source).type == "RESPONSE"
                and graph.get_node(edge.target)
                and graph.get_node(edge.target).type in {
                    "MANUAL_ACTIVITY",
                    "SYSTEM_ACTIVITY",
                    "SYSTEM_CHECK"
                }
                and target_position.get(
                    "y",
                    0
                ) < source_position.get(
                    "y",
                    0
                )
                and abs(
                    target_position.get(
                        "x",
                        0
                    )
                    - source_position.get(
                        "x",
                        0
                    )
                ) > 80
                and not is_restart_loop(
                    edge
                )
            ):

                target_handle = "bottom"

            if (
                routing_type == "REVIEW_BRANCH"
                and target_position.get(
                    "x",
                    0
                ) < source_position.get(
                    "x",
                    0
                )
            ):

                target_handle = "return"

            if (
                routing_type == "TERMINAL_BRANCH"
                and graph.get_node(edge.source)
                and graph.get_node(edge.source).type == "RESPONSE"
            ):

                source_handle = "success"

                target_handle = "target"

            if edge.metadata.get(
                "connector_segment"
            ) == "to_reference":

                source_handle = "error"

                target_handle = "left"

            if edge.metadata.get(
                "connector_segment"
            ) == "from_reference":

                source_handle = "right"

                target_position = node_positions.get(
                    edge.target,
                    {}
                )

                source_position = node_positions.get(
                    edge.source,
                    {}
                )

                target_handle = (
                    "loopback"
                    if source_position.get(
                        "x",
                        0
                    ) < target_position.get(
                        "x",
                        0
                    )
                    else "return"
                )

        # ===================================
        # BUILD EDGE
        # ===================================

            edge_label = infer_response_option_label(
                graph,
                edge
            )

            reactflow_edge = {

            "id": f"EDGE_{index}",

            "source": edge.source,

            "target": edge.target,

            "label": edge_label,

            "type": "semantic",

            "animated": animated,
             "sourceHandle": source_handle,
             
             "targetHandle": target_handle,


            # ===================================
            # VISUAL STYLE
            # ===================================

            "style": {

                "stroke": edge_color,

                "strokeWidth": 2
            },


            "labelStyle": {

                "fill": edge_color,

                "fontWeight": "bold"
            },


            # ===================================
            # ROUTING METADATA
            # ===================================

            "data": {

                "routing_type": routing_type,

                "lane_offset": lane_offset,

                "routing_role": edge.routing_role,

                "restart_side": restart_side,

                "restart_lane_index": restart_lane_index,

                "local_retry_side": local_retry_side,

                "local_retry_anchor": (
                    "top"
                    if (
                        routing_type == "LOCAL_RETRY_LOOP"
                        and source_handle == "top_retry"
                    )
                    else "side"
                ),

                "edge_type": edge.edge_type,

                "source_type": graph.get_node(
                    edge.source
                ).type if graph.get_node(edge.source) else None,

                "target_type": graph.get_node(
                    edge.target
                ).type if graph.get_node(edge.target) else None,

                "source_width": estimate_node_half_width(
                    graph.get_node(
                        edge.source
                    )
                ) * 2,

                "target_width": estimate_node_half_width(
                    graph.get_node(
                        edge.target
                    )
                ) * 2,

                "global_return_bus_x": global_return_bus_x,

                "source_error_branch_count": total_error_branches_by_source.get(
                    edge.source,
                    0
                ),

                "source_error_branch_layout": error_branch_layout_by_source.get(
                    edge.source,
                    "single"
                ),

                "source_error_branch_max_y": max(
                    [
                        position[1]
                        for position in error_branch_positions_by_source.get(
                            edge.source,
                            []
                        )
                    ]
                    or [
                        None
                    ]
                ),

                "source_business_branch_count": total_business_branches_by_source.get(
                    edge.source,
                    0
                ),

                "source_business_branch_layout": business_branch_layout_by_source.get(
                    edge.source,
                    "single"
                ),

                "source_business_branch_max_y": max(
                    [
                        position[1]
                        for position in business_branch_positions_by_source.get(
                            edge.source,
                            []
                        )
                    ]
                    or [
                        None
                    ]
                ),

                "source_review_branch_count": total_review_branches_by_source.get(
                    edge.source,
                    0
                ),

                "source_review_branch_max_y": max(
                    [
                        position[1]
                        for position in review_branch_positions_by_source.get(
                            edge.source,
                            []
                        )
                    ]
                    or [
                        None
                    ]
                ),

                "restart_left_occupied_right_x": restart_left_occupied_right_x(
                    graph,
                    node_positions,
                    edge
                ),

                "restart_left_occupied_left_x": restart_left_occupied_left_x(
                    graph,
                    node_positions,
                    edge
                ),

                "restart_right_occupied_right_x": max(
                    [
                        value
                        for value in [
                            restart_right_occupied_right_x(
                                graph,
                                node_positions,
                                edge
                            ),
                            (
                                outer_loop_max_right_lane_x_by_target.get(
                                    edge.target
                                )
                                if outer_loop_max_right_lane_x_by_target.get(
                                    edge.target
                                )
                                is not None
                                else None
                            )
                        ]
                        if value is not None
                    ]
                    or [
                        None
                    ]
                ),

                "restart_right_reserved_x": max(
                    [
                        value
                        for value in [
                            (
                                (
                                    outer_loop_max_right_lane_x_by_target.get(
                                        edge.target
                                    )
                                    + (
                                        96
                                        * (
                                            outer_loop_max_right_lane_index_by_target.get(
                                                edge.target,
                                                1
                                            )
                                            - 1
                                        )
                                    )
                                )
                                if outer_loop_max_right_lane_x_by_target.get(
                                    edge.target
                                )
                                is not None
                                else None
                            ),
                            *[
                                reservation["lane_x"] + 96
                                for reservation in outer_loop_right_lane_reservations
                                if intervals_overlap(
                                    edge_vertical_interval(
                                        node_positions,
                                        edge
                                    ),
                                    reservation["interval"],
                                    padding=RESTART_OUTER_BUS_RESERVATION_PADDING
                                )
                            ]
                        ]
                        if value is not None
                    ]
                    or [
                        None
                    ]
                ),

                "target_outer_loop_count": outer_loop_totals_by_target.get(
                    edge.target,
                    0
                )
                if routing_type != "OUTER_LOOP"
                else outer_loop_totals_by_bus_group.get(
                    bus_group_key,
                    0
                ),

                "target_outer_loop_max_source_y": outer_loop_max_source_y_by_target.get(
                    edge.target
                )
                if routing_type != "OUTER_LOOP"
                else outer_loop_max_source_y_by_bus_group.get(
                    bus_group_key
                ),

                "target_outer_loop_max_source_width": outer_loop_max_source_width_by_target.get(
                    edge.target
                )
                if routing_type != "OUTER_LOOP"
                else outer_loop_max_source_width_by_bus_group.get(
                    bus_group_key
                ),

                "outer_loop_bus_group": "|".join(
                    str(
                        value
                    )
                    for value in bus_group_key
                ),

                "outer_loop_bus_lane_index": outer_loop_bus_lane_index_by_bus_group.get(
                    bus_group_key,
                    1
                ),

                "collapsed_merge": edge.metadata.get(
                    "collapsed_merge",
                    False
                ),

                "render_expanded_error": edge.metadata.get(
                    "render_expanded_error",
                    False
                ),

                "virtual_merge_id": edge.metadata.get(
                    "virtual_merge_id"
                ),

                "connector_segment": edge.metadata.get(
                    "connector_segment"
                ),

                "connector_label": edge.metadata.get(
                    "connector_label"
                ),

                "semantic_source": edge.metadata.get(
                    "semantic_source"
                ),

                "semantic_target": edge.metadata.get(
                    "semantic_target"
                ),

                "visual_terminal_edge": edge.metadata.get(
                    "visual_terminal_edge",
                    False
                )
            }
        }


            reactflow_edges.append(
            reactflow_edge
        )


    return reactflow_edges


# ===================================
# BUILD REACTFLOW GRAPH
# ===================================

def build_reactflow_graph(

    graph,

    node_positions,

    semantic_groups
):

    render_nodes, render_edges, render_positions = build_render_model(
        graph,
        node_positions
    )

    return {

        "nodes": build_reactflow_nodes(

            render_nodes,

            render_positions,

            render_edges
        ),

        "edges": build_reactflow_edges(
            graph,
            render_positions,
            render_edges
        ),

        "semantic_groups": semantic_groups
    }


# ===================================
# PRINT REACTFLOW REPORT
# ===================================

def print_reactflow_report(

    reactflow_graph
):

    print(
        "\n===== REACTFLOW GRAPH =====\n"
    )


    print(

        "Total Nodes:",

        len(
            reactflow_graph["nodes"]
        )
    )


    print(

        "Total Edges:",

        len(
            reactflow_graph["edges"]
        )
    )
