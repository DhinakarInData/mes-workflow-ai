import argparse
import json
import math
from pathlib import Path


LOOP_ROUTING_TYPES = {
    "OUTER_LOOP",
    "RESTART_FLOW",
    "LOCAL_RETRY_LOOP",
    "BOTTOM_LOOP",
}


BRANCH_ROUTING_TYPES = {
    "RIGHT_EXTERNAL",
    "BUSINESS_BRANCH",
    "REVIEW_BRANCH",
    "SUCCESS_REJOIN",
    "TERMINAL_BRANCH",
    "DOWN",
}


MAINLIKE_TYPES = {
    "start",
    "manual_activity",
    "system_activity",
    "system_check",
    "response",
    "end",
}


MAX_REASONABLE_COORDINATE = 50000

MAX_REASONABLE_DIAGRAM_HEIGHT = 14000

MAX_REASONABLE_DIAGRAM_WIDTH = 3600


SUCCESS_ROUTES = {
    "DOWN",
    "VERTICAL",
    "SUCCESS_REJOIN",
}


TERMINAL_ROUTES = {
    "TERMINAL_BRANCH",
    "VERTICAL",
}


ERROR_BRANCH_ROUTES = {
    "RIGHT_EXTERNAL",
    "REVIEW_BRANCH",
}


def node_label(node):
    data = node.get(
        "data",
        {}
    )

    return (
        data.get("display_label")
        or data.get("label")
        or node.get("id")
    )


def routing_type(edge):
    data = edge.get(
        "data",
        {}
    )

    return (
        data.get("routing_type")
        or data.get("routingType")
        or data.get("route")
        or ""
    )


def edge_data(edge):
    return edge.get(
        "data",
        {}
    )


def edge_label(edge):
    data = edge.get(
        "data",
        {}
    )

    return (
        data.get("label")
        or edge.get("label")
        or ""
    )


def edge_routing_role(edge):
    data = edge.get(
        "data",
        {}
    )

    return (
        data.get("routing_role")
        or data.get("routingRole")
        or ""
    )


def normalize_label(value):
    return " ".join(
        (
            value
            or ""
        )
        .strip()
        .upper()
        .replace(
            "_",
            " "
        )
        .split()
    )


def is_failure_label(value):
    label = normalize_label(
        value
    )

    if not label:
        return False

    failure_terms = [
        "INVALID",
        "INCORRECT",
        "MISMATCH",
        "NOT",
        "FAIL",
        "FAILED",
        "ERROR",
        "DUE",
        "EXPIRED",
        "ABOVE",
        "BELOW",
        "OUT OF RANGE",
        "OUTSIDE RANGE",
        "REJECT",
        "SHORT",
        "EXCESS",
    ]

    return any(
        term in label
        for term in failure_terms
    )


def is_success_route(edge):
    return (
        routing_type(edge) in SUCCESS_ROUTES
        or edge_routing_role(edge) == "SUCCESS"
    )


def is_terminal_route(edge, nodes_by_id):
    target = nodes_by_id.get(
        edge.get("target")
    )

    return (
        routing_type(edge) in TERMINAL_ROUTES
        or (
            target
            and target.get("type") == "end"
        )
    )


def node_position(node):
    position = node.get(
        "position",
        {}
    )

    return (
        float(position.get("x", 0)),
        float(position.get("y", 0)),
    )


def is_finite_number(value):
    return isinstance(
        value,
        (
            int,
            float,
        )
    ) and math.isfinite(
        value
    )


def node_size(node):
    data = node.get(
        "data",
        {}
    )

    width = float(
        data.get(
            "width",
            220
        )
    )

    height = float(
        data.get(
            "height",
            100
        )
    )

    return width, height


def node_bounds(node, padding=0):
    x, y = node_position(
        node
    )

    width, height = node_size(
        node
    )

    return {
        "left": x - (width / 2) - padding,
        "right": x + (width / 2) + padding,
        "top": y - (height / 2) - padding,
        "bottom": y + (height / 2) + padding,
    }


def node_handle_position(node, handle_id):
    x, y = node_position(
        node
    )

    width, height = node_size(
        node
    )

    if handle_id in [
        "error",
        "return",
        "right",
    ]:
        return x + (width / 2), y

    if handle_id in [
        "restart",
        "loopback",
        "left",
    ]:
        return x - (width / 2), y

    if handle_id in [
        "success",
        "bottom",
    ]:
        return x, y + (height / 2)

    if handle_id in [
        "target",
        "top",
    ]:
        return x, y - (height / 2)

    return x, y


def edge_endpoint_position(edge, node, endpoint):
    handle_id = edge.get(
        "sourceHandle"
        if endpoint == "source"
        else "targetHandle"
    )

    return node_handle_position(
        node,
        handle_id
    )


def segment_intersects_bounds(x1, y1, x2, y2, bounds):
    if abs(y1 - y2) < 1:
        y = y1
        left = min(x1, x2)
        right = max(x1, x2)

        return (
            bounds["top"] <= y <= bounds["bottom"]
            and right >= bounds["left"]
            and left <= bounds["right"]
        )

    if abs(x1 - x2) < 1:
        x = x1
        top = min(y1, y2)
        bottom = max(y1, y2)

        return (
            bounds["left"] <= x <= bounds["right"]
            and bottom >= bounds["top"]
            and top <= bounds["bottom"]
        )

    return False


def bounds_overlap(first, second):
    return not (
        first["right"] < second["left"]
        or second["right"] < first["left"]
        or first["bottom"] < second["top"]
        or second["bottom"] < first["top"]
    )


def is_rendered_node(node):
    data = node.get(
        "data",
        {}
    )

    return not data.get(
        "hidden",
        False
    )


def is_main_candidate(node):
    node_type = node.get(
        "type",
        ""
    )

    data = node.get(
        "data",
        {}
    )

    if data.get(
        "is_error_activity"
    ):
        return False

    if data.get(
        "visual_type"
    ) == "LINKED_WORKFLOW":
        return False

    return node_type in MAINLIKE_TYPES


