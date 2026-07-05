from collections import deque


MAIN_X = 700
HORIZONTAL_GAP = 340
VERTICAL_GAP = 250
MIN_VERTICAL_GAP = 190
NODE_HEIGHT_UNIT = 28
ERROR_BRANCH_START_OFFSET = 90
ERROR_BRANCH_VERTICAL_GAP = 170
POST_ERROR_MAIN_GAP = 105
TERMINAL_BRANCH_BASE_GAP = 105
TERMINAL_BRANCH_LABEL_LINE_GAP = 26
TERMINAL_BRANCH_MAX_GAP = 185
SIDE_BRANCH_TAIL_GAP = 105
MAX_SIDE_BRANCH_DEPTH = 12
RETURN_BUS_GAP = 260
GLOBAL_RETURN_BUS_X = 2060
ERROR_COLUMN_X = 1120
LOCAL_RETRY_CORRIDOR_GAP = 420
LOCAL_RETRY_CORRIDOR_CLEARANCE = 340
SIDE_COLUMN_TOLERANCE = 24
REVIEW_BRANCH_X = 360
REVIEW_BRANCH_VERTICAL_GAP = 230
SIDE_FALLBACK_SCORE_MARGIN = 2
SIDE_TERMINAL_OUTCOME_X = (
    REVIEW_BRANCH_X
    + (
        (MAIN_X - REVIEW_BRANCH_X)
        * 0.56
    )
)
MIN_LAYOUT_ITERATIONS = 50
MAX_LAYOUT_ITERATION_FACTOR = 10

ERROR_CONDITIONS = [
    "INVALID",
    "INCORRECT",
    "NOT",
    "NO",
    "FALSE",
    "FAIL",
    "ERROR",
    "REJECT",
    "MISMATCH",
    "BLOCK"
]

SUCCESS_CONDITIONS = [
    "VALID",
    "CORRECT",
    "YES",
    "TRUE",
    "DONE",
    "PASS",
    "SUCCESS",
    "COMPLY",
    "APPROVED",
    "MATCH"
]


REVIEW_BRANCH_KEYWORDS = [
    "REJECT",
    "REVIEW",
    "CORRECTION",
    "CORRECT",
    "REWORK",
    "SUPERVISOR",
    "QA",
    "APPROVAL",
    "NOT APPROVED",
    "DEVIATION"
]


def normalize_edge_label(edge):

    return (
        edge.condition
        or edge.edge_label
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )


def terminal_outcome_vertical_gap(edge):

    label = normalize_edge_label(
        edge
    )

    if not label:

        return ERROR_BRANCH_START_OFFSET

    label_line_count = max(
        1,
        (
            len(label)
            + 17
        ) // 18
    )

    return min(
        TERMINAL_BRANCH_MAX_GAP,
        max(
            ERROR_BRANCH_START_OFFSET,
            TERMINAL_BRANCH_BASE_GAP
            + (
                label_line_count
                * TERMINAL_BRANCH_LABEL_LINE_GAP
            )
        )
    )


def is_retry_error_loopback_edge(edge):

    if not (
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
    ):

        return False

    label = normalize_edge_label(
        edge
    )

    if label in [
        "YES",
        "NO",
        "VALID",
        "PASS",
        "APPROVED",
        "COMPLETE",
        "FINISH"
    ]:

        return False

    if any(
        keyword in label
        for keyword in [
            "WITHIN",
            "NEXT",
            "CONTINUE",
            "MORE MATERIAL",
            "CORRECTION"
        ]
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
        "SHORT",
        "EXCESS"
    ]

    return any(
        keyword in label
        for keyword in retry_keywords
    )


def is_restart_or_return_label(edge):

    label = normalize_edge_label(
        edge
    )

    if not label:

        return False

    restart_keywords = [
        "YES",
        "NEXT",
        "CONTINUE",
        "RETRY",
        "REPEAT",
        "RETURN",
        "RESCAN",
        "RE-ENTER",
        "REENTER",
        "REWEIGH",
        "REWEIGHING",
        "CORRECTION",
        "CORRECT",
        "APPROVE REWEIGHING",
        "APPROVES REWEIGHING"
    ]

    return any(
        keyword in label
        for keyword in restart_keywords
    )


def get_routing_role(edge):

    if edge.routing_role:

        return edge.routing_role

    if edge.edge_type == "LOOPBACK":

        return "LOOPBACK"

    if edge.edge_type == "SEQUENCE":

        return "MAIN_FLOW"

    if edge.edge_type == "CONDITIONAL":

        condition = (
            edge.condition
            or edge.edge_label
            or ""
        ).upper()

        for keyword in ERROR_CONDITIONS:

            if keyword in condition:

                return "ERROR"

        for keyword in SUCCESS_CONDITIONS:

            if keyword in condition:

                return "SUCCESS"

    return "MAIN_FLOW"


def is_loopback_edge(edge):

    routing_role = get_routing_role(
        edge
    )

    return (
        routing_role == "LOOPBACK"
        or edge.edge_type == "LOOPBACK"
    )


def is_spine_node(node):

    return node.type in [
        "RESPONSE",
        "DECISION"
    ]


def lane_x(lane_index):

    return MAIN_X + (
        lane_index * HORIZONTAL_GAP
    )


def edge_priority(edge):

    routing_role = get_routing_role(
        edge
    )

    if routing_role == "MAIN_FLOW":

        return 0

    if routing_role == "SUCCESS":

        return 1

    if routing_role == "ERROR":

        return 2

    if routing_role == "SIDE_BRANCH":

        return 2

    return 3


def count_error_branches(edges):

    return sum(
        1
        for edge in edges
        if get_routing_role(edge) == "ERROR"
    )


def count_side_branches(edges):

    return sum(
        1
        for edge in edges
        if get_routing_role(edge) == "SIDE_BRANCH"
    )


def target_has_retry_return(
    graph,
    target_id
):

    outgoing = graph.adjacency_map.get(
        target_id,
        []
    )

    for edge in outgoing:

        if is_loopback_edge(edge):

            return True

        target = graph.get_node(
            edge.target
        )

        if target and target.type == "MERGE":

            return True

    return False


def source_has_retry_or_error_branch(
    graph,
    source_id
):

    for edge in graph.adjacency_map.get(
        source_id,
        []
    ):

        if get_routing_role(edge) == "ERROR":

            return True

        if edge.metadata.get(
            "merge_incoming_loopback"
        ):

            return True

        target = graph.get_node(
            edge.target
        )

        if target and target.type == "MERGE":

            return True

    return False


def choose_error_group_layout(
    graph,
    edges
):

    error_edges = [
        edge
        for edge in edges
        if get_routing_role(edge) == "ERROR"
    ]

    if len(error_edges) <= 1:

        return "single"

    has_retry_return = any(
        target_has_retry_return(
            graph,
            edge.target
        )
        for edge in error_edges
    )

    if has_retry_return:

        return "vertical"

    return "horizontal"


def is_review_branch_edge(
    graph,
    edge
):

    target = graph.get_node(
        edge.target
    )

    label = normalize_edge_label(
        edge
    )

    target_label = (
        target.label
        if target and target.label
        else ""
    ).upper().replace(
        "_",
        " "
    )

    review_text = f"{label} {target_label}"

    ordinary_error_terms = [
        "INVALID",
        "INCORRECT",
        "MISMATCH",
        "NOT FOUND",
        "NOT VALID",
        "NOT CORRECT",
    ]

    if any(
        term in label
        for term in ordinary_error_terms
    ):

        return False

    if get_routing_role(edge) != "ERROR" or target is None:

        return False

    if target.type == "MANUAL_ACTIVITY":

        return any(
            keyword in review_text
            for keyword in REVIEW_BRANCH_KEYWORDS
        )

    if (
        target.type == "SYSTEM_ACTIVITY"
        and "DEVIATION" in review_text
    ):

        return True

    return False


def branch_has_terminal_end(
    graph,
    start_id
):

    queue = deque([
        start_id
    ])

    visited = set()

    iterations = 0

    max_iterations = max(
        MIN_LAYOUT_ITERATIONS,
        len(graph.nodes) * MAX_LAYOUT_ITERATION_FACTOR
    )

    while queue:

        iterations += 1

        if iterations > max_iterations:

            break

        node_id = queue.popleft()

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

            if (
                is_loopback_edge(
                    outgoing_edge
                )
                or is_restart_or_return_label(
                    outgoing_edge
                )
            ):

                continue

            queue.append(
                outgoing_edge.target
            )

    return False