def build_maps(graph):
    nodes = {
        node.get("id"): node
        for node in graph.get(
            "nodes",
            []
        )
        if node.get("id")
    }

    outgoing = {}
    incoming = {}

    for edge in graph.get(
        "edges",
        []
    ):
        outgoing.setdefault(
            edge.get("source"),
            []
        ).append(edge)
        incoming.setdefault(
            edge.get("target"),
            []
        ).append(edge)

    return nodes, outgoing, incoming


def non_loop_incoming_count(incoming, node_id):
    return len(
        [
            edge
            for edge in incoming.get(
                node_id,
                []
            )
            if routing_type(edge) not in LOOP_ROUTING_TYPES
        ]
    )


def branch_target_node_ids(incoming):
    branch_routes = {
        "BUSINESS_BRANCH",
        "REVIEW_BRANCH",
        "RIGHT_EXTERNAL",
        "TERMINAL_BRANCH",
        "SUCCESS_REJOIN",
    }

    return {
        node_id
        for node_id, edges in incoming.items()
        if any(
            routing_type(edge) in branch_routes
            for edge in edges
        )
    }


def has_direct_main_success_owner(nodes, incoming, target_id, x_tolerance=80):
    target = nodes.get(
        target_id
    )

    if not target:
        return False

    target_x, target_y = node_position(
        target
    )

    for edge in incoming.get(
        target_id,
        []
    ):
        if routing_type(edge) in LOOP_ROUTING_TYPES:
            continue

        if edge_routing_role(edge) not in [
            "MAIN_FLOW",
            "SUCCESS",
            "LOCAL_CONTINUATION",
        ]:
            continue

        source = nodes.get(
            edge.get("source")
        )

        if not source or source.get("type") != "response":
            continue

        source_x, source_y = node_position(
            source
        )

        if abs(source_x - target_x) > x_tolerance:
            continue

        if target_y < source_y:
            continue

        return True

    return False


def parallel_success_branch_node_ids(nodes, outgoing, incoming):
    branch_nodes = set()

    branch_routing_types = {
        "DOWN",
        "VERTICAL",
        "SUCCESS_REJOIN",
    }

    roots = []

    for source_id, edges in outgoing.items():
        source = nodes.get(
            source_id
        )

        if not source or source.get("type") != "response":
            continue

        success_rejoin_edges = [
            edge
            for edge in edges
            if routing_type(edge) == "SUCCESS_REJOIN"
            and edge_routing_role(edge) == "SUCCESS"
        ]

        if len(success_rejoin_edges) < 2:
            continue

        roots.extend(
            edge.get("target")
            for edge in success_rejoin_edges
            if edge.get("target") in nodes
        )

    queue = list(
        roots
    )

    visited = set()

    while queue:
        node_id = queue.pop(0)

        if node_id in visited:
            continue

        visited.add(
            node_id
        )

        if (
            node_id not in roots
            and non_loop_incoming_count(
                incoming,
                node_id
            ) > 1
        ):
            continue

        branch_nodes.add(
            node_id
        )

        for edge in outgoing.get(
            node_id,
            []
        ):
            if routing_type(edge) not in branch_routing_types:
                continue

            target_id = edge.get("target")

            if target_id not in nodes:
                continue

            if (
                target_id not in roots
                and non_loop_incoming_count(
                    incoming,
                    target_id
                ) > 1
            ):
                continue

            queue.append(
                target_id
            )

    return branch_nodes


def safe_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def loop_lane_x(edge, source_x, source_y, target_x, target_y):
    data = edge_data(
        edge
    )

    route = routing_type(
        edge
    )

    if route == "LOCAL_RETRY_LOOP":
        side = data.get(
            "local_retry_side",
            "right"
        )
        span = abs(
            source_y - target_y
        )

        if side == "left":
            distance = (
                56
                if span <= 420
                else 260
            )

            return min(source_x, target_x) - distance

        distance = (
            56
            if span <= 420
            else 420
        )

        return max(source_x, target_x) + distance

    if route == "OUTER_LOOP":
        is_error_retry_return = (
            target_y < source_y
            and (
                data.get("source_type") == "SYSTEM_ACTIVITY"
                or data.get("collapsed_merge")
                or data.get("render_expanded_error")
                or source_x > target_x + 60
            )
        )

        if is_error_retry_return:
            lane_index = max(
                int(
                    safe_float(
                        data.get(
                            "outer_loop_bus_lane_index"
                        ),
                        1
                    )
                ),
                1
            )

            lane_step = 96

            if source_x < target_x:
                source_width = safe_float(
                    data.get(
                        "target_outer_loop_max_source_width"
                    ),
                    safe_float(
                        data.get(
                            "source_width"
                        ),
                        0
                    )
                )

                occupied_left = safe_float(
                    data.get(
                        "restart_left_occupied_left_x"
                    ),
                    float("inf")
                )

                return min(
                    source_x - source_width - 46
                    if source_width > 0
                    else source_x - 46,
                    min(
                        source_x,
                        target_x
                    ) - 46,
                    occupied_left
                ) - (
                    lane_step
                    * (
                        lane_index - 1
                    )
                )

            occupied_right = safe_float(
                data.get(
                    "restart_right_occupied_right_x"
                ),
                float("-inf")
            )

            return (
                max(
                    max(
                        source_x,
                        target_x
                    )
                    + 46,
                    occupied_right
                )
                + (
                    lane_step
                    * (
                        lane_index - 1
                    )
                )
            )

        return safe_float(
            data.get(
                "global_return_bus_x"
            ),
            2060
        )

    if route == "RESTART_FLOW":
        side = data.get(
            "restart_side",
            "left"
        )

        lane_index = max(
            int(
                safe_float(
                    data.get(
                        "restart_lane_index"
                    ),
                    1
                )
            ),
            1
        )

        vertical_distance = abs(
            source_y - target_y
        )

        same_column = abs(
            source_x - target_x
        ) < 80

        lane_distance = (
            260
            if (
                target_y < source_y
                and same_column
                and vertical_distance <= 520
            )
            else min(
                330,
                235 + (vertical_distance * 0.025)
            )
            if (
                target_y < source_y
                and same_column
                and vertical_distance > 520
            )
            else 145
        )

        if side == "right":
            occupied_right = safe_float(
                (
                    data.get(
                        "restart_right_reserved_x"
                    )
                    if data.get(
                        "restart_right_reserved_x"
                    )
                    is not None
                    else data.get(
                        "restart_right_occupied_right_x"
                    )
                ),
                float("-inf")
            )

            return max(
                max(source_x, target_x) + lane_distance + ((lane_index - 1) * 132),
                occupied_right + 132 + ((lane_index - 1) * 132)
            )

        return min(
            source_x,
            target_x
        ) - lane_distance

    return None


def is_error_retry_return(edge, source_x, source_y, target_x, target_y):
    data = edge_data(
        edge
    )

    return (
        routing_type(edge) == "OUTER_LOOP"
        and target_y < source_y
        and (
            data.get("source_type") == "SYSTEM_ACTIVITY"
            or data.get("collapsed_merge")
            or data.get("render_expanded_error")
            or source_x > target_x + 60
            or source_x < target_x - 60
        )
    )


def draws_shared_retry_bus(edge, source_x, source_y, target_x, target_y):
    data = edge_data(
        edge
    )

    if not is_error_retry_return(
        edge,
        source_x,
        source_y,
        target_x,
        target_y
    ):
        return True

    target_outer_loop_count = int(
        safe_float(
            data.get(
                "target_outer_loop_count"
            ),
            0
        )
    )

    target_outer_loop_max_source_y = safe_float(
        data.get(
            "target_outer_loop_max_source_y"
        ),
        source_y
    )

    return (
        target_outer_loop_count <= 1
        or abs(
            source_y - target_outer_loop_max_source_y
        ) < 2
    )


def clear_loop_lane_x(edge, nodes_by_id, lane_x, source_y, target_y):
    direction = (
        1
        if lane_x > edge_endpoint_position(
            edge,
            nodes_by_id.get(
                edge.get("source")
            ),
            "source"
        )[0]
        else -1
    )

    lane_top = min(
        source_y,
        target_y
    )

    lane_bottom = max(
        source_y,
        target_y
    )

    cleared_lane_x = lane_x

    for node_id, node in nodes_by_id.items():
        if node_id in [
            edge.get("source"),
            edge.get("target")
        ]:
            continue

        if not is_rendered_node(
            node
        ):
            continue

        bounds = node_bounds(
            node,
            padding=28
        )

        overlaps_y = not (
            lane_bottom < bounds["top"]
            or lane_top > bounds["bottom"]
        )

        if not overlaps_y:
            continue

        if not (
            bounds["left"] <= cleared_lane_x <= bounds["right"]
        ):
            continue

        cleared_lane_x = (
            bounds["right"] + 28
            if direction > 0
            else bounds["left"] - 28
        )

    return cleared_lane_x


def loop_edge_segments(edge, nodes_by_id):
    source = nodes_by_id.get(
        edge.get("source")
    )

    target = nodes_by_id.get(
        edge.get("target")
    )

    if not source or not target:
        return []

    source_x, source_y = edge_endpoint_position(
        edge,
        source,
        "source"
    )

    target_x, target_y = edge_endpoint_position(
        edge,
        target,
        "target"
    )

    lane_x = loop_lane_x(
        edge,
        source_x,
        source_y,
        target_x,
        target_y
    )

    if lane_x is None:
        return []

    if routing_type(edge) in [
        "OUTER_LOOP",
        "LOCAL_RETRY_LOOP"
    ]:
        lane_x = clear_loop_lane_x(
            edge,
            nodes_by_id,
            lane_x,
            source_y,
            target_y
        )

    if not draws_shared_retry_bus(
        edge,
        source_x,
        source_y,
        target_x,
        target_y
    ):
        return [
            (source_x, source_y, lane_x, source_y),
        ]

    return [
        (source_x, source_y, lane_x, source_y),
        (lane_x, source_y, lane_x, target_y),
        (lane_x, target_y, target_x, target_y),
    ]


def loop_interval(edge, nodes_by_id):
    source = nodes_by_id.get(
        edge.get("source")
    )

    target = nodes_by_id.get(
        edge.get("target")
    )

    if not source or not target:
        return None

    source_x, source_y = edge_endpoint_position(
        edge,
        source,
        "source"
    )

    target_x, target_y = edge_endpoint_position(
        edge,
        target,
        "target"
    )

    lane_x = loop_lane_x(
        edge,
        source_x,
        source_y,
        target_x,
        target_y
    )

    if lane_x is None:
        return None

    if routing_type(edge) in [
        "OUTER_LOOP",
        "LOCAL_RETRY_LOOP"
    ]:
        lane_x = clear_loop_lane_x(
            edge,
            nodes_by_id,
            lane_x,
            source_y,
            target_y
        )

    if not draws_shared_retry_bus(
        edge,
        source_x,
        source_y,
        target_x,
        target_y
    ):
        return None

    return {
        "edge": edge,
        "lane_x": lane_x,
        "top": min(source_y, target_y),
        "bottom": max(source_y, target_y),
        "route": routing_type(edge),
    }


def validate_edge_endpoints(graph):
    nodes, _, _ = build_maps(
        graph
    )

    violations = []

    for edge in graph.get(
        "edges",
        []
    ):
        source = edge.get(
            "source"
        )
        target = edge.get(
            "target"
        )

        if source not in nodes:
            violations.append(
                {
                    "rule": "edge_endpoint_exists",
                    "severity": "error",
                    "message": f"Edge source {source} is missing",
                    "edge": {
                        "source": source,
                        "target": target,
                    },
                }
            )

        if target not in nodes:
            violations.append(
                {
                    "rule": "edge_endpoint_exists",
                    "severity": "error",
                    "message": f"Edge target {target} is missing",
                    "edge": {
                        "source": source,
                        "target": target,
                    },
                }
            )

    return violations