def is_side_terminal_outcome_edge(
    graph,
    edge,
    current_x
):

    if get_routing_role(
        edge
    ) != "ERROR":

        return False

    if current_x > REVIEW_BRANCH_X:

        return False

    target = graph.get_node(
        edge.target
    )

    if not target or target.type in [
        "END",
        "MERGE"
    ]:

        return False

    return branch_has_terminal_end(
        graph,
        edge.target
    )


def review_branch_depth(
    graph,
    start_id
):

    queue = deque([
        (
            start_id,
            0
        )
    ])

    best_depth_by_node = {}

    max_depth = 0

    iterations = 0

    max_iterations = max(
        MIN_LAYOUT_ITERATIONS,
        len(graph.nodes) * MAX_LAYOUT_ITERATION_FACTOR
    )

    while queue:

        iterations += 1

        if iterations > max_iterations:

            break

        node_id, depth = queue.popleft()

        if depth > MAX_SIDE_BRANCH_DEPTH:

            continue

        if best_depth_by_node.get(
            node_id,
            -1
        ) >= depth:

            continue

        best_depth_by_node[node_id] = depth

        max_depth = max(
            max_depth,
            depth
        )

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if is_loopback_edge(
                edge
            ) or is_restart_or_return_label(
                edge
            ):

                continue

            target = graph.get_node(
                edge.target
            )

            if not target:

                continue

            if target.type in [
                "END",
                "MERGE"
            ]:

                continue

            routing_role = get_routing_role(
                edge
            )

            next_depth = depth + (
                1
                if routing_role in [
                    "MAIN_FLOW",
                    "SUCCESS"
                ]
                else 0
            )

            target_incoming = [
                incoming_edge
                for incoming_edge in graph.reverse_adjacency_map.get(
                    edge.target,
                    []
                )
                if not is_loopback_edge(
                    incoming_edge
                )
            ]

            if (
                edge.target != start_id
                and len(
                    target_incoming
                ) > 1
            ):

                max_depth = max(
                    max_depth,
                    next_depth
                )

                continue

            queue.append(
                (
                    edge.target,
                    next_depth
                )
            )

    return max_depth


def review_branch_vertical_reserve(
    graph,
    edges
):

    review_edges = [
        edge
        for edge in edges
        if is_review_branch_edge(
            graph,
            edge
        )
    ]

    if not review_edges:

        return 0

    max_depth = max(
        review_branch_depth(
            graph,
            edge.target
        )
        for edge in review_edges
    )

    return (
        ERROR_BRANCH_START_OFFSET
        + (
            max_depth
            * MIN_VERTICAL_GAP
        )
        + SIDE_BRANCH_TAIL_GAP
    )


def estimate_node_height(node):

    if not node or not node.label:

        return 80

    line_count = (
        len(node.label) // 28
    ) + 1

    if node.type == "RESPONSE":

        return max(
            78,
            line_count * 22
        )

    if node.type == "SYSTEM_ACTIVITY":

        return max(
            82,
            line_count * NODE_HEIGHT_UNIT
        )

    if node.type == "MANUAL_ACTIVITY":

        return max(
            82,
            line_count * NODE_HEIGHT_UNIT
        )

    return 80


def estimate_node_width(node):

    if not node or not node.label:

        return 220

    return min(
        max(
            220,
            len(node.label) * 7
        ),
        420
    )