def validate_unique_ids(graph):
    violations = []

    seen_node_ids = set()

    for node in graph.get(
        "nodes",
        []
    ):
        node_id = node.get(
            "id"
        )

        if not node_id:
            violations.append(
                {
                    "rule": "node_id_present",
                    "severity": "error",
                    "message": "A node is missing its id",
                    "node": node,
                }
            )
            continue

        if node_id in seen_node_ids:
            violations.append(
                {
                    "rule": "unique_node_id",
                    "severity": "error",
                    "message": f"Duplicate node id {node_id}",
                    "node": node_id,
                }
            )

        seen_node_ids.add(
            node_id
        )

    seen_edge_ids = set()

    for edge in graph.get(
        "edges",
        []
    ):
        edge_id = edge.get(
            "id"
        )

        if not edge_id:
            continue

        if edge_id in seen_edge_ids:
            violations.append(
                {
                    "rule": "unique_edge_id",
                    "severity": "error",
                    "message": f"Duplicate edge id {edge_id}",
                    "edge": {
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                    },
                }
            )

        seen_edge_ids.add(
            edge_id
        )

    return violations


def validate_node_positions(graph):
    violations = []

    for node in graph.get(
        "nodes",
        []
    ):
        if not is_rendered_node(
            node
        ):
            continue

        position = node.get(
            "position",
            {}
        )

        try:
            x = float(
                position.get(
                    "x"
                )
            )
            y = float(
                position.get(
                    "y"
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            violations.append(
                {
                    "rule": "finite_node_position",
                    "severity": "error",
                    "message": f"{node.get('id')} has non-numeric position",
                    "node": {
                        "id": node.get("id"),
                        "position": position,
                    },
                }
            )
            continue

        if not (
            is_finite_number(
                x
            )
            and is_finite_number(
                y
            )
        ):
            violations.append(
                {
                    "rule": "finite_node_position",
                    "severity": "error",
                    "message": f"{node.get('id')} has NaN or infinite position",
                    "node": {
                        "id": node.get("id"),
                        "position": position,
                    },
                }
            )
            continue

        if (
            abs(
                x
            ) > MAX_REASONABLE_COORDINATE
            or abs(
                y
            ) > MAX_REASONABLE_COORDINATE
        ):
            violations.append(
                {
                    "rule": "reasonable_node_position",
                    "severity": "error",
                    "message": (
                        f"{node.get('id')} position is outside the "
                        "reasonable layout range"
                    ),
                    "node": {
                        "id": node.get("id"),
                        "label": node_label(node),
                        "x": x,
                        "y": y,
                    },
                }
            )

    return violations


def validate_no_rendered_merge_nodes(graph):
    violations = []

    for node in graph.get(
        "nodes",
        []
    ):
        if not is_rendered_node(
            node
        ):
            continue

        node_type = (
            node.get(
                "type",
                ""
            )
            or ""
        ).lower()

        if node_type != "merge":
            continue

        violations.append(
            {
                "rule": "merge_nodes_hidden",
                "severity": "error",
                "message": f"MERGE node {node.get('id')} is rendered",
                "node": node.get(
                    "id"
                ),
            }
        )

    return violations


def validate_node_overlaps(graph, padding=12):
    nodes = [
        node
        for node in graph.get(
            "nodes",
            []
        )
        if is_rendered_node(
            node
        )
    ]

    violations = []

    for first_index, first_node in enumerate(
        nodes
    ):
        first_bounds = node_bounds(
            first_node,
            padding
        )

        for second_node in nodes[
            first_index + 1:
        ]:
            second_bounds = node_bounds(
                second_node,
                padding
            )

            if not bounds_overlap(
                first_bounds,
                second_bounds
            ):
                continue

            violations.append(
                {
                    "rule": "no_node_overlap",
                    "severity": "error",
                    "message": (
                        f"{first_node.get('id')} overlaps "
                        f"{second_node.get('id')}"
                    ),
                    "nodes": [
                        first_node.get("id"),
                        second_node.get("id"),
                    ],
                }
            )

    return violations


def validate_forward_branches_do_not_go_up(graph, tolerance=40):
    nodes, _, incoming = build_maps(
        graph
    )

    violations = []

    for edge in graph.get(
        "edges",
        []
    ):
        route = routing_type(
            edge
        )

        if route not in BRANCH_ROUTING_TYPES:
            continue

        source = nodes.get(
            edge.get("source")
        )
        target = nodes.get(
            edge.get("target")
        )

        if not source or not target:
            continue

        if source.get("type") != "response":
            continue

        if (
            route == "SUCCESS_REJOIN"
            and has_direct_main_success_owner(
                nodes,
                incoming,
                edge.get("target")
            )
        ):
            continue

        source_x, source_y = node_position(
            source
        )
        target_x, target_y = node_position(
            target
        )

        if target_y >= source_y - tolerance:
            continue

        violations.append(
            {
                "rule": "forward_branch_not_above_response",
                "severity": "error",
                "message": (
                    f"{edge.get('source')} -> {edge.get('target')} "
                    f"({edge_label(edge) or route}) places branch target "
                    "above its response source"
                ),
                "edge": {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "label": edge_label(edge),
                    "routing_type": route,
                    "source_y": source_y,
                    "target_y": target_y,
                    "source_x": source_x,
                    "target_x": target_x,
                },
            }
        )

    return violations


def is_loop_route(edge):
    return routing_type(
        edge
    ) in LOOP_ROUTING_TYPES


def is_forward_route(edge):
    route = routing_type(
        edge
    )

    if route in LOOP_ROUTING_TYPES:
        return False

    data = edge_data(
        edge
    )

    role = edge_routing_role(
        edge
    )

    edge_type = (
        data.get(
            "edge_type"
        )
        or ""
    )

    return (
        role in [
            "MAIN_FLOW",
            "SUCCESS",
            "LOCAL_CONTINUATION",
        ]
        or edge_type in [
            "SEQUENCE",
        ]
        or route in [
            "DOWN",
            "VERTICAL",
            "SUCCESS_REJOIN",
            "BUSINESS_BRANCH",
            "TERMINAL_BRANCH",
            "REVIEW_BRANCH",
            "RIGHT_EXTERNAL",
        ]
    )


def validate_forward_edges_are_monotonic(graph, tolerance=60):
    nodes, _, incoming = build_maps(
        graph
    )

    violations = []

    for edge in graph.get(
        "edges",
        []
    ):
        if not is_forward_route(
            edge
        ):
            continue

        source = nodes.get(
            edge.get("source")
        )
        target = nodes.get(
            edge.get("target")
        )

        if not source or not target:
            continue

        if (
            routing_type(edge) == "SUCCESS_REJOIN"
            and has_direct_main_success_owner(
                nodes,
                incoming,
                edge.get("target")
            )
        ):
            continue

        source_y = node_position(
            source
        )[1]
        target_y = node_position(
            target
        )[1]

        if (
            not math.isfinite(source_y)
            or not math.isfinite(target_y)
        ):
            continue

        if target_y + tolerance >= source_y:
            continue

        violations.append(
            {
                "rule": "forward_edge_monotonic_y",
                "severity": "error",
                "message": (
                    f"{edge.get('source')} -> {edge.get('target')} "
                    "is a forward route but target is above source"
                ),
                "edge": {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "label": edge_label(edge),
                    "routing_type": routing_type(edge),
                    "source_y": source_y,
                    "target_y": target_y,
                },
            }
        )

    return violations


def validate_loop_edges_are_backward_or_side_return(graph, tolerance=40):
    nodes, _, _ = build_maps(
        graph
    )

    violations = []

    for edge in graph.get(
        "edges",
        []
    ):
        if not is_loop_route(
            edge
        ):
            continue

        source = nodes.get(
            edge.get("source")
        )
        target = nodes.get(
            edge.get("target")
        )

        if not source or not target:
            continue

        source_y = node_position(
            source
        )[1]
        target_y = node_position(
            target
        )[1]

        if (
            not math.isfinite(source_y)
            or not math.isfinite(target_y)
        ):
            continue

        if target_y <= source_y + tolerance:
            continue

        violations.append(
            {
                "rule": "loopback_target_not_below_source",
                "severity": "warning",
                "message": (
                    f"{edge.get('source')} -> {edge.get('target')} "
                    "is a loop route but target is below source"
                ),
                "edge": {
                    "source": edge.get("source"),
                    "target": edge.get("target"),
                    "label": edge_label(edge),
                    "routing_type": routing_type(edge),
                    "source_y": source_y,
                    "target_y": target_y,
                },
            }
        )

    return violations


def validate_response_option_coverage(graph):
    nodes, outgoing, _ = build_maps(
        graph
    )

    violations = []

    for node_id, node in nodes.items():
        if node.get("type") != "response":
            continue

        edges = outgoing.get(
            node_id,
            []
        )

        if not edges:
            violations.append(
                {
                    "rule": "response_has_options",
                    "severity": "error",
                    "message": f"Response node {node_id} has no outgoing options",
                    "node": {
                        "id": node_id,
                        "label": node_label(node),
                    },
                }
            )
            continue

        option_edges = [
            edge
            for edge in edges
            if routing_type(edge) != "CONNECTOR_STUB"
        ]

        if not option_edges:
            continue

        labels = []

        for edge in option_edges:
            label = normalize_label(
                edge_label(edge)
            )

            if not label and len(option_edges) > 1:
                violations.append(
                    {
                        "rule": "response_option_label_present",
                        "severity": "error",
                        "message": (
                            f"Response option {edge.get('source')} -> "
                            f"{edge.get('target')} is missing a label"
                        ),
                        "edge": {
                            "source": edge.get("source"),
                            "target": edge.get("target"),
                            "routing_type": routing_type(edge),
                        },
                    }
                )

            if label:
                labels.append(
                    label
                )

        duplicates = sorted(
            {
                label
                for label in labels
                if labels.count(label) > 1
            }
        )

        for label in duplicates:
            violations.append(
                {
                    "rule": "response_option_label_unique",
                    "severity": "error",
                    "message": (
                        f"Response node {node_id} has duplicate option "
                        f"label {label}"
                    ),
                    "node": node_id,
                }
            )

        has_success_or_terminal = any(
            is_success_route(
                edge
            )
            or is_terminal_route(
                edge,
                nodes
            )
            for edge in option_edges
        )

        has_only_loops = all(
            routing_type(edge) in LOOP_ROUTING_TYPES
            for edge in option_edges
        )

        if not has_success_or_terminal and not has_only_loops:
            violations.append(
                {
                    "rule": "response_has_continuation_or_terminal",
                    "severity": "warning",
                    "message": (
                        f"Response node {node_id} has no clear success "
                        "or terminal option"
                    ),
                    "node": node_id,
                }
            )

    return violations


def validate_error_branch_groups(graph, x_tolerance=120):
    nodes, outgoing, _ = build_maps(
        graph
    )

    violations = []

    for source_id, edges in outgoing.items():
        error_edges = [
            edge
            for edge in edges
            if routing_type(edge) == "RIGHT_EXTERNAL"
        ]

        if len(error_edges) < 2:
            continue

        target_nodes = [
            nodes.get(
                edge.get("target")
            )
            for edge in error_edges
        ]
        target_nodes = [
            node
            for node in target_nodes
            if node
        ]

        if len(target_nodes) < 2:
            continue

        xs = [
            node_position(node)[0]
            for node in target_nodes
        ]

        if max(xs) - min(xs) <= x_tolerance:
            continue

        violations.append(
            {
                "rule": "same_source_error_branch_column",
                "severity": "warning",
                "message": (
                    f"Error branches from {source_id} are spread "
                    "across multiple columns"
                ),
                "source": source_id,
                "targets": [
                    node.get("id")
                    for node in target_nodes
                ],
                "x_values": xs,
            }
        )

    return violations


def validate_response_branch_section_ownership(graph, max_branch_span=1800):
    nodes, outgoing, _ = build_maps(
        graph
    )

    violations = []

    for source_id, edges in outgoing.items():
        source = nodes.get(
            source_id
        )

        if not source or source.get("type") != "response":
            continue

        source_y = node_position(
            source
        )[1]

        if not math.isfinite(
            source_y
        ):
            continue

        for edge in edges:
            route = routing_type(
                edge
            )

            if route in LOOP_ROUTING_TYPES:
                continue

            if route not in BRANCH_ROUTING_TYPES and route != "VERTICAL":
                continue

            target = nodes.get(
                edge.get("target")
            )

            if not target:
                continue

            if target.get("type") == "end":
                continue

            target_y = node_position(
                target
            )[1]

            if not math.isfinite(
                target_y
            ):
                continue

            if abs(
                target_y - source_y
            ) <= max_branch_span:
                continue

            violations.append(
                {
                    "rule": "response_branch_section_ownership",
                    "severity": "error",
                    "message": (
                        f"Response branch {source_id} -> {edge.get('target')} "
                        "escapes its local branch section"
                    ),
                    "edge": {
                        "source": source_id,
                        "target": edge.get("target"),
                        "label": edge_label(edge),
                        "routing_type": route,
                        "source_y": source_y,
                        "target_y": target_y,
                    },
                }
            )

    return violations


def can_reach_loop_or_terminal(nodes, outgoing, start_id, max_depth=6):
    visited = set()
    queue = [
        (
            start_id,
            0,
        )
    ]

    while queue:
        node_id, depth = queue.pop(0)

        if node_id in visited:
            continue

        visited.add(
            node_id
        )

        if depth > max_depth:
            continue

        for edge in outgoing.get(
            node_id,
            []
        ):
            if routing_type(edge) in LOOP_ROUTING_TYPES:
                return True

            target = nodes.get(
                edge.get("target")
            )

            if target and target.get("type") == "end":
                return True

            if not target:
                continue

            queue.append(
                (
                    edge.get("target"),
                    depth + 1,
                )
            )

    return False


def validate_error_branch_return_completeness(graph):
    nodes, outgoing, _ = build_maps(
        graph
    )

    violations = []

    for edge in graph.get(
        "edges",
        []
    ):
        if routing_type(edge) not in ERROR_BRANCH_ROUTES:
            continue

        label = edge_label(
            edge
        )

        if not is_failure_label(
            label
        ):
            continue

        target_id = edge.get(
            "target"
        )

        target = nodes.get(
            target_id
        )

        if not target:
            continue

        target_outgoing = outgoing.get(
            target_id,
            []
        )

        if not target_outgoing:
            violations.append(
                {
                    "rule": "error_branch_has_return_or_terminal",
                    "severity": "error",
                    "message": (
                        f"Error branch target {target_id} has no outgoing "
                        "return, continuation, or terminal route"
                    ),
                    "edge": {
                        "source": edge.get("source"),
                        "target": target_id,
                        "label": label,
                        "routing_type": routing_type(edge),
                    },
                }
            )
            continue

        if can_reach_loop_or_terminal(
            nodes,
            outgoing,
            target_id
        ):
            continue

        if any(
            is_success_route(
                outgoing_edge
            )
            for outgoing_edge in target_outgoing
        ):
            continue

        violations.append(
            {
                "rule": "error_branch_has_return_or_terminal",
                "severity": "warning",
                "message": (
                    f"Error branch target {target_id} does not clearly "
                    "return, terminate, or rejoin"
                ),
                "edge": {
                    "source": edge.get("source"),
                    "target": target_id,
                    "label": label,
                    "routing_type": routing_type(edge),
                },
            }
        )

    return violations


def validate_main_spine_stability(graph, tolerance=180):
    nodes_by_id, outgoing, incoming = build_maps(
        graph
    )

    parallel_branch_nodes = parallel_success_branch_node_ids(
        nodes_by_id,
        outgoing,
        incoming
    )

    explicit_branch_targets = branch_target_node_ids(
        incoming
    )

    candidate_ids = [
        node_id
        for node_id, node in nodes_by_id.items()
        if is_rendered_node(node)
        and is_main_candidate(node)
        and node_id not in parallel_branch_nodes
        and node_id not in explicit_branch_targets
    ]

    x_counts = {}

    for node_id in candidate_ids:
        x, _ = node_position(
            nodes_by_id[node_id]
        )
        rounded_x = round(
            x / 20
        ) * 20
        x_counts[rounded_x] = x_counts.get(
            rounded_x,
            0
        ) + 1

    if not x_counts:
        return []

    start_x = next(
        (
            node_position(
                node
            )[0]
            for node in nodes_by_id.values()
            if node.get("type") == "start"
            or node.get("type") == "START"
        ),
        None
    )

    dominant_x = (
        round(
            start_x / 20
        ) * 20
        if start_x is not None
        else max(
            x_counts,
            key=x_counts.get
        )
    )

    nodes = [
        nodes_by_id[node_id]
        for node_id in candidate_ids
        if abs(
            node_position(
                nodes_by_id[node_id]
            )[0] - dominant_x
        ) <= tolerance
    ]

    if len(nodes) < 4:
        return []

    median_x = dominant_x

    outliers = []

    for node_id in candidate_ids:
        node = nodes_by_id[
            node_id
        ]
        x, _ = node_position(node)

        if abs(x - median_x) > tolerance:
            outliers.append(
                {
                    "id": node_id,
                    "label": node_label(node),
                    "x": x,
                }
            )

    if len(outliers) <= max(
        2,
        len(candidate_ids) * 0.35
    ):
        return []

    if not outliers:
        return []

    return [
        {
            "rule": "main_spine_stability",
            "severity": "warning",
            "message": (
                "Many main-like nodes drift away from the dominant spine"
            ),
            "median_x": median_x,
            "outliers": outliers,
        }
    ]


def validate_main_spine_y_gaps(graph, max_gap=1400):
    nodes_by_id, outgoing, incoming = build_maps(
        graph
    )

    parallel_branch_nodes = parallel_success_branch_node_ids(
        nodes_by_id,
        outgoing,
        incoming
    )

    main_nodes = []

    for node_id, node in nodes_by_id.items():
        if not is_rendered_node(
            node
        ):
            continue

        if not is_main_candidate(
            node
        ):
            continue

        if node_id in parallel_branch_nodes:
            continue

        x, y = node_position(
            node
        )

        if not (
            math.isfinite(
                x
            )
            and math.isfinite(
                y
            )
        ):
            continue

        main_nodes.append(
            {
                "id": node_id,
                "label": node_label(node),
                "x": x,
                "y": y,
            }
        )

    if len(
        main_nodes
    ) < 3:
        return []

    x_counts = {}

    for node in main_nodes:
        rounded_x = round(
            node["x"] / 20
        ) * 20
        x_counts[rounded_x] = x_counts.get(
            rounded_x,
            0
        ) + 1

    dominant_x = max(
        x_counts,
        key=x_counts.get
    )

    spine_nodes = sorted(
        [
            node
            for node in main_nodes
            if abs(
                node["x"] - dominant_x
            ) <= 180
        ],
        key=lambda item: item["y"]
    )

    violations = []

    for first, second in zip(
        spine_nodes,
        spine_nodes[1:]
    ):
        gap = second["y"] - first["y"]

        if gap <= max_gap:
            continue

        violations.append(
            {
                "rule": "main_spine_y_gap",
                "severity": "error",
                "message": (
                    f"Main spine has an excessive vertical gap between "
                    f"{first['id']} and {second['id']}"
                ),
                "nodes": [
                    first["id"],
                    second["id"],
                ],
                "gap": gap,
            }
        )

    return violations


def validate_diagram_extent_budget(graph):
    nodes = [
        node
        for node in graph.get(
            "nodes",
            []
        )
        if is_rendered_node(
            node
        )
    ]

    finite_bounds = []

    for node in nodes:
        x, y = node_position(
            node
        )

        if not (
            math.isfinite(
                x
            )
            and math.isfinite(
                y
            )
        ):
            continue

        finite_bounds.append(
            node_bounds(
                node
            )
        )

    if not finite_bounds:
        return []

    left = min(
        bounds["left"]
        for bounds in finite_bounds
    )
    right = max(
        bounds["right"]
        for bounds in finite_bounds
    )
    top = min(
        bounds["top"]
        for bounds in finite_bounds
    )
    bottom = max(
        bounds["bottom"]
        for bounds in finite_bounds
    )

    width = right - left
    height = bottom - top

    violations = []

    if width > MAX_REASONABLE_DIAGRAM_WIDTH:
        violations.append(
            {
                "rule": "diagram_width_budget",
                "severity": "warning",
                "message": (
                    "Diagram width exceeds the current FDS review budget"
                ),
                "width": width,
            }
        )

    if height > MAX_REASONABLE_DIAGRAM_HEIGHT:
        violations.append(
            {
                "rule": "diagram_height_budget",
                "severity": "error",
                "message": (
                    "Diagram height exceeds the current FDS review budget"
                ),
                "height": height,
            }
        )

    return violations


def segments_cross(first, second):
    x1, y1, x2, y2 = first
    x3, y3, x4, y4 = second

    first_horizontal = abs(
        y1 - y2
    ) < 1
    second_horizontal = abs(
        y3 - y4
    ) < 1

    if first_horizontal == second_horizontal:
        return False

    if first_horizontal:
        horizontal = first
        vertical = second
    else:
        horizontal = second
        vertical = first

    hx1, hy, hx2, _ = horizontal
    vx, vy1, _, vy2 = vertical

    return (
        min(hx1, hx2) < vx < max(hx1, hx2)
        and min(vy1, vy2) < hy < max(vy1, vy2)
    )


def validate_loopback_crossing_density(graph, max_crossings=12):
    nodes_by_id, _, _ = build_maps(
        graph
    )

    loop_edges = [
        edge
        for edge in graph.get(
            "edges",
            []
        )
        if routing_type(edge) in LOOP_ROUTING_TYPES
    ]

    edge_segments = []

    for edge in loop_edges:
        segments = loop_edge_segments(
            edge,
            nodes_by_id
        )

        if not segments:
            continue

        edge_segments.append(
            {
                "edge": edge,
                "segments": segments,
            }
        )

    crossings = 0

    for index, first in enumerate(
        edge_segments
    ):
        for second in edge_segments[index + 1:]:
            if (
                first["edge"].get("target")
                == second["edge"].get("target")
                and edge_data(first["edge"]).get("outer_loop_bus_group")
                == edge_data(second["edge"]).get("outer_loop_bus_group")
            ):
                continue

            for first_segment in first["segments"]:
                for second_segment in second["segments"]:
                    if segments_cross(
                        first_segment,
                        second_segment
                    ):
                        crossings += 1

    if crossings <= max_crossings:
        return []

    return [
        {
            "rule": "loopback_crossing_density",
            "severity": "warning",
            "message": (
                "Loopback routes have high crossing density"
            ),
            "crossings": crossings,
        }
    ]


def validate_loopback_lane_stability(graph):
    nodes_by_id, _, _ = build_maps(
        graph
    )

    loop_edges = [
        edge
        for edge in graph.get(
            "edges",
            []
        )
        if routing_type(edge) in LOOP_ROUTING_TYPES
    ]

    violations = []
    intervals = [
        interval
        for interval in (
            loop_interval(
                edge,
                nodes_by_id
            )
            for edge in loop_edges
        )
        if interval
    ]

    for index, first in enumerate(
        intervals
    ):
        first_edge = first["edge"]

        for second in intervals[index + 1:]:
            second_edge = second["edge"]

            vertical_overlap = min(
                first["bottom"],
                second["bottom"]
            ) - max(
                first["top"],
                second["top"]
            )

            if vertical_overlap <= 80:
                continue

            first_data = edge_data(
                first_edge
            )

            second_data = edge_data(
                second_edge
            )

            same_shared_retry_bus = (
                first["route"] == "OUTER_LOOP"
                and second["route"] == "OUTER_LOOP"
                and first_edge.get("target") == second_edge.get("target")
                and (
                    first_data.get("virtual_merge_id")
                    and first_data.get("virtual_merge_id")
                    == second_data.get("virtual_merge_id")
                    or (
                        first_data.get("collapsed_merge")
                        and second_data.get("collapsed_merge")
                    )
                )
            )

            if same_shared_retry_bus:
                continue

            if abs(
                first["lane_x"] - second["lane_x"]
            ) >= 52:
                continue

            violations.append(
                {
                    "rule": "loopback_lane_spacing",
                    "severity": "warning",
                    "message": "Loopback lanes are visually too close over the same vertical interval",
                    "edges": [
                        {
                            "source": first_edge.get("source"),
                            "target": first_edge.get("target"),
                            "routing_type": first["route"],
                            "lane_x": first["lane_x"],
                        },
                        {
                            "source": second_edge.get("source"),
                            "target": second_edge.get("target"),
                            "routing_type": second["route"],
                            "lane_x": second["lane_x"],
                        },
                    ],
                    "vertical_overlap": vertical_overlap,
                }
            )

    for edge in loop_edges:
        segments = loop_edge_segments(
            edge,
            nodes_by_id
        )

        if not segments:
            continue

        for node_id, node in nodes_by_id.items():
            if node_id in [
                edge.get("source"),
                edge.get("target"),
            ]:
                continue

            if not is_rendered_node(
                node
            ):
                continue

            bounds = node_bounds(
                node,
                padding=10
            )

            if not any(
                segment_intersects_bounds(
                    *segment,
                    bounds
                )
                for segment in segments
            ):
                continue

            violations.append(
                {
                    "rule": "loopback_crosses_node",
                    "severity": "warning",
                    "message": "Loopback route crosses a rendered node",
                    "edge": {
                        "source": edge.get("source"),
                        "target": edge.get("target"),
                        "routing_type": routing_type(edge),
                    },
                    "node": {
                        "id": node_id,
                        "label": node_label(node),
                    },
                }
            )

    return violations


def validate_outer_loop_bus_group_isolation(graph):
    nodes_by_id, _, _ = build_maps(
        graph
    )

    intervals = [
        interval
        for interval in (
            loop_interval(
                edge,
                nodes_by_id
            )
            for edge in graph.get(
                "edges",
                []
            )
            if routing_type(edge) == "OUTER_LOOP"
        )
        if interval
    ]

    violations = []

    for index, first in enumerate(
        intervals
    ):
        first_edge = first["edge"]
        first_data = edge_data(
            first_edge
        )
        first_group = first_data.get(
            "outer_loop_bus_group"
        )

        for second in intervals[index + 1:]:
            second_edge = second["edge"]

            if first_edge.get("target") != second_edge.get("target"):
                continue

            second_data = edge_data(
                second_edge
            )
            second_group = second_data.get(
                "outer_loop_bus_group"
            )

            if not first_group or not second_group:
                continue

            if first_group == second_group:
                continue

            vertical_overlap = min(
                first["bottom"],
                second["bottom"]
            ) - max(
                first["top"],
                second["top"]
            )

            if vertical_overlap <= 80:
                continue

            if abs(
                first["lane_x"] - second["lane_x"]
            ) >= 52:
                continue

            violations.append(
                {
                    "rule": "outer_loop_bus_group_isolation",
                    "severity": "error",
                    "message": (
                        "Different response-owned loopback groups share "
                        "the same return bus lane"
                    ),
                    "edges": [
                        {
                            "source": first_edge.get("source"),
                            "target": first_edge.get("target"),
                            "routing_type": routing_type(first_edge),
                            "bus_group": first_group,
                            "lane_x": first["lane_x"],
                        },
                        {
                            "source": second_edge.get("source"),
                            "target": second_edge.get("target"),
                            "routing_type": routing_type(second_edge),
                            "bus_group": second_group,
                            "lane_x": second["lane_x"],
                        },
                    ],
                    "vertical_overlap": vertical_overlap,
                }
            )

    return violations


def validate_reactflow_graph(graph):
    violations = []

    validators = [
        validate_unique_ids,
        validate_node_positions,
        validate_no_rendered_merge_nodes,
        validate_edge_endpoints,
        validate_node_overlaps,
        validate_forward_edges_are_monotonic,
        validate_forward_branches_do_not_go_up,
        validate_loop_edges_are_backward_or_side_return,
        validate_response_option_coverage,
        validate_error_branch_groups,
        validate_response_branch_section_ownership,
        validate_error_branch_return_completeness,
        validate_main_spine_stability,
        validate_main_spine_y_gaps,
        validate_diagram_extent_budget,
        validate_outer_loop_bus_group_isolation,
        validate_loopback_lane_stability,
        validate_loopback_crossing_density,
    ]

    for validator in validators:
        violations.extend(
            validator(
                graph
            )
        )

    return violations


def print_report(graph_path, violations):
    print("FDS LAYOUT STABILITY REPORT")
    print("===========================")
    print(f"graph: {graph_path}")
    print(f"violations: {len(violations)}")

    if not violations:
        print("status: PASS")
        return

    has_error = any(
        violation["severity"] == "error"
        for violation in violations
    )

    print(
        "status: FAIL"
        if has_error
        else "status: REVIEW"
    )

    for index, violation in enumerate(
        violations,
        start=1
    ):
        print()
        print(
            f"{index}. [{violation['severity']}] "
            f"{violation['rule']}"
        )
        print(
            violation["message"]
        )

        if "edge" in violation:
            edge = violation["edge"]
            print(
                "   edge: "
                f"{edge.get('source')} -> {edge.get('target')} "
                f"{edge.get('label') or ''} "
                f"{edge.get('routing_type') or ''}"
            )

        if "nodes" in violation:
            print(
                "   nodes: "
                + ", ".join(
                    violation["nodes"]
                )
            )

        if "targets" in violation:
            print(
                "   targets: "
                + ", ".join(
                    violation["targets"]
                )
            )

        if "outliers" in violation:
            preview = violation["outliers"][:8]
            print(
                "   outliers: "
                + ", ".join(
                    item["id"]
                    for item in preview
                )
            )


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Validate generated ReactFlow JSON against generic "
            "FDS layout stability invariants."
        )
    )
    parser.add_argument(
        "graph",
        nargs="?",
        default="../frontend/src/data/test_graph.json",
        help="Path to generated ReactFlow JSON",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print violations as JSON",
    )

    args = parser.parse_args()

    graph_path = Path(
        args.graph
    )

    if not graph_path.is_absolute():
        graph_path = Path.cwd() / graph_path

    graph = json.loads(
        graph_path.read_text(
            encoding="utf-8"
        )
    )

    violations = validate_reactflow_graph(
        graph
    )

    if args.json:
        print(
            json.dumps(
                violations,
                indent=2
            )
        )
    else:
        print_report(
            graph_path,
            violations
        )

    if any(
        violation["severity"] == "error"
        for violation in violations
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