def node_collision_bounds(
    graph,
    node_id,
    node_x,
    node_y,
    padding=28
):

    node = graph.get_node(
        node_id
    )

    if (
        not node
        or node_id not in node_x
        or node_id not in node_y
    ):

        return None

    half_width = estimate_node_width(
        node
    ) / 2

    half_height = estimate_node_height(
        node
    ) / 2

    return {
        "left": node_x[node_id] - half_width - padding,
        "right": node_x[node_id] + half_width + padding,
        "top": node_y[node_id] - half_height - padding,
        "bottom": node_y[node_id] + half_height + padding
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


def incoming_non_loopback_edges(
    graph,
    node_id
):

    return [
        edge
        for edge in graph.reverse_adjacency_map.get(
            node_id,
            []
        )
        if not is_loopback_edge(edge)
    ]


def is_branch_position_node(
    graph,
    node_id
):

    incoming = incoming_non_loopback_edges(
        graph,
        node_id
    )

    if not incoming:

        return False

    roles = [
        get_routing_role(edge)
        for edge in incoming
    ]

    return any(
        role in [
            "ERROR",
            "SIDE_BRANCH"
        ]
        for role in roles
    ) and not any(
        role in [
            "MAIN_FLOW",
            "LOCAL_CONTINUATION"
        ]
        for role in roles
    )


def is_side_terminal_outcome_node(
    graph,
    node_id,
    node_x
):

    for edge in incoming_non_loopback_edges(
        graph,
        node_id
    ):

        if edge.source not in node_x:

            continue

        if is_side_terminal_outcome_edge(
            graph,
            edge,
            node_x[edge.source]
        ):

            return True

    return False


def layout_collision_priority(
    graph,
    node_id
):

    node = graph.get_node(
        node_id
    )

    if not node:

        return 9

    if node.type in [
        "START",
        "END",
        "MERGE"
    ]:

        return 0

    if node.type in [
        "RESPONSE",
        "DECISION",
        "SYSTEM_CHECK",
        "MANUAL_ACTIVITY"
    ]:

        return 1

    if is_branch_position_node(
        graph,
        node_id
    ):

        return 3

    return 2


def collision_with_occupied(
    graph,
    node_id,
    candidate_x,
    candidate_y,
    occupied
):

    original_x = None

    original_y = None

    if node_id in occupied:

        return None

    node = graph.get_node(
        node_id
    )

    if not node:

        return None

    half_width = estimate_node_width(
        node
    ) / 2

    half_height = estimate_node_height(
        node
    ) / 2

    candidate_bounds = {
        "left": candidate_x - half_width - 28,
        "right": candidate_x + half_width + 28,
        "top": candidate_y - half_height - 28,
        "bottom": candidate_y + half_height + 28
    }

    for bounds in occupied.values():

        if bounds_overlap(
            candidate_bounds,
            bounds
        ):

            return bounds

    return None


def branch_x_candidates(
    graph,
    node_id,
    node_x
):

    incoming = incoming_non_loopback_edges(
        graph,
        node_id
    )

    source_x_values = [
        node_x.get(
            edge.source
        )
        for edge in incoming
        if edge.source in node_x
    ]

    if not source_x_values:

        return []

    source_x = source_x_values[0]

    current_x = node_x.get(
        node_id,
        source_x
    )

    if is_side_terminal_outcome_node(
        graph,
        node_id,
        node_x
    ):

        return [
            current_x
        ]

    direction = (
        1
        if current_x >= source_x
        else -1
    )

    candidates = [
        current_x,
        current_x + (
            direction * HORIZONTAL_GAP
        ),
        source_x - (
            direction * HORIZONTAL_GAP
        ),
        source_x + (
            direction * HORIZONTAL_GAP
        ),
        current_x - (
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


def main_path_gap_for_edges(
    node,
    edges,
    error_group_layout="single",
    graph=None
):

    error_branch_count = count_error_branches(
        edges
    )

    node_height = estimate_node_height(
        node
    )

    base_gap = max(
        MIN_VERTICAL_GAP,
        node_height + 105
    )

    if not error_branch_count:

        review_branch_gap = (
            review_branch_vertical_reserve(
                graph,
                edges
            )
            if graph is not None
            else 0
        )

        return max(
            base_gap,
            review_branch_gap
        )

    review_branch_gap = (
        review_branch_vertical_reserve(
            graph,
            edges
        )
        if graph is not None
        else 0
    )

    if error_group_layout == "horizontal":

        return max(
            base_gap,
            ERROR_BRANCH_START_OFFSET
            + POST_ERROR_MAIN_GAP,
            review_branch_gap
        )

    return max(
        base_gap,
        ERROR_BRANCH_START_OFFSET
        + (
            (error_branch_count - 1)
            * ERROR_BRANCH_VERTICAL_GAP
        )
        + POST_ERROR_MAIN_GAP,
        review_branch_gap
    )


def should_update_position(
    node_id,
    next_x,
    next_y,
    node_x,
    node_y
):

    if node_id not in node_y:

        return True

    if next_y > node_y[node_id]:

        return True

    return (
        next_y == node_y[node_id]
        and next_x != node_x.get(node_id)
    )


def direct_main_success_owner_edge(
    graph,
    node_id,
    node_x
):

    for incoming_edge in incoming_non_loopback_edges(
        graph,
        node_id
    ):

        if get_routing_role(
            incoming_edge
        ) not in [
            "MAIN_FLOW",
            "SUCCESS",
            "LOCAL_CONTINUATION"
        ]:

            continue

        source = graph.get_node(
            incoming_edge.source
        )

        if not source or source.type != "RESPONSE":

            continue

        if node_x.get(
            incoming_edge.source
        ) != MAIN_X:

            continue

        return incoming_edge

    return None


def should_update_position_for_edge(
    graph,
    edge,
    next_x,
    next_y,
    node_x,
    node_y
):

    if edge.target not in node_y:

        return True

    owner_edge = direct_main_success_owner_edge(
        graph,
        edge.target,
        node_x
    )

    if (
        owner_edge
        and owner_edge.source != edge.source
        and next_y > node_y[edge.target]
    ):

        return False

    return should_update_position(
        edge.target,
        next_x,
        next_y,
        node_x,
        node_y
    )


def is_backward_edge(
    edge,
    current_y,
    node_y
):

    if edge.target not in node_y:

        return False

    return node_y[edge.target] <= current_y


def build_forward_layout(graph):

    node_x = {}

    node_y = {}

    error_count_by_source = {}

    side_count_by_source = {}

    success_count_by_source = {}

    root = graph.get_start_node()

    if not root:

        return node_x, node_y

    node_x[root.id] = MAIN_X

    node_y[root.id] = 0

    queue = deque([
        root.id
    ])

    max_iterations = max(
        MIN_LAYOUT_ITERATIONS,
        len(graph.nodes) * MAX_LAYOUT_ITERATION_FACTOR
    )

    iterations = 0

    while queue:

        iterations += 1

        if iterations > max_iterations:

            break

        node_id = queue.popleft()

        node = graph.get_node(
            node_id
        )

        if not node:

            continue

        current_x = node_x.get(
            node_id,
            MAIN_X
        )

        current_y = node_y.get(
            node_id,
            0
        )

        raw_outgoing = graph.adjacency_map.get(
            node_id,
            []
        )

        outgoing = [
            edge
            for edge in raw_outgoing
            if not is_loopback_edge(edge)
        ]

        outgoing.sort(
            key=edge_priority
        )

        spacing_edges = outgoing + [
            edge
            for edge in raw_outgoing
            if is_retry_error_loopback_edge(
                edge
            )
        ]

        error_group_layout = choose_error_group_layout(
            graph,
            spacing_edges
        )

        main_path_gap = main_path_gap_for_edges(
            node,
            spacing_edges,
            error_group_layout,
            graph
        )

        error_branch_count = count_error_branches(
            spacing_edges
        )

        parallel_success_edges = [
            edge
            for edge in outgoing
            if (
                get_routing_role(
                    edge
                ) == "SUCCESS"
                and graph.get_node(
                    edge.target
                )
                and graph.get_node(
                    edge.target
                ).type not in [
                    "END",
                    "MERGE"
                ]
            )
        ]

        has_parallel_success = (
            node.type == "RESPONSE"
            and len(
                parallel_success_edges
            ) > 1
        )

        for edge in outgoing:

            target = graph.get_node(
                edge.target
            )

            if not target:

                continue

            routing_role = get_routing_role(
                edge
            )

            if (
                target.type not in [
                    "END",
                    "MERGE"
                ]
                and is_backward_edge(
                    edge,
                    current_y,
                    node_y
                )
            ):

                continue

            next_x = current_x

            next_y = current_y + main_path_gap

            if routing_role == "ERROR":

                error_count_by_source[edge.source] = (
                    error_count_by_source.get(
                        edge.source,
                        0
                    ) + 1
                )

                branch_index = error_count_by_source[
                    edge.source
                ]

                is_review_branch = is_review_branch_edge(
                    graph,
                    edge
                )

                is_side_terminal_outcome = is_side_terminal_outcome_edge(
                    graph,
                    edge,
                    current_x
                )

                has_mixed_side_branches = any(
                    get_routing_role(outgoing_edge) == "SIDE_BRANCH"
                    for outgoing_edge in outgoing
                )

                if (
                    is_side_terminal_outcome
                ):

                    next_x = current_x

                elif (
                    is_review_branch
                    or current_x <= REVIEW_BRANCH_X
                ):

                    next_x = (
                        current_x - HORIZONTAL_GAP
                        if current_x <= REVIEW_BRANCH_X
                        else REVIEW_BRANCH_X
                    )

                else:

                    if error_group_layout == "horizontal":

                        next_x = (
                            ERROR_COLUMN_X
                            + (
                                (branch_index - 1)
                                * HORIZONTAL_GAP
                            )
                        )

                    else:

                        next_x = (
                            current_x + HORIZONTAL_GAP
                            if current_x >= ERROR_COLUMN_X
                            else ERROR_COLUMN_X
                        )

                if error_branch_count == 1:

                    next_y = (
                        current_y
                        + terminal_outcome_vertical_gap(
                            edge
                        )
                        if is_side_terminal_outcome
                        else current_y + ERROR_BRANCH_VERTICAL_GAP
                        if has_mixed_side_branches
                        else current_y
                    )

                elif is_review_branch:

                    next_y = (
                        current_y
                        + (
                            (branch_index - 1)
                            * ERROR_BRANCH_VERTICAL_GAP
                        )
                    )

                elif error_group_layout == "horizontal":

                    next_y = (
                        current_y
                        + ERROR_BRANCH_START_OFFSET
                    )

                else:

                    next_y = (
                        current_y
                        + (
                            (branch_index - 1)
                            * ERROR_BRANCH_VERTICAL_GAP
                        )
                    )

            elif routing_role == "SIDE_BRANCH":

                side_count_by_source[edge.source] = (
                    side_count_by_source.get(
                        edge.source,
                        0
                    ) + 1
                )

                branch_index = side_count_by_source[
                    edge.source
                ]

                branch_row = (
                    branch_index - 1
                ) // 2

                if current_x == MAIN_X:

                    next_x = (
                        current_x - HORIZONTAL_GAP
                        if branch_index % 2 == 1
                        else current_x + HORIZONTAL_GAP
                    )

                else:

                    next_x = (
                        current_x + HORIZONTAL_GAP
                        if current_x < MAIN_X
                        else current_x - HORIZONTAL_GAP
                    )

                next_y = (
                    current_y
                    + main_path_gap
                    + (
                        branch_row
                        * ERROR_BRANCH_VERTICAL_GAP
                    )
                )

                if (
                    target.type == "RESPONSE"
                    and not any(
                        (
                            not is_loopback_edge(outgoing_edge)
                            and get_routing_role(
                                outgoing_edge
                            )
                            in [
                                "MAIN_FLOW",
                                "SUCCESS",
                                "LOCAL_CONTINUATION"
                            ]
                            and graph.get_node(
                                outgoing_edge.target
                            )
                            and graph.get_node(
                                outgoing_edge.target
                            ).type not in [
                                "END",
                                "MERGE"
                            ]
                        )
                        for outgoing_edge in graph.adjacency_map.get(
                            edge.target,
                            []
                        )
                    )
                ):

                    next_y = max(
                        next_y,
                        current_y + MIN_VERTICAL_GAP
                    )

            elif routing_role == "LOCAL_CONTINUATION":

                next_x = current_x

                next_y = current_y + main_path_gap

            elif routing_role == "SUCCESS":

                if has_parallel_success:

                    success_count_by_source[edge.source] = (
                        success_count_by_source.get(
                            edge.source,
                            0
                        ) + 1
                    )

                    branch_index = success_count_by_source[
                        edge.source
                    ]

                    branch_row = (
                        branch_index - 1
                    ) // 2

                    if current_x == MAIN_X:

                        next_x = (
                            current_x - HORIZONTAL_GAP
                            if branch_index % 2 == 1
                            else current_x + HORIZONTAL_GAP
                        )

                    else:

                        next_x = (
                            current_x + HORIZONTAL_GAP
                            if current_x < MAIN_X
                            else current_x - HORIZONTAL_GAP
                        )

                    next_y = (
                        current_y
                        + main_path_gap
                        + (
                            branch_row
                            * ERROR_BRANCH_VERTICAL_GAP
                        )
                    )

                elif is_spine_node(node):

                    next_x = MAIN_X

                else:

                    next_x = current_x

            elif routing_role == "MAIN_FLOW":

                if is_spine_node(target):

                    next_x = (
                        MAIN_X
                        if current_x == MAIN_X
                        else current_x
                    )

                else:

                    next_x = current_x

            if (
                routing_role in [
                    "MAIN_FLOW",
                    "SUCCESS"
                ]
                and is_spine_node(target)
                and current_x == MAIN_X
                and not has_parallel_success
            ):

                next_x = MAIN_X

            if should_update_position_for_edge(
                graph,
                edge,
                next_x,
                next_y,
                node_x,
                node_y
            ):

                node_x[edge.target] = next_x

                node_y[edge.target] = next_y

                if target.type not in [
                    "END",
                    "MERGE"
                ]:

                    queue.append(
                        edge.target
                    )

    return node_x, node_y


def is_forward_spacing_edge(graph, edge):

    if is_loopback_edge(edge):

        return False

    source = graph.get_node(
        edge.source
    )

    target = graph.get_node(
        edge.target
    )

    if not source or not target:

        return False

    if target.type in [
        "END",
        "MERGE"
    ]:

        return False

    routing_role = get_routing_role(
        edge
    )

    return routing_role in [
        "MAIN_FLOW",
        "SUCCESS",
        "LOCAL_CONTINUATION"
    ]


def is_side_success_rejoin_edge(
    graph,
    edge,
    node_x
):

    if get_routing_role(
        edge
    ) != "SUCCESS":

        return False

    incoming = non_loopback_incoming_edges(
        graph,
        edge.target
    )

    if len(
        incoming
    ) < 2:

        return False

    source_x = node_x.get(
        edge.source
    )

    target_x = node_x.get(
        edge.target
    )

    if source_x is None or target_x is None:

        return False

    return source_x != target_x


def collect_forward_spacing_chain(graph, start_node_id):

    visited = set()

    queue = deque([
        start_node_id
    ])

    while queue:

        node_id = queue.popleft()

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if not is_forward_spacing_edge(
                graph,
                edge
            ):

                continue

            if edge.target in visited:

                continue

            queue.append(
                edge.target
            )

    return visited


def enforce_forward_spacing(
    graph,
    node_x,
    node_y
):

    max_iterations = max(
        MIN_LAYOUT_ITERATIONS,
        len(graph.nodes) * MAX_LAYOUT_ITERATION_FACTOR
    )

    for _ in range(max_iterations):

        changed = False

        for edge in graph.edges:

            if not is_forward_spacing_edge(
                graph,
                edge
            ):

                continue

            if (
                edge.source not in node_y
                or edge.target not in node_y
            ):

                continue

            if is_side_success_rejoin_edge(
                graph,
                edge,
                node_x
            ):

                continue

            if (
                is_restart_or_return_label(edge)
                and node_y[edge.target] <= node_y[edge.source]
            ):

                continue

            source = graph.get_node(
                edge.source
            )

            required_gap = max(
                MIN_VERTICAL_GAP,
                estimate_node_height(source) + 100
            )

            minimum_target_y = (
                node_y[edge.source]
                + required_gap
            )

            if node_y[edge.target] >= minimum_target_y:

                continue

            delta = minimum_target_y - node_y[edge.target]

            for node_id in collect_forward_spacing_chain(
                graph,
                edge.target
            ):

                if node_id not in node_y:

                    continue

                node_y[node_id] += delta

            changed = True

        if not changed:

            break


def is_response_owned_forward_branch(
    graph,
    edge
):

    if is_loopback_edge(
        edge
    ):

        return False

    source = graph.get_node(
        edge.source
    )

    target = graph.get_node(
        edge.target
    )

    if not source or not target:

        return False

    if source.type != "RESPONSE":

        return False

    if target.type in [
        "END",
        "MERGE"
    ]:

        return False

    routing_role = get_routing_role(
        edge
    )

    return routing_role in [
        "ERROR",
        "SIDE_BRANCH",
        "SUCCESS",
        "LOCAL_CONTINUATION"
    ]


def enforce_response_branch_ownership(
    graph,
    node_x,
    node_y
):

    max_iterations = max(
        MIN_LAYOUT_ITERATIONS,
        len(graph.nodes) * MAX_LAYOUT_ITERATION_FACTOR
    )

    for _ in range(max_iterations):

        changed = False

        for edge in graph.edges:

            if not is_response_owned_forward_branch(
                graph,
                edge
            ):

                continue

            if (
                edge.source not in node_y
                or edge.target not in node_y
            ):

                continue

            owner_edge = direct_main_success_owner_edge(
                graph,
                edge.target,
                node_x
            )

            if (
                owner_edge
                and owner_edge.source != edge.source
            ):

                continue

            minimum_target_y = node_y[
                edge.source
            ]

            if node_y[edge.target] >= minimum_target_y:

                continue

            delta = minimum_target_y - node_y[
                edge.target
            ]

            shift_chain = collect_forward_spacing_chain(
                graph,
                edge.target
            )

            if edge.source in shift_chain:

                continue

            for node_id in shift_chain:

                if node_id not in node_y:

                    continue

                node_y[node_id] += delta

            changed = True

        if not changed:

            break


def same_source_retry_error_edges(
    graph,
    source_id
):

    source = graph.get_node(
        source_id
    )

    if not source or source.type != "RESPONSE":

        return []

    return [
        edge
        for edge in graph.adjacency_map.get(
            source_id,
            []
        )
        if (
            get_routing_role(
                edge
            ) == "ERROR"
            and edge.target in graph.nodes
            and target_has_retry_return(
                graph,
                edge.target
            )
        )
    ]


def same_source_right_error_edges(
    graph,
    source_id,
    node_x
):

    source = graph.get_node(
        source_id
    )

    if not source or source.type != "RESPONSE":

        return []

    source_x = node_x.get(
        source_id
    )

    if source_x is None:

        return []

    result = []

    for edge in graph.adjacency_map.get(
        source_id,
        []
    ):

        target = graph.get_node(
            edge.target
        )

        if not target:

            continue

        if target.type != "SYSTEM_ACTIVITY":

            continue

        if get_routing_role(
            edge
        ) != "ERROR":

            continue

        target_x = node_x.get(
            edge.target
        )

        if target_x is None:

            continue

        if target_x < source_x:

            continue

        result.append(
            edge
        )

    return result


def error_group_column_x(source_x):

    if source_x == MAIN_X:

        return ERROR_COLUMN_X

    if source_x < MAIN_X:

        return source_x - HORIZONTAL_GAP

    return source_x + HORIZONTAL_GAP


def align_same_source_retry_error_groups(
    graph,
    node_x,
    node_y
):

    for source_id in graph.nodes:

        if source_id not in node_x or source_id not in node_y:

            continue

        error_edges = same_source_retry_error_edges(
            graph,
            source_id
        )

        right_error_edges = same_source_right_error_edges(
            graph,
            source_id,
            node_x
        )

        if len(
            right_error_edges
        ) > len(
            error_edges
        ):

            error_edges = right_error_edges

        if len(
            error_edges
        ) < 2:

            continue

        group_x = error_group_column_x(
            node_x[source_id]
        )

        start_y = node_y[source_id]

        for index, edge in enumerate(
            error_edges
        ):

            if edge.target not in node_x or edge.target not in node_y:

                continue

            next_y = (
                start_y
                + (
                    index
                    * ERROR_BRANCH_VERTICAL_GAP
                )
            )

            delta_y = next_y - node_y[edge.target]

            node_x[edge.target] = group_x

            for node_id in collect_forward_spacing_chain(
                graph,
                edge.target
            ):

                if node_id not in node_y:

                    continue

                node_y[node_id] += delta_y


def exclusive_branch_chain(
    graph,
    start_id,
    max_depth=10
):

    branch_nodes = set()

    queue = deque([
        (
            start_id,
            0
        )
    ])

    while queue:

        node_id, depth = queue.popleft()

        if depth > max_depth:

            continue

        if node_id in branch_nodes:

            continue

        node = graph.get_node(
            node_id
        )

        if not node or node.type == "MERGE":

            continue

        incoming = [
            edge
            for edge in non_loopback_incoming_edges(
                graph,
                node_id
            )
        ]

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

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if is_loopback_edge(
                edge
            ):

                continue

            role = get_routing_role(
                edge
            )

            if role not in [
                "MAIN_FLOW",
                "SUCCESS",
                "LOCAL_CONTINUATION",
                "ERROR",
                "SIDE_BRANCH"
            ]:

                continue

            target = graph.get_node(
                edge.target
            )

            if not target or target.type == "MERGE":

                continue

            queue.append(
                (
                    edge.target,
                    depth + 1
                )
            )

    return branch_nodes


def branch_side_candidate_score(
    graph,
    edge,
    branch_nodes,
    candidate_x,
    node_x,
    node_y
):

    if edge.source not in node_x or edge.source not in node_y:

        return 999

    if edge.target not in node_y:

        return 999

    source_x = node_x[edge.source]

    source_y = node_y[edge.source]

    target_y = node_y[edge.target]

    x_min = min(
        source_x,
        candidate_x
    )

    x_max = max(
        source_x,
        candidate_x
    )

    y_min = min(
        source_y,
        target_y
    )

    y_max = max(
        source_y,
        target_y
    )

    score = 0

    for node_id in graph.nodes:

        if (
            node_id in branch_nodes
            or node_id == edge.source
            or node_id not in node_x
            or node_id not in node_y
        ):

            continue

        bounds = node_collision_bounds(
            graph,
            node_id,
            node_x,
            node_y,
            padding=36
        )

        if not bounds:

            continue

        if (
            bounds["left"] <= candidate_x <= bounds["right"]
            and not (
                bounds["bottom"] < y_min
                or bounds["top"] > y_max
            )
        ):

            score += 4

        if (
            bounds["top"] <= source_y <= bounds["bottom"]
            and not (
                bounds["right"] < x_min
                or bounds["left"] > x_max
            )
        ):

            score += 3

        if (
            bounds["top"] <= target_y <= bounds["bottom"]
            and not (
                bounds["right"] < x_min
                or bounds["left"] > x_max
            )
        ):

            score += 2

    return score


def segment_intersects_bounds(
    start_x,
    start_y,
    end_x,
    end_y,
    bounds
):

    if not bounds:

        return False

    if abs(
        start_x - end_x
    ) < 1:

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

    if abs(
        start_y - end_y
    ) < 1:

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


def branch_return_candidate_score(
    graph,
    branch_nodes,
    current_x,
    candidate_x,
    node_x,
    node_y
):

    score = 0

    delta_x = candidate_x - current_x

    for branch_node_id in branch_nodes:

        if branch_node_id not in node_y:

            continue

        for outgoing_edge in graph.adjacency_map.get(
            branch_node_id,
            []
        ):

            if not is_loopback_edge(
                outgoing_edge
            ):

                continue

            if outgoing_edge.target not in node_x or outgoing_edge.target not in node_y:

                continue

            source_x = node_x.get(
                branch_node_id,
                current_x
            ) + delta_x

            source_y = node_y[branch_node_id]

            target_x = node_x[outgoing_edge.target]

            target_y = node_y[outgoing_edge.target]

            return_lane_x = (
                source_x - 160
                if source_x < target_x
                else source_x + 160
            )

            path_segments = [
                (
                    source_x,
                    source_y,
                    return_lane_x,
                    source_y
                ),
                (
                    return_lane_x,
                    source_y,
                    return_lane_x,
                    target_y
                ),
                (
                    return_lane_x,
                    target_y,
                    target_x,
                    target_y
                )
            ]

            for node_id in graph.nodes:

                if (
                    node_id in branch_nodes
                    or node_id == outgoing_edge.target
                    or node_id not in node_x
                    or node_id not in node_y
                ):

                    continue

                node = graph.get_node(
                    node_id
                )

                if not node or node.type in [
                    "MERGE",
                    "CONNECTOR"
                ]:

                    continue

                bounds = node_collision_bounds(
                    graph,
                    node_id,
                    node_x,
                    node_y,
                    padding=42
                )

                if not bounds:

                    continue

                if any(
                    segment_intersects_bounds(
                        *segment,
                        bounds
                    )
                    for segment in path_segments
                ):

                    score += 8

            if (
                source_x < target_x
                and any(
                    (
                        node_id not in branch_nodes
                        and node_id in node_x
                        and node_id in node_y
                        and node_x[node_id] < target_x
                        and min(source_y, target_y) <= node_y[node_id] <= max(source_y, target_y)
                    )
                    for node_id in graph.nodes
                )
            ):

                score += 6

            approach_side = (
                -1
                if source_x < target_x
                else 1
            )

            approach_top = min(
                source_y,
                target_y
            ) - 900

            approach_bottom = max(
                source_y,
                target_y
            ) + 140

            for node_id in graph.nodes:

                if (
                    node_id in branch_nodes
                    or node_id == outgoing_edge.target
                    or node_id not in node_x
                    or node_id not in node_y
                ):

                    continue

                if not (
                    approach_top <= node_y[node_id] <= approach_bottom
                ):

                    continue

                if approach_side < 0:

                    if not (
                        node_x[node_id] < target_x
                        and node_x[node_id] >= source_x - HORIZONTAL_GAP
                    ):

                        continue

                else:

                    if not (
                        node_x[node_id] > target_x
                        and node_x[node_id] <= source_x + HORIZONTAL_GAP
                    ):

                        continue

                score += 5

    return score


def branch_returns_to_upstream_main_spine(
    graph,
    branch_nodes,
    edge,
    node_x,
    node_y
):

    if edge.source not in node_x or edge.source not in node_y:

        return False

    source_x = node_x[edge.source]

    source_y = node_y[edge.source]

    for branch_node_id in branch_nodes:

        for outgoing_edge in graph.adjacency_map.get(
            branch_node_id,
            []
        ):

            if not is_loopback_edge(
                outgoing_edge
            ):

                continue

            if outgoing_edge.target not in node_x or outgoing_edge.target not in node_y:

                continue

            if node_y[outgoing_edge.target] >= source_y:

                continue

            if abs(
                node_x[outgoing_edge.target] - source_x
            ) <= SIDE_COLUMN_TOLERANCE:

                return True

    return False


def maybe_flip_response_side_branch(
    graph,
    edge,
    node_x,
    node_y
):

    if not is_response_owned_forward_branch(
        graph,
        edge
    ):

        return False

    if edge.source not in node_x or edge.target not in node_x:

        return False

    if edge.source not in node_y or edge.target not in node_y:

        return False

    has_mixed_retry_or_error_branch = (
        get_routing_role(edge) == "SIDE_BRANCH"
        and source_has_retry_or_error_branch(
            graph,
            edge.source
        )
    )

    if (
        target_has_retry_return(
            graph,
            edge.target
        )
        and not has_mixed_retry_or_error_branch
        and not is_review_branch_edge(
            graph,
            edge
        )
    ):

        return False

    target_incoming = non_loopback_incoming_edges(
        graph,
        edge.target
    )

    if len(
        target_incoming
    ) > 1:

        return False

    source_x = node_x[edge.source]

    current_x = node_x[edge.target]

    if abs(
        current_x - source_x
    ) <= SIDE_COLUMN_TOLERANCE:

        return False

    left_x = source_x - HORIZONTAL_GAP

    right_x = source_x + HORIZONTAL_GAP

    alternate_x = (
        right_x
        if current_x < source_x
        else left_x
    )

    branch_nodes = exclusive_branch_chain(
        graph,
        edge.target
    )

    if not branch_nodes:

        return False

    current_score = branch_side_candidate_score(
        graph,
        edge,
        branch_nodes,
        current_x,
        node_x,
        node_y
    )

    current_score += branch_return_candidate_score(
        graph,
        branch_nodes,
        current_x,
        current_x,
        node_x,
        node_y
    )

    alternate_score = branch_side_candidate_score(
        graph,
        edge,
        branch_nodes,
        alternate_x,
        node_x,
        node_y
    )

    alternate_score += branch_return_candidate_score(
        graph,
        branch_nodes,
        current_x,
        alternate_x,
        node_x,
        node_y
    )

    if (
        is_review_branch_edge(
            graph,
            edge
        )
        and current_x < source_x
        and alternate_x > source_x
        and current_score == alternate_score
        and branch_returns_to_upstream_main_spine(
            graph,
            branch_nodes,
            edge,
            node_x,
            node_y
        )
    ):

        delta_x = alternate_x - current_x

        for node_id in branch_nodes:

            if node_id in node_x:

                node_x[node_id] += delta_x

        return True

    if (
        has_mixed_retry_or_error_branch
        and current_x > source_x
        and alternate_x < source_x
        and alternate_score <= current_score + SIDE_FALLBACK_SCORE_MARGIN
    ):

        delta_x = alternate_x - current_x

        for node_id in branch_nodes:

            if node_id in node_x:

                node_x[node_id] += delta_x

        return True

    if current_score < alternate_score + SIDE_FALLBACK_SCORE_MARGIN:

        return False

    delta_x = alternate_x - current_x

    for node_id in branch_nodes:

        if node_id in node_x:

            node_x[node_id] += delta_x

    return True


def resolve_response_branch_side_crossovers(
    graph,
    node_x,
    node_y
):

    max_iterations = max(
        3,
        min(
            8,
            len(graph.nodes)
        )
    )

    for _ in range(max_iterations):

        changed = False

        for edge in graph.edges:

            if maybe_flip_response_side_branch(
                graph,
                edge,
                node_x,
                node_y
            ):

                changed = True

        if not changed:

            break


def enforce_side_response_branch_visibility(
    graph,
    node_x,
    node_y
):

    for edge in graph.edges:

        if get_routing_role(
            edge
        ) != "SIDE_BRANCH":

            continue

        source = graph.get_node(
            edge.source
        )

        target = graph.get_node(
            edge.target
        )

        if not source or not target:

            continue

        if source.type != "RESPONSE" or target.type != "RESPONSE":

            continue

        if edge.source not in node_y or edge.target not in node_y:

            continue

        minimum_y = node_y[edge.source] + MIN_VERTICAL_GAP

        if node_y[edge.target] >= minimum_y:

            continue

        delta = minimum_y - node_y[edge.target]

        for node_id in collect_forward_spacing_chain(
            graph,
            edge.target
        ):

            if node_id in node_y:

                node_y[node_id] += delta


def align_side_branch_targets(
    graph,
    node_x,
    node_y
):

    side_counts_by_source = {}

    for edge in graph.edges:

        if get_routing_role(
            edge
        ) != "SIDE_BRANCH":

            continue

        if (
            edge.source not in node_x
            or edge.source not in node_y
            or edge.target not in node_x
            or edge.target not in node_y
        ):

            continue

        side_counts_by_source[edge.source] = (
            side_counts_by_source.get(
                edge.source,
                0
            ) + 1
        )

        branch_index = side_counts_by_source[
            edge.source
        ]

        source_x = node_x[edge.source]

        branch_row = (
            branch_index - 1
        ) // 2

        if source_x == MAIN_X:

            node_x[edge.target] = (
                source_x - HORIZONTAL_GAP
                if branch_index % 2 == 1
                else source_x + HORIZONTAL_GAP
            )

        else:

            node_x[edge.target] = (
                source_x + HORIZONTAL_GAP
                if source_x < MAIN_X
                else source_x - HORIZONTAL_GAP
            )

        source_node = graph.get_node(
            edge.source
        )

        main_path_gap = max(
            MIN_VERTICAL_GAP,
            estimate_node_height(
                source_node
            ) + 105
        )

        node_y[edge.target] = (
            node_y[edge.source]
            + main_path_gap
            + (
                branch_row
                * ERROR_BRANCH_VERTICAL_GAP
            )
        )


def non_loopback_incoming_edges(
    graph,
    node_id
):

    return [
        edge
        for edge in graph.reverse_adjacency_map.get(
            node_id,
            []
        )
        if not is_loopback_edge(
            edge
        )
    ]


def main_continuation_targets(
    graph,
    node_id
):

    result = []

    for edge in graph.adjacency_map.get(
        node_id,
        []
    ):

        if is_loopback_edge(
            edge
        ):

            continue

        if get_routing_role(
            edge
        ) not in [
            "MAIN_FLOW",
            "SUCCESS",
            "LOCAL_CONTINUATION"
        ]:

            continue

        target = graph.get_node(
            edge.target
        )

        if not target or target.type in [
            "END",
            "MERGE"
        ]:

            continue

        result.append(
            edge.target
        )

    return result


def align_rejoin_spine(
    graph,
    node_x,
    node_y
):

    rejoin_nodes = []

    for node_id, node in graph.nodes.items():

        if node.type in [
            "END",
            "MERGE"
        ]:

            continue

        incoming = [
            edge
            for edge in non_loopback_incoming_edges(
                graph,
                node_id
            )
            if get_routing_role(
                edge
            ) in [
                "MAIN_FLOW",
                "SUCCESS",
                "SIDE_BRANCH",
                "LOCAL_CONTINUATION"
            ]
        ]

        if len(
            incoming
        ) < 2:

            continue

        source_positions = [
            node_x.get(
                edge.source
            )
            for edge in incoming
            if edge.source in node_x
        ]

        if not source_positions:

            continue

        has_left_source = any(
            x < MAIN_X
            for x in source_positions
        )

        has_right_source = any(
            x > MAIN_X
            for x in source_positions
        )

        has_main_source = any(
            x == MAIN_X
            for x in source_positions
        )

        if not (
            has_main_source
            or (
                has_left_source
                and has_right_source
            )
        ):

            continue

        rejoin_nodes.append(
            node_id
        )

    queue = deque(
        rejoin_nodes
    )

    visited = set()

    while queue:

        node_id = queue.popleft()

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        if node_id in node_x:

            node_x[node_id] = MAIN_X

        for target_id in main_continuation_targets(
            graph,
            node_id
        ):

            queue.append(
                target_id
            )


def align_side_success_rejoins(
    graph,
    node_x,
    node_y
):

    for node_id, node in graph.nodes.items():

        if node.type in [
            "END",
            "MERGE"
        ]:

            continue

        incoming = non_loopback_incoming_edges(
            graph,
            node_id
        )

        if len(
            incoming
        ) < 2:

            continue

        if direct_main_success_owner_edge(
            graph,
            node_id,
            node_x
        ):

            continue

        side_success_sources = [
            edge.source
            for edge in incoming
            if (
                get_routing_role(
                    edge
                ) == "SUCCESS"
                and edge.source in node_y
                and node_x.get(
                    edge.source
                ) != node_x.get(
                    node_id
                )
            )
        ]

        if not side_success_sources:

            continue

        target_y = max(
            node_y[source_id]
            for source_id in side_success_sources
        ) + MIN_VERTICAL_GAP

        target_y = max(
            target_y,
            max(
                node_y[edge.source] + MIN_VERTICAL_GAP
                for edge in incoming
                if edge.source in node_y
            )
        )

        current_y = node_y.get(
            node_id
        )

        if current_y is None or target_y == current_y:

            continue

        delta = target_y - current_y

        for shift_node_id in collect_forward_spacing_chain(
            graph,
            node_id
        ):

            if shift_node_id not in node_y:

                continue

            node_y[shift_node_id] += delta


def branch_reaches_node(
    graph,
    start_id,
    target_id,
    max_depth=8
):

    queue = deque([
        (
            start_id,
            0
        )
    ])

    visited = set()

    while queue:

        node_id, depth = queue.popleft()

        if depth > max_depth:

            continue

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        if node_id == target_id:

            return True

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if is_loopback_edge(
                edge
            ):

                continue

            if get_routing_role(
                edge
            ) not in [
                "MAIN_FLOW",
                "SUCCESS",
                "LOCAL_CONTINUATION"
            ]:

                continue

            queue.append(
                (
                    edge.target,
                    depth + 1
                )
            )

    return False


def collect_branch_until_rejoin(
    graph,
    start_id,
    rejoin_id,
    max_depth=12
):

    branch_nodes = set()

    queue = deque([
        (
            start_id,
            0
        )
    ])

    visited = set()

    while queue:

        node_id, depth = queue.popleft()

        if depth > max_depth:

            continue

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        if node_id == rejoin_id:

            continue

        branch_nodes.add(
            node_id
        )

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if is_loopback_edge(
                edge
            ):

                continue

            if get_routing_role(
                edge
            ) not in [
                "MAIN_FLOW",
                "SUCCESS",
                "LOCAL_CONTINUATION"
            ]:

                continue

            queue.append(
                (
                    edge.target,
                    depth + 1
                )
            )

    return branch_nodes


def align_direct_indirect_success_rejoins(
    graph,
    node_x,
    node_y
):

    for source_id, source_node in graph.nodes.items():

        if source_node.type != "RESPONSE":

            continue

        if source_id not in node_x or source_id not in node_y:

            continue

        success_edges = [
            edge
            for edge in graph.adjacency_map.get(
                source_id,
                []
            )
            if (
                get_routing_role(
                    edge
                ) == "SUCCESS"
                and edge.target in node_x
                and edge.target in node_y
            )
        ]

        if len(
            success_edges
        ) < 2:

            continue

        for direct_edge in success_edges:

            for indirect_edge in success_edges:

                if direct_edge is indirect_edge:

                    continue

                if not branch_reaches_node(
                    graph,
                    indirect_edge.target,
                    direct_edge.target
                ):

                    continue

                source_x = node_x[source_id]

                side_x = (
                    source_x - HORIZONTAL_GAP
                    if source_x == MAIN_X
                    else source_x + (
                        HORIZONTAL_GAP
                        if source_x < MAIN_X
                        else -HORIZONTAL_GAP
                    )
                )

                direct_y = max(
                    node_y[direct_edge.target],
                    node_y[source_id] + MIN_VERTICAL_GAP
                )

                node_x[direct_edge.target] = source_x
                node_y[direct_edge.target] = direct_y

                branch_nodes = collect_branch_until_rejoin(
                    graph,
                    indirect_edge.target,
                    direct_edge.target
                )

                for node_id in branch_nodes:

                    if node_id not in node_x:

                        continue

                    node_x[node_id] = side_x

                node_x[indirect_edge.target] = side_x


def first_forward_rejoin_target(
    graph,
    node_id
):

    outgoing = [
        edge
        for edge in graph.adjacency_map.get(
            node_id,
            []
        )
        if (
            not is_loopback_edge(
                edge
            )
            and get_routing_role(
                edge
            )
            in [
                "MAIN_FLOW",
                "SUCCESS",
                "LOCAL_CONTINUATION"
            ]
        )
    ]

    if len(
        outgoing
    ) != 1:

        return None

    target = graph.get_node(
        outgoing[0].target
    )

    if not target or target.type in [
        "END",
        "MERGE"
    ]:

        return None

    return outgoing[0].target


def align_parallel_success_branch_targets(
    graph,
    node_x,
    node_y
):

    for source_id, source_node in graph.nodes.items():

        if source_node.type != "RESPONSE":

            continue

        if source_id not in node_x or source_id not in node_y:

            continue

        success_edges = [
            edge
            for edge in graph.adjacency_map.get(
                source_id,
                []
            )
            if (
                get_routing_role(
                    edge
                ) == "SUCCESS"
                and edge.target in node_x
                and edge.target in node_y
                and graph.get_node(
                    edge.target
                )
                and graph.get_node(
                    edge.target
                ).type not in [
                    "END",
                    "MERGE"
                ]
            )
        ]

        if len(
            success_edges
        ) < 2:

            continue

        skip_direct_indirect = False

        for first_edge in success_edges:

            for second_edge in success_edges:

                if first_edge is second_edge:

                    continue

                if branch_reaches_node(
                    graph,
                    first_edge.target,
                    second_edge.target,
                    max_depth=6
                ):

                    skip_direct_indirect = True

                    break

            if skip_direct_indirect:

                break

        if skip_direct_indirect:

            continue

        rejoin_targets = {
            first_forward_rejoin_target(
                graph,
                edge.target
            )
            for edge in success_edges
        }

        rejoin_targets.discard(
            None
        )

        shared_rejoin = (
            next(
                iter(
                    rejoin_targets
                )
            )
            if len(
                rejoin_targets
            ) == 1
            else None
        )

        source_x = node_x[source_id]

        branch_y = max(
            node_y[source_id] + MIN_VERTICAL_GAP,
            min(
                node_y[edge.target]
                for edge in success_edges
            )
        )

        side_columns = [
            source_x - HORIZONTAL_GAP,
            source_x + HORIZONTAL_GAP
        ]

        if source_x != MAIN_X:

            side_columns = [
                source_x,
                MAIN_X
            ]

        for index, edge in enumerate(
            success_edges
        ):

            target_id = edge.target

            incoming = non_loopback_incoming_edges(
                graph,
                target_id
            )

            if len(
                incoming
            ) > 1:

                continue

            target_x = side_columns[
                index % len(
                    side_columns
                )
            ]

            node_x[target_id] = target_x

            node_y[target_id] = (
                branch_y
                + (
                    (index // len(side_columns))
                    * ERROR_BRANCH_VERTICAL_GAP
                )
            )

        if shared_rejoin and shared_rejoin in node_x:

            node_x[shared_rejoin] = MAIN_X

            rejoin_y = max(
                node_y[edge.target]
                for edge in success_edges
                if edge.target in node_y
            ) + MIN_VERTICAL_GAP

            if node_y.get(
                shared_rejoin,
                0
            ) < rejoin_y:

                delta = rejoin_y - node_y[shared_rejoin]

                for node_id in collect_forward_spacing_chain(
                    graph,
                    shared_rejoin
                ):

                    if node_id in node_y:

                        node_y[node_id] += delta


def enforce_review_branch_target_spacing(
    graph,
    node_x,
    node_y
):

    for source_id, source_node in graph.nodes.items():

        if source_node.type != "RESPONSE":

            continue

        if source_id not in node_x or source_id not in node_y:

            continue

        review_edges = [
            edge
            for edge in graph.adjacency_map.get(
                source_id,
                []
            )
            if (
                is_review_branch_edge(
                    graph,
                    edge
                )
                and edge.target in node_x
                and edge.target in node_y
            )
        ]

        if len(
            review_edges
        ) < 2:

            continue

        review_edges.sort(
            key=lambda edge: (
                node_y.get(
                    edge.target,
                    0
                ),
                node_x.get(
                    edge.target,
                    0
                )
            )
        )

        for index, edge in enumerate(
            review_edges
        ):

            target_id = edge.target

            minimum_target_y = (
                node_y[source_id]
                + (
                    index
                    * REVIEW_BRANCH_VERTICAL_GAP
                )
            )

            if node_y[target_id] >= minimum_target_y:

                continue

            delta = minimum_target_y - node_y[target_id]

            for node_id in collect_forward_spacing_chain(
                graph,
                target_id
            ):

                if node_id in node_y:

                    node_y[node_id] += delta


def is_local_retry_layout_edge(
    graph,
    edge,
    node_x,
    node_y
):

    if not is_loopback_edge(
        edge
    ):

        return False

    source = graph.get_node(
        edge.source
    )

    target = graph.get_node(
        edge.target
    )

    if not source or not target:

        return False

    if edge.source not in node_x or edge.target not in node_x:

        return False

    if edge.source not in node_y or edge.target not in node_y:

        return False

    if node_y[edge.target] >= node_y[edge.source]:

        return False

    if abs(
        node_x[edge.source] - node_x[edge.target]
    ) > SIDE_COLUMN_TOLERANCE:

        return False

    if source.group == "ERROR_HANDLING":

        return False

    return (
        source.type in [
            "SYSTEM_ACTIVITY",
            "MANUAL_ACTIVITY"
        ]
        and target.type in [
            "SYSTEM_CHECK",
            "SYSTEM_ACTIVITY",
            "MANUAL_ACTIVITY"
        ]
    )


def same_column_connected_nodes(
    graph,
    start_id,
    node_x,
    column_x
):

    queue = deque([
        start_id
    ])

    visited = set()

    while queue:

        node_id = queue.popleft()

        if node_id in visited:

            continue

        if node_x.get(
            node_id
        ) != column_x:

            continue

        visited.add(
            node_id
        )

        connected_edges = (
            graph.adjacency_map.get(
                node_id,
                []
            )
            + graph.reverse_adjacency_map.get(
                node_id,
                []
            )
        )

        for edge in connected_edges:

            if is_loopback_edge(
                edge
            ):

                continue

            other_id = (
                edge.target
                if edge.source == node_id
                else edge.source
            )

            if node_x.get(
                other_id
            ) != column_x:

                continue

            queue.append(
                other_id
            )

    return visited


def reserve_local_retry_corridors(
    graph,
    node_x,
    node_y
):

    for edge in graph.edges:

        if not is_local_retry_layout_edge(
            graph,
            edge,
            node_x,
            node_y
        ):

            continue

        source_x = node_x[edge.source]

        target_y = node_y[edge.target]

        source_y = node_y[edge.source]

        if source_x == MAIN_X:

            continue

        direction = (
            1
            if source_x < MAIN_X
            else -1
        )

        corridor_x = (
            source_x
            + (
                direction
                * LOCAL_RETRY_CORRIDOR_GAP
            )
        )

        interval_top = min(
            source_y,
            target_y
        )

        interval_bottom = max(
            source_y,
            target_y
        )

        blocked_columns = []

        for node_id, x in list(
            node_x.items()
        ):

            if node_id in [
                edge.source,
                edge.target
            ]:

                continue

            if node_id not in node_y:

                continue

            node = graph.get_node(
                node_id
            )

            if not node or node.type in [
                "MERGE",
                "CONNECTOR"
            ]:

                continue

            if not (
                interval_top <= node_y[node_id] <= interval_bottom
            ):

                continue

            if direction > 0:

                if not (
                    source_x < x <= corridor_x + LOCAL_RETRY_CORRIDOR_CLEARANCE
                ):

                    continue

            else:

                if not (
                    corridor_x - LOCAL_RETRY_CORRIDOR_CLEARANCE <= x < source_x
                ):

                    continue

            if x not in blocked_columns:

                blocked_columns.append(
                    x
                )

        for column_x in blocked_columns:

            if column_x == MAIN_X:

                continue

            new_x = (
                corridor_x
                + (
                    direction
                    * LOCAL_RETRY_CORRIDOR_CLEARANCE
                )
            )

            for node_id in list(
                node_x
            ):

                if node_x.get(
                    node_id
                ) != column_x:

                    continue

                if node_id not in node_y:

                    continue

                if not (
                    interval_top <= node_y[node_id] <= interval_bottom
                ):

                    continue

                component = same_column_connected_nodes(
                    graph,
                    node_id,
                    node_x,
                    column_x
                )

                for component_node_id in component:

                    node_x[component_node_id] = new_x


def resolve_node_position_collisions(
    graph,
    node_x,
    node_y
):

    ordered_nodes = sorted(
        [
            node_id
            for node_id in graph.nodes
            if (
                node_id in node_x
                and node_id in node_y
                and graph.get_node(node_id)
                and graph.get_node(node_id).type != "MERGE"
            )
        ],
        key=lambda node_id: (
            node_y.get(
                node_id,
                0
            ),
            layout_collision_priority(
                graph,
                node_id
            ),
            node_x.get(
                node_id,
                0
            )
        )
    )

    occupied = {}

    for node_id in ordered_nodes:

        node = graph.get_node(
            node_id
        )

        if not node:

            continue

        resolved = False

        if is_branch_position_node(
            graph,
            node_id
        ):

            for candidate_x in branch_x_candidates(
                graph,
                node_id,
                node_x
            ):

                if collision_with_occupied(
                    graph,
                    node_id,
                    candidate_x,
                    node_y[node_id],
                    occupied
                ):

                    continue

                node_x[node_id] = candidate_x

                resolved = True

                break

        if not resolved:

            collision = collision_with_occupied(
                graph,
                node_id,
                node_x[node_id],
                node_y[node_id],
                occupied
            )

            guard = 0

            while collision and guard < len(graph.nodes):

                guard += 1

                next_y = (
                    collision["bottom"]
                    + (
                        estimate_node_height(
                            node
                        ) / 2
                    )
                    + 34
                )

                delta = next_y - node_y[node_id]

                if delta <= 0:

                    delta = MIN_VERTICAL_GAP

                chain = collect_forward_spacing_chain(
                    graph,
                    node_id
                )

                if not chain:

                    chain = {
                        node_id
                    }

                for chain_node_id in chain:

                    if chain_node_id in node_y:

                        node_y[chain_node_id] += delta

                collision = collision_with_occupied(
                    graph,
                    node_id,
                    node_x[node_id],
                    node_y[node_id],
                    occupied
                )

        occupied[node_id] = node_collision_bounds(
            graph,
            node_id,
            node_x,
            node_y
        )


def calculate_global_return_bus_x(node_x):

    rightmost_x = MAIN_X

    if node_x:

        rightmost_x = max(
            node_x.values()
        )

    return max(
        GLOBAL_RETURN_BUS_X,
        rightmost_x + RETURN_BUS_GAP
    )


def choose_terminal_source(
    graph,
    node_id,
    node_x,
    node_y
):

    incoming = [
        edge
        for edge in graph.reverse_adjacency_map.get(
            node_id,
            []
        )
        if not is_loopback_edge(edge)
    ]

    candidates = []

    for edge in incoming:

        if edge.source not in node_y:

            continue

        candidates.append(
            (
                node_y[edge.source],
                node_x.get(
                    edge.source,
                    MAIN_X
                ),
                edge.source
            )
        )

    if not candidates:

        return MAIN_X, 0

    source_y, source_x, _ = max(
        candidates,
        key=lambda item: (
            item[0],
            item[1]
        )
    )

    return source_x, source_y


def position_end_nodes(
    graph,
    node_x,
    node_y
):

    for node_id, node in graph.nodes.items():

        if node.type != "END":

            continue

        source_x, source_y = choose_terminal_source(
            graph,
            node_id,
            node_x,
            node_y
        )

        node_x[node_id] = source_x

        node_y[node_id] = source_y + VERTICAL_GAP


def position_merge_nodes(
    graph,
    node_x,
    node_y,
    global_return_bus_x
):

    for node_id, node in graph.nodes.items():

        if node.type != "MERGE":

            continue

        incoming = [
            edge
            for edge in graph.reverse_adjacency_map.get(
                node_id,
                []
            )
            if edge.source in node_y
        ]

        if not incoming:

            node_x[node_id] = global_return_bus_x

            node_y[node_id] = 0

            continue

        lowest_source_y = max(
            node_y[edge.source]
            for edge in incoming
        )

        node_x[node_id] = global_return_bus_x

        node_y[node_id] = (
            lowest_source_y + VERTICAL_GAP
        )


def build_topology_layout(graph):

    node_x, node_y = build_forward_layout(
        graph
    )

    enforce_forward_spacing(
        graph,
        node_x,
        node_y
    )

    align_side_branch_targets(
        graph,
        node_x,
        node_y
    )

    align_rejoin_spine(
        graph,
        node_x,
        node_y
    )

    align_parallel_success_branch_targets(
        graph,
        node_x,
        node_y
    )

    enforce_review_branch_target_spacing(
        graph,
        node_x,
        node_y
    )

    align_side_success_rejoins(
        graph,
        node_x,
        node_y
    )

    align_direct_indirect_success_rejoins(
        graph,
        node_x,
        node_y
    )

    enforce_side_response_branch_visibility(
        graph,
        node_x,
        node_y
    )

    resolve_response_branch_side_crossovers(
        graph,
        node_x,
        node_y
    )

    reserve_local_retry_corridors(
        graph,
        node_x,
        node_y
    )

    enforce_response_branch_ownership(
        graph,
        node_x,
        node_y
    )

    align_same_source_retry_error_groups(
        graph,
        node_x,
        node_y
    )

    enforce_forward_spacing(
        graph,
        node_x,
        node_y
    )

    align_side_success_rejoins(
        graph,
        node_x,
        node_y
    )

    align_parallel_success_branch_targets(
        graph,
        node_x,
        node_y
    )

    enforce_review_branch_target_spacing(
        graph,
        node_x,
        node_y
    )

    align_direct_indirect_success_rejoins(
        graph,
        node_x,
        node_y
    )

    enforce_side_response_branch_visibility(
        graph,
        node_x,
        node_y
    )

    resolve_response_branch_side_crossovers(
        graph,
        node_x,
        node_y
    )

    reserve_local_retry_corridors(
        graph,
        node_x,
        node_y
    )

    enforce_response_branch_ownership(
        graph,
        node_x,
        node_y
    )

    align_same_source_retry_error_groups(
        graph,
        node_x,
        node_y
    )

    align_direct_indirect_success_rejoins(
        graph,
        node_x,
        node_y
    )

    enforce_side_response_branch_visibility(
        graph,
        node_x,
        node_y
    )

    align_parallel_success_branch_targets(
        graph,
        node_x,
        node_y
    )

    enforce_review_branch_target_spacing(
        graph,
        node_x,
        node_y
    )

    resolve_response_branch_side_crossovers(
        graph,
        node_x,
        node_y
    )

    reserve_local_retry_corridors(
        graph,
        node_x,
        node_y
    )

    resolve_node_position_collisions(
        graph,
        node_x,
        node_y
    )

    enforce_response_branch_ownership(
        graph,
        node_x,
        node_y
    )

    align_same_source_retry_error_groups(
        graph,
        node_x,
        node_y
    )

    align_direct_indirect_success_rejoins(
        graph,
        node_x,
        node_y
    )

    enforce_side_response_branch_visibility(
        graph,
        node_x,
        node_y
    )

    reserve_local_retry_corridors(
        graph,
        node_x,
        node_y
    )

    resolve_node_position_collisions(
        graph,
        node_x,
        node_y
    )

    align_same_source_retry_error_groups(
        graph,
        node_x,
        node_y
    )

    align_direct_indirect_success_rejoins(
        graph,
        node_x,
        node_y
    )

    reserve_local_retry_corridors(
        graph,
        node_x,
        node_y
    )

    enforce_response_branch_ownership(
        graph,
        node_x,
        node_y
    )

    global_return_bus_x = calculate_global_return_bus_x(
        node_x
    )

    position_merge_nodes(
        graph,
        node_x,
        node_y,
        global_return_bus_x
    )

    position_end_nodes(
        graph,
        node_x,
        node_y
    )

    node_positions = {}

    for node_id in graph.nodes:

        node_positions[node_id] = {

            "x": node_x.get(
                node_id,
                MAIN_X
            ),

            "y": node_y.get(
                node_id,
                0
            )
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
