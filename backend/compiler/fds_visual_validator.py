from dataclasses import dataclass


NODE_PADDING = 10
LANE_TOLERANCE = 8
MIN_SHARED_LANE_OVERLAP = 32
MAX_REASONABLE_EDGE_LENGTH = 2200
MIN_PERPENDICULAR_CLEARANCE = 18
MIN_SIBLING_BRANCH_CLEARANCE = 40
TARGET_SIDE_IMPROVEMENT_THRESHOLD = 180
TARGET_SIDE_CANDIDATES = [
    "target",
    "return",
    "loopback",
    "bottom",
]

ISSUE_PRIORITIES = {
    "edge_crosses_node_body": "P1",
    "lane_crossing": "P1",
    "local_retry_crosses_response_branch": "P1",
    "response_section_branch_congestion": "P2",
    "lane_overlap": "P2",
    "cleaner_target_side_available": "P2",
    "target_side_congestion": "P2",
    "label_overlaps_node": "P3",
    "excessive_lane_length": "P3",
}

ISSUE_ACTIONS = {
    "edge_crosses_node_body": "reroute_around_nodes",
    "lane_crossing": "select_non_crossing_lane",
    "local_retry_crosses_response_branch": "select_non_crossing_retry_lane",
    "response_section_branch_congestion": "repair_response_section_as_group",
    "lane_overlap": "allocate_separate_lane",
    "cleaner_target_side_available": "try_target_handle",
    "target_side_congestion": "spread_target_handles",
    "label_overlaps_node": "move_label_or_extend_lane_gap",
    "excessive_lane_length": "consider_connector_or_nearer_lane",
}


@dataclass
class Box:
    node_id: str
    left: float
    right: float
    top: float
    bottom: float


@dataclass
class Segment:
    edge_id: str
    source: str
    target: str
    label: str
    routing_type: str
    x1: float
    y1: float
    x2: float
    y2: float


def _edge_data(edge):
    return edge.get("data", {}) or {}


def _routing_type(edge):
    data = _edge_data(edge)

    return (
        data.get("routing_type")
        or data.get("routingType")
        or data.get("route")
        or ""
    )


def _edge_label(edge):
    data = _edge_data(edge)

    return data.get("label") or edge.get("label") or ""


def _normalized_label(value):
    return " ".join(
        (
            value
            or ""
        )
        .strip()
        .upper()
        .replace("_", " ")
        .split()
    )


def _is_restart_label(value):
    return _normalized_label(value) in {
        "YES",
        "CONTINUE",
        "CONTINUE WITH NEXT",
        "CONTINUE WITH NEXT EQUIPMENT",
        "NEXT",
        "NEXT EQUIPMENT",
    }


def _node_display_label(node):
    data = node.get("data", {}) or {}

    return (
        data.get("display_label")
        or data.get("label")
        or node.get("id")
        or ""
    )


def _node_ref(node_id, nodes_by_id):
    node = nodes_by_id.get(node_id)

    if not node:
        return node_id or ""

    label = _node_display_label(node)

    if not label or label == node_id:
        return node_id

    return f"{label} ({node_id})"


def _node_position(node):
    position = node.get("position", {}) or {}

    return (
        float(position.get("x", 0)),
        float(position.get("y", 0)),
    )


def _node_size(node):
    data = node.get("data", {}) or {}
    node_type = node.get("type", "")

    if node_type == "response":
        return 112.0, 86.0

    if node_type in {"start", "end"}:
        return (
            float(data.get("width", 140)),
            float(data.get("height", 54)),
        )

    return (
        float(data.get("width", 220)),
        float(data.get("height", 100)),
    )


def _node_box(node, padding=0):
    x, y = _node_position(node)
    width, height = _node_size(node)

    return Box(
        node_id=node.get("id"),
        left=x - (width / 2) - padding,
        right=x + (width / 2) + padding,
        top=y - (height / 2) - padding,
        bottom=y + (height / 2) + padding,
    )


def _handle_point(box, handle_id):
    x = (box.left + box.right) / 2
    y = (box.top + box.bottom) / 2

    if handle_id in {"error", "return", "right"}:
        return box.right, y

    if handle_id in {"restart", "loopback", "left"}:
        return box.left, y

    if handle_id in {"success", "bottom", "bottom_retry"}:
        return x, box.bottom

    if handle_id in {"target", "top", "top_retry"}:
        return x, box.top

    return x, y


def _normalize_segments(points, edge):
    segments = []

    for start, end in zip(points, points[1:]):
        x1, y1 = start
        x2, y2 = end

        if abs(x1 - x2) < 1 and abs(y1 - y2) < 1:
            continue

        segments.append(
            Segment(
                edge_id=edge.get("id", ""),
                source=edge.get("source", ""),
                target=edge.get("target", ""),
                label=_edge_label(edge),
                routing_type=_routing_type(edge),
                x1=x1,
                y1=y1,
                x2=x2,
                y2=y2,
            )
        )

    return segments


def _edge_with_target_handle(edge, target_handle):
    candidate = dict(edge)
    candidate["targetHandle"] = target_handle

    return candidate


def _orthogonal_segments(edge, boxes):
    source_box = boxes.get(edge.get("source"))
    target_box = boxes.get(edge.get("target"))

    if not source_box or not target_box:
        return []

    source_point = _handle_point(
        source_box,
        edge.get("sourceHandle"),
    )
    target_point = _handle_point(
        target_box,
        edge.get("targetHandle"),
    )

    routing_type = _routing_type(edge)
    data = _edge_data(edge)
    source_x, source_y = source_point
    target_x, target_y = target_point

    if abs(source_x - target_x) < 1 or abs(source_y - target_y) < 1:
        return _normalize_segments(
            [source_point, target_point],
            edge,
        )

    if routing_type in {"DOWN", "VERTICAL"}:
        mid_y = source_y + ((target_y - source_y) * 0.5)
        return _normalize_segments(
            [
                source_point,
                (source_x, mid_y),
                (target_x, mid_y),
                target_point,
            ],
            edge,
        )

    if routing_type == "RIGHT_EXTERNAL":
        source_branch_count = int(
            data.get("source_error_branch_count") or 1
        )
        uses_single_direct_branch = source_branch_count <= 1

        if uses_single_direct_branch:
            return _normalize_segments(
                [
                    source_point,
                    target_point,
                ],
                edge,
            )

        branch_spine_x = source_x + 76
        target_entry_x = target_x

        return _normalize_segments(
            [
                source_point,
                (branch_spine_x, source_y),
                (branch_spine_x, target_y),
                (target_entry_x, target_y),
            ],
            edge,
        )

    if routing_type == "REVIEW_BRANCH":
        review_branch_count = int(
            data.get("source_review_branch_count") or 1
        )
        review_lane_index = max(
            int(data.get("lane_offset") or 1),
            1,
        )
        target_entry_x = (
            target_x + 10
            if source_x > target_x
            else target_x - 10
        )
        review_lane_spread = (
            (review_lane_index - 1) * 34
            if review_branch_count > 1
            else 0
        )
        branch_lane_x = (
            min(source_x, target_x)
            - 70
            - review_lane_spread
        )
        review_branch_y = (
            target_y
            if review_branch_count > 1
            else source_y
        )

        if edge.get("targetHandle") in {"target", "top"}:
            top_target_approach_y = target_y - 18

            if (
                abs(review_branch_y - target_y) < 4
                and abs(source_y - review_branch_y) < 4
            ):
                return _normalize_segments(
                    [
                        source_point,
                        (target_x, source_y),
                        (target_x, top_target_approach_y),
                        target_point,
                    ],
                    edge,
                )

            return _normalize_segments(
                [
                    source_point,
                    (source_x, review_branch_y),
                    (branch_lane_x, review_branch_y),
                    (branch_lane_x, top_target_approach_y),
                    (target_x, top_target_approach_y),
                    target_point,
                ],
                edge,
            )

        if (
            abs(review_branch_y - target_y) < 4
            and abs(source_y - review_branch_y) < 4
        ):
            return _normalize_segments(
                [
                    source_point,
                    (target_entry_x, target_y),
                    target_point,
                ],
                edge,
            )

        return _normalize_segments(
            [
                source_point,
                (source_x, review_branch_y),
                (branch_lane_x, review_branch_y),
                (branch_lane_x, target_y),
                (target_entry_x, target_y),
                target_point,
            ],
            edge,
        )

    if routing_type == "SUCCESS_REJOIN":
        direction = 1 if target_x >= source_x else -1
        target_entry_x = target_x - (direction * 10)
        label = _edge_label(edge)
        label_width = min(160, max(42, min(len(label), 18) * 7 + 18))
        label_x = source_x + ((target_entry_x - source_x) * 0.48)
        label_gap_start_x = label_x - (direction * ((label_width / 2) + 14))
        label_gap_end_x = label_x + (direction * ((label_width / 2) + 14))
        first_segment_end_x = (
            min(label_gap_start_x, label_gap_end_x)
            if direction > 0
            else max(label_gap_start_x, label_gap_end_x)
        )
        second_segment_start_x = (
            max(label_gap_start_x, label_gap_end_x)
            if direction > 0
            else min(label_gap_start_x, label_gap_end_x)
        )
        branch_width = abs(source_x - target_entry_x)
        rejoin_lane_step = min(
            max(branch_width * 0.18, 24),
            58,
        )
        rejoin_lane_x = (
            min(target_entry_x - 28, second_segment_start_x + rejoin_lane_step)
            if direction > 0
            else max(target_entry_x + 28, second_segment_start_x - rejoin_lane_step)
        )
        rejoin_segment_start_x = (
            min(second_segment_start_x, rejoin_lane_x - 10)
            if direction > 0
            else max(second_segment_start_x, rejoin_lane_x + 10)
        )

        if edge.get("targetHandle") in {"target", "top"}:
            return (
                _normalize_segments(
                    [
                        source_point,
                        (first_segment_end_x, source_y),
                    ],
                    edge,
                )
                + _normalize_segments(
                    [
                        (rejoin_segment_start_x, source_y),
                        (rejoin_lane_x, source_y),
                        (rejoin_lane_x, target_y),
                        target_point,
                    ],
                    edge,
                )
            )

        return (
            _normalize_segments(
                [
                    source_point,
                    (first_segment_end_x, source_y),
                ],
                edge,
            )
            + _normalize_segments(
                [
                    (rejoin_segment_start_x, source_y),
                    (rejoin_lane_x, source_y),
                    (rejoin_lane_x, target_y),
                    target_point,
                ],
                edge,
            )
        )

    if routing_type in {"BUSINESS_BRANCH", "TERMINAL_BRANCH"}:
        direction = 1 if target_x >= source_x else -1
        lane_x = source_x + (direction * max(90, min(abs(target_x - source_x) * 0.55, 180)))

        if edge.get("targetHandle") in {"target", "top"}:
            return _normalize_segments(
                [
                    source_point,
                    (lane_x, source_y),
                    (lane_x, target_y),
                    target_point,
                ],
                edge,
            )

        return _normalize_segments(
            [
                source_point,
                (lane_x, source_y),
                (lane_x, target_y),
                target_point,
            ],
            edge,
        )

    if routing_type in {"LOCAL_RETRY_LOOP", "OUTER_LOOP", "BOTTOM_LOOP"}:
        if routing_type == "OUTER_LOOP":
            lane_x = float(
                data.get(
                    "global_return_bus_x",
                    max(source_x, target_x) + 140,
                )
            )

            if data.get("outer_loop_bus_lane_index"):
                lane_x += (
                    int(data.get("outer_loop_bus_lane_index") or 1)
                    - 1
                ) * 70
        else:
            route_side = (
                data.get("restart_side")
                or data.get("local_retry_side")
                or ("left" if target_x <= source_x else "right")
            )
            if route_side == "left":
                lane_x = min(source_x, target_x) - 120
            else:
                lane_x = max(source_x, target_x) + 120

        return _normalize_segments(
            [
                source_point,
                (lane_x, source_y),
                (lane_x, target_y),
                target_point,
            ],
            edge,
        )

    if routing_type == "RESTART_FLOW":
        restart_side = (
            "right"
            if data.get("restart_side") == "right"
            else "left"
        )
        restart_lane_index = max(
            int(data.get("restart_lane_index") or 1),
            1,
        )
        span_y = abs(source_y - target_y)
        source_target_x_gap = abs(source_x - target_x)
        is_restart_label = _is_restart_label(
            _edge_label(edge)
        )
        is_user_restart = (
            data.get("source_type") == "RESPONSE"
            and is_restart_label
        )
        is_long_main_restart = (
            target_y < source_y
            and source_target_x_gap < 80
            and span_y > 520
        )
        is_local_validation_retry = (
            target_y < source_y
            and not is_long_main_restart
            and not is_restart_label
        )

        if is_local_validation_retry:
            lane_distance = min(
                180,
                max(
                    88,
                    82 + (span_y * 0.08),
                ),
            )
        elif is_long_main_restart:
            lane_distance = min(
                330,
                235 + (span_y * 0.025),
            )
        elif is_user_restart:
            lane_distance = 260
        else:
            lane_distance = 145

        occupied_right_x = data.get("restart_left_occupied_right_x")
        occupied_left_x = data.get("restart_left_occupied_left_x")
        occupied_outer_right_x = data.get("restart_right_occupied_right_x")

        occupied_right_x = (
            float(occupied_right_x)
            if occupied_right_x is not None
            else None
        )
        occupied_left_x = (
            float(occupied_left_x)
            if occupied_left_x is not None
            else None
        )
        occupied_outer_right_x = (
            float(occupied_outer_right_x)
            if occupied_outer_right_x is not None
            else None
        )

        if restart_side == "right":
            lane_x = max(source_x, target_x) + lane_distance
            lane_x += (restart_lane_index - 1) * 132

            if occupied_outer_right_x is not None:
                lane_x = max(
                    lane_x,
                    occupied_outer_right_x
                    + 132
                    + ((restart_lane_index - 1) * 132),
                )
        else:
            preferred_lane_x = min(source_x, target_x) - lane_distance
            lane_x = preferred_lane_x

            if (
                is_long_main_restart
                and occupied_right_x is not None
            ):
                source_left_clearance = min(source_x, target_x) - occupied_right_x
                can_use_inner_lane = source_left_clearance >= 240
                nearest_clear_lane_x = min(
                    occupied_right_x,
                    min(source_x, target_x) - 92,
                )

                if can_use_inner_lane:
                    lane_x = max(
                        preferred_lane_x,
                        nearest_clear_lane_x,
                    )
                elif occupied_left_x is not None:
                    lane_x = min(
                        preferred_lane_x,
                        occupied_left_x - 132,
                    )

        if (
            data.get("source_type") == "RESPONSE"
            and data.get("target_type") == "MANUAL_ACTIVITY"
            and target_y < source_y
            and not is_restart_label
            and source_target_x_gap > 80
        ):
            if edge.get("targetHandle") in {"return", "right"}:
                lane_x = max(
                    lane_x,
                    target_x + 36,
                )
            elif edge.get("targetHandle") in {"loopback", "left"}:
                lane_x = min(
                    lane_x,
                    target_x - 36,
                )

        target_y_adjusted = (
            target_y + 26
            if (
                is_user_restart
                and int(data.get("target_outer_loop_count") or 0) > 0
            )
            else target_y
        )

        if edge.get("targetHandle") in {"target", "top"}:
            approach_y = target_y_adjusted - 14
            points = [
                source_point,
                (lane_x, source_y),
                (lane_x, approach_y),
                (target_x, approach_y),
                target_point,
            ]
        elif edge.get("targetHandle") == "bottom":
            approach_y = target_y_adjusted + 14
            points = [
                source_point,
                (lane_x, source_y),
                (lane_x, approach_y),
                (target_x, approach_y),
                target_point,
            ]
        else:
            target_arrow_x = (
                target_x - 10
                if lane_x < target_x
                else target_x + 10
            )
            points = [
                source_point,
                (lane_x, source_y),
                (lane_x, target_y_adjusted),
                (target_arrow_x, target_y_adjusted),
            ]

        return _normalize_segments(
            points,
            edge,
        )

    mid_y = source_y + ((target_y - source_y) * 0.5)

    return _normalize_segments(
        [
            source_point,
            (source_x, mid_y),
            (target_x, mid_y),
            target_point,
        ],
        edge,
    )


def _segment_orientation(segment):
    if abs(segment.x1 - segment.x2) < 1:
        return "vertical"

    if abs(segment.y1 - segment.y2) < 1:
        return "horizontal"

    return "diagonal"


def _range_overlap(first_start, first_end, second_start, second_end):
    first_low = min(first_start, first_end)
    first_high = max(first_start, first_end)
    second_low = min(second_start, second_end)
    second_high = max(second_start, second_end)

    return max(
        0,
        min(first_high, second_high) - max(first_low, second_low),
    )


def _segment_hits_box(segment, box):
    orientation = _segment_orientation(segment)

    if orientation == "vertical":
        return (
            box.left <= segment.x1 <= box.right
            and _range_overlap(segment.y1, segment.y2, box.top, box.bottom) > 0
        )

    if orientation == "horizontal":
        return (
            box.top <= segment.y1 <= box.bottom
            and _range_overlap(segment.x1, segment.x2, box.left, box.right) > 0
        )

    return False


def _segments_share_lane(first, second):
    first_orientation = _segment_orientation(first)
    second_orientation = _segment_orientation(second)

    if first_orientation != second_orientation:
        return False, 0

    if first_orientation == "vertical":
        if abs(first.x1 - second.x1) > LANE_TOLERANCE:
            return False, 0

        overlap = _range_overlap(first.y1, first.y2, second.y1, second.y2)

        return overlap >= MIN_SHARED_LANE_OVERLAP, overlap

    if first_orientation == "horizontal":
        if abs(first.y1 - second.y1) > LANE_TOLERANCE:
            return False, 0

        overlap = _range_overlap(first.x1, first.x2, second.x1, second.x2)

        return overlap >= MIN_SHARED_LANE_OVERLAP, overlap

    return False, 0


def _distance(first_x, first_y, second_x, second_y):
    return abs(first_x - second_x) + abs(first_y - second_y)


def _point_near_segment_endpoint(segment, x, y, tolerance):
    return (
        _distance(segment.x1, segment.y1, x, y) <= tolerance
        or _distance(segment.x2, segment.y2, x, y) <= tolerance
    )


def _segments_cross_perpendicular(first, second):
    first_orientation = _segment_orientation(first)
    second_orientation = _segment_orientation(second)

    if first_orientation == second_orientation:
        return False, None

    if {
        first_orientation,
        second_orientation,
    } != {
        "horizontal",
        "vertical",
    }:
        return False, None

    horizontal = first if first_orientation == "horizontal" else second
    vertical = first if first_orientation == "vertical" else second

    horizontal_left = min(horizontal.x1, horizontal.x2)
    horizontal_right = max(horizontal.x1, horizontal.x2)
    vertical_top = min(vertical.y1, vertical.y2)
    vertical_bottom = max(vertical.y1, vertical.y2)

    x = vertical.x1
    y = horizontal.y1

    crosses = (
        horizontal_left < x < horizontal_right
        and vertical_top < y < vertical_bottom
    )

    if not crosses:
        return False, None

    if (
        _point_near_segment_endpoint(
            first,
            x,
            y,
            MIN_PERPENDICULAR_CLEARANCE,
        )
        or _point_near_segment_endpoint(
            second,
            x,
            y,
            MIN_PERPENDICULAR_CLEARANCE,
        )
    ):
        return False, None

    return True, {
        "x": round(x, 1),
        "y": round(y, 1),
    }


def _route_length(segments):
    return sum(
        abs(segment.x2 - segment.x1)
        + abs(segment.y2 - segment.y1)
        for segment in segments
    )


def _route_node_hit_count(segments, boxes):
    count = 0

    for segment in segments:
        for node_id, box in boxes.items():
            if node_id in {
                segment.source,
                segment.target,
            }:
                continue

            if _segment_hits_box(segment, box):
                count += 1

    return count


def _route_perpendicular_crossing_count(segments, other_segments):
    count = 0

    for segment in segments:
        for other in other_segments:
            if segment.edge_id == other.edge_id:
                continue

            crosses, _ = _segments_cross_perpendicular(
                segment,
                other,
            )

            if crosses:
                count += 1

    return count


def _segments_have_low_perpendicular_clearance(first, second, clearance):
    first_orientation = _segment_orientation(first)
    second_orientation = _segment_orientation(second)

    if {
        first_orientation,
        second_orientation,
    } != {
        "horizontal",
        "vertical",
    }:
        return False, None

    horizontal = first if first_orientation == "horizontal" else second
    vertical = first if first_orientation == "vertical" else second
    horizontal_min_x = min(horizontal.x1, horizontal.x2)
    horizontal_max_x = max(horizontal.x1, horizontal.x2)
    vertical_min_y = min(vertical.y1, vertical.y2)
    vertical_max_y = max(vertical.y1, vertical.y2)
    vertical_x = vertical.x1
    horizontal_y = horizontal.y1

    if not (
        vertical_min_y - clearance
        <= horizontal_y
        <= vertical_max_y + clearance
    ):
        return False, None

    if horizontal_min_x <= vertical_x <= horizontal_max_x:
        distance = 0
    elif vertical_x < horizontal_min_x:
        distance = horizontal_min_x - vertical_x
    else:
        distance = vertical_x - horizontal_max_x

    if distance > clearance:
        return False, None

    return True, (
        vertical_x,
        horizontal_y,
    )


def _route_shared_lane_count(segments, other_segments):
    count = 0

    for segment in segments:
        for other in other_segments:
            if segment.edge_id == other.edge_id:
                continue

            shares_lane, _ = _segments_share_lane(
                segment,
                other,
            )

            if shares_lane:
                count += 1

    return count


def _route_turn_count(segments):
    count = 0

    for first, second in zip(segments, segments[1:]):
        if _segment_orientation(first) != _segment_orientation(second):
            count += 1

    return count


def _route_backtrack_count(segments):
    count = 0

    for first, second in zip(segments, segments[1:]):
        first_orientation = _segment_orientation(first)
        second_orientation = _segment_orientation(second)

        if first_orientation != second_orientation:
            continue

        if first_orientation == "horizontal":
            if abs(first.y1 - second.y1) > 1:
                continue

            first_direction = 1 if first.x2 >= first.x1 else -1
            second_direction = 1 if second.x2 >= second.x1 else -1

            if first_direction != second_direction:
                count += 1

        if first_orientation == "vertical":
            if abs(first.x1 - second.x1) > 1:
                continue

            first_direction = 1 if first.y2 >= first.y1 else -1
            second_direction = 1 if second.y2 >= second.y1 else -1

            if first_direction != second_direction:
                count += 1

    return count


def _route_score(segments, boxes, other_segments):
    return (
        _route_node_hit_count(segments, boxes) * 1000
        + _route_perpendicular_crossing_count(segments, other_segments) * 350
        + _route_shared_lane_count(segments, other_segments) * 160
        + _route_backtrack_count(segments) * 260
        + _route_turn_count(segments) * 35
        + (_route_length(segments) * 0.04)
    )


def _is_branch_route(edge):
    return _routing_type(edge) in {
        "BUSINESS_BRANCH",
        "REVIEW_BRANCH",
        "SUCCESS_REJOIN",
        "TERMINAL_BRANCH",
        "RESTART_FLOW",
        "LOCAL_RETRY_LOOP",
    }


def _is_local_retry_route(edge):
    return _routing_type(edge) == "LOCAL_RETRY_LOOP"


def _is_response_branch_route(edge):
    return _routing_type(edge) in {
        "BUSINESS_BRANCH",
        "REVIEW_BRANCH",
        "SUCCESS_REJOIN",
        "TERMINAL_BRANCH",
        "RESTART_FLOW",
        "RIGHT_EXTERNAL",
    }


def _is_response_node(node):
    data = node.get("data", {}) or {}

    return (
        node.get("type") == "response"
        or data.get("response_actor") is not None
        or "Response" in _node_display_label(node)
    )


def _is_section_quality_rule(rule):
    return rule in {
        "lane_crossing",
        "local_retry_crosses_response_branch",
        "lane_overlap",
        "target_side_congestion",
        "cleaner_target_side_available",
    }


def _build_response_section_issues(edges, nodes_by_id, issues):
    outgoing_by_source = {}

    for edge in edges:
        source = edge.get("source")

        if not source:
            continue

        outgoing_by_source.setdefault(
            source,
            [],
        ).append(edge)

    issue_edges = set()

    for issue in issues:
        if not _is_section_quality_rule(issue.get("rule")):
            continue

        if issue.get("edge_id"):
            issue_edges.add(issue.get("edge_id"))

        if issue.get("other_edge_id"):
            issue_edges.add(issue.get("other_edge_id"))

    section_issues = []

    for source, outgoing_edges in outgoing_by_source.items():
        source_node = nodes_by_id.get(source)

        if not source_node or not _is_response_node(source_node):
            continue

        branch_edges = [
            edge
            for edge in outgoing_edges
            if _is_branch_route(edge)
            or _routing_type(edge) in {"RIGHT_EXTERNAL", "DOWN"}
        ]

        if len(branch_edges) <= 1:
            continue

        affected_edges = [
            edge
            for edge in branch_edges
            if edge.get("id") in issue_edges
        ]

        if not affected_edges:
            continue

        labels = [
            _edge_label(edge)
            for edge in branch_edges
            if _edge_label(edge)
        ]

        section_issues.append(
            {
                "severity": "warning",
                "rule": "response_section_branch_congestion",
                "message": (
                    "Response section has branch congestion; repair this "
                    "decision area as one group instead of fixing only one "
                    "edge."
                ),
                "source": source,
                "section_edge_ids": [
                    edge.get("id")
                    for edge in branch_edges
                    if edge.get("id")
                ],
                "affected_edge_ids": [
                    edge.get("id")
                    for edge in affected_edges
                    if edge.get("id")
                ],
                "labels": labels,
            }
        )

    return section_issues


def _edge_endpoint_set(edge):
    return {
        edge.get("source"),
        edge.get("target"),
    }


def _edges_are_local_branch_siblings(first_edge, second_edge, graph_context):
    first_endpoints = _edge_endpoint_set(first_edge)
    second_endpoints = _edge_endpoint_set(second_edge)

    if first_endpoints & second_endpoints:
        return True

    incoming_by_target = graph_context.get("incoming_by_target", {})

    first_parents = set(
        incoming_by_target.get(
            first_edge.get("source"),
            [],
        )
    ) | set(
        incoming_by_target.get(
            first_edge.get("target"),
            [],
        )
    )
    second_parents = set(
        incoming_by_target.get(
            second_edge.get("source"),
            [],
        )
    ) | set(
        incoming_by_target.get(
            second_edge.get("target"),
            [],
        )
    )

    return bool(first_parents & second_parents)


def _is_local_retry_response_branch_crossing(first_edge, second_edge, graph_context):
    first_is_retry = _is_local_retry_route(first_edge)
    second_is_retry = _is_local_retry_route(second_edge)

    if first_is_retry == second_is_retry:
        return False

    retry_edge = first_edge if first_is_retry else second_edge
    branch_edge = second_edge if first_is_retry else first_edge

    if not _is_response_branch_route(branch_edge):
        return False

    return _edges_are_local_branch_siblings(
        retry_edge,
        branch_edge,
        graph_context,
    )


def _issue_priority(issue):
    return ISSUE_PRIORITIES.get(
        issue.get("rule"),
        "P3",
    )


def _issue_action(issue):
    return ISSUE_ACTIONS.get(
        issue.get("rule"),
        "inspect_route",
    )


def _issue_sort_key(issue):
    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
    }

    return (
        priority_order.get(
            issue.get("priority"),
            9,
        ),
        issue.get("edge_id") or "",
        issue.get("rule") or "",
        issue.get("target") or "",
    )


def _dedupe_pair_key(first_edge_id, second_edge_id):
    return "|".join(
        sorted(
            [
                first_edge_id or "",
                second_edge_id or "",
            ]
        )
    )


def _issue_dedupe_key(issue):
    rule = issue.get("rule")

    if rule in {
        "lane_crossing",
        "local_retry_crosses_response_branch",
        "lane_overlap",
    }:
        return (
            rule,
            _dedupe_pair_key(
                issue.get("edge_id"),
                issue.get("other_edge_id"),
            ),
        )

    if rule == "edge_crosses_node_body":
        return (
            rule,
            issue.get("edge_id"),
            issue.get("node"),
        )

    if rule == "cleaner_target_side_available":
        return (
            rule,
            issue.get("edge_id"),
            issue.get("current_target_handle"),
            issue.get("suggested_target_handle"),
        )

    if rule == "target_side_congestion":
        return (
            rule,
            issue.get("target"),
            issue.get("target_handle"),
        )

    if rule == "response_section_branch_congestion":
        return (
            rule,
            issue.get("source"),
        )

    return (
        rule,
        issue.get("edge_id"),
        issue.get("target"),
        issue.get("message"),
    )


def _dedupe_issues(issues):
    seen = set()
    deduped = []

    for issue in issues:
        key = _issue_dedupe_key(issue)

        if key in seen:
            continue

        seen.add(key)
        deduped.append(issue)

    return deduped


def _group_node_crossing_issues(issues, nodes_by_id):
    grouped = {}
    passthrough = []

    for issue in issues:
        if issue.get("rule") != "edge_crosses_node_body":
            passthrough.append(issue)
            continue

        key = issue.get("edge_id")

        grouped.setdefault(
            key,
            {
                **issue,
                "crossed_nodes": [],
                "crossed_node_refs": [],
            },
        )

        node_id = issue.get("node")

        if node_id and node_id not in grouped[key]["crossed_nodes"]:
            grouped[key]["crossed_nodes"].append(node_id)
            grouped[key]["crossed_node_refs"].append(
                _node_ref(
                    node_id,
                    nodes_by_id,
                )
            )

    merged = []

    for issue in grouped.values():
        crossed_node_refs = issue.get("crossed_node_refs", [])

        if len(crossed_node_refs) > 1:
            issue["message"] = (
                "Edge route crosses multiple nodes: "
                + ", ".join(crossed_node_refs)
                + "."
            )
        elif crossed_node_refs:
            issue["message"] = (
                "Edge route crosses node "
                + crossed_node_refs[0]
                + "."
            )

        merged.append(issue)

    return passthrough + merged


def _make_repair_hint(issue):
    action = issue.get("action")

    if action == "try_target_handle":
        return (
            f"Try targetHandle={issue.get('suggested_target_handle')} "
            f"instead of {issue.get('current_target_handle')}."
        )

    if action == "select_non_crossing_lane":
        return "Choose a route side/lane that does not cross the other edge."

    if action == "select_non_crossing_retry_lane":
        return (
            "Move the retry/return lane outside the sibling response branch "
            "so both decisions remain readable."
        )

    if action == "repair_response_section_as_group":
        return (
            "Evaluate all outgoing branches from this response together; keep "
            "the main/down branch clean and move side/retry branches to "
            "non-crossing lanes or cleaner target handles."
        )

    if action == "allocate_separate_lane":
        return "Reserve a separate lane for one of the overlapping edges."

    if action == "reroute_around_nodes":
        return "Move this route outside the occupied node corridor."

    if action == "spread_target_handles":
        return "Use a different target side for at least one incoming edge."

    if action == "consider_connector_or_nearer_lane":
        return "Use a connector or shorten the return lane."

    if action == "move_label_or_extend_lane_gap":
        return "Move the label or increase the lane gap around it."

    return "Inspect this route before auto-repair."


def _finalize_issues(issues, nodes_by_id):
    for issue in issues:
        if issue.get("source"):
            issue["source_ref"] = _node_ref(
                issue.get("source"),
                nodes_by_id,
            )

        if issue.get("target"):
            issue["target_ref"] = _node_ref(
                issue.get("target"),
                nodes_by_id,
            )

        issue["priority"] = _issue_priority(issue)
        issue["action"] = _issue_action(issue)

    issues = _dedupe_issues(issues)
    issues = _group_node_crossing_issues(
        issues,
        nodes_by_id,
    )

    for issue in issues:
        issue["priority"] = _issue_priority(issue)
        issue["action"] = _issue_action(issue)
        issue["repair_hint"] = _make_repair_hint(issue)

    return sorted(
        issues,
        key=_issue_sort_key,
    )


def _issue(severity, rule, message, edge=None, **extra):
    result = {
        "severity": severity,
        "rule": rule,
        "message": message,
    }

    if edge:
        result.update(
            {
                "edge_id": edge.edge_id,
                "source": edge.source,
                "target": edge.target,
                "label": edge.label,
                "routing_type": edge.routing_type,
            }
        )

    result.update(extra)

    return result


def _label_box(edge, segments):
    label = _edge_label(edge)

    if not label or not segments:
        return None

    longest = max(
        segments,
        key=lambda segment: abs(segment.x2 - segment.x1) + abs(segment.y2 - segment.y1),
    )

    line_count = max(1, (len(label) + 17) // 18)
    width = min(160, max(42, min(len(label), 18) * 7 + 18))
    height = 16 + ((line_count - 1) * 13)
    x = (longest.x1 + longest.x2) / 2
    y = (longest.y1 + longest.y2) / 2

    return Box(
        node_id=edge.get("id", ""),
        left=x - (width / 2),
        right=x + (width / 2),
        top=y - (height / 2),
        bottom=y + (height / 2),
    )


def _boxes_overlap(first, second):
    return not (
        first.right < second.left
        or second.right < first.left
        or first.bottom < second.top
        or second.bottom < first.top
    )


def validate_fds_visual_layout(reactflow_graph):
    nodes = [
        node
        for node in reactflow_graph.get("nodes", [])
        if not (node.get("data", {}) or {}).get("hidden")
    ]
    edges = reactflow_graph.get("edges", [])
    nodes_by_id = {
        node.get("id"): node
        for node in nodes
        if node.get("id")
    }
    edges_by_id = {
        edge.get("id", ""): edge
        for edge in edges
        if edge.get("id")
    }
    incoming_by_target = {}

    for edge in edges:
        incoming_by_target.setdefault(
            edge.get("target"),
            [],
        ).append(edge.get("source"))

    graph_context = {
        "incoming_by_target": incoming_by_target,
    }

    boxes = {
        node.get("id"): _node_box(
            node,
            padding=NODE_PADDING,
        )
        for node in nodes
        if node.get("id")
    }

    edge_segments = {
        edge.get("id", ""): _orthogonal_segments(edge, boxes)
        for edge in edges
    }

    issues = []

    for edge in edges:
        segments = edge_segments.get(edge.get("id", ""), [])

        for segment in segments:
            length = abs(segment.x2 - segment.x1) + abs(segment.y2 - segment.y1)

            if length > MAX_REASONABLE_EDGE_LENGTH:
                issues.append(
                    _issue(
                        "warning",
                        "excessive_lane_length",
                        "Edge route is very long; consider connector or a nearer return lane.",
                        segment,
                        length=round(length, 1),
                    )
                )

            for node_id, box in boxes.items():
                if node_id in {segment.source, segment.target}:
                    continue

                if _segment_hits_box(segment, box):
                    issues.append(
                        _issue(
                            "error",
                            "edge_crosses_node_body",
                            (
                                "Edge segment crosses node "
                                f"{_node_ref(node_id, nodes_by_id)}."
                            ),
                            segment,
                            node=node_id,
                            node_ref=_node_ref(node_id, nodes_by_id),
                        )
                    )

        label_box = _label_box(edge, segments)

        if label_box:
            for node_id, box in boxes.items():
                if node_id in {edge.get("source"), edge.get("target")}:
                    continue

                if _boxes_overlap(label_box, box):
                    issues.append(
                        _issue(
                            "warning",
                            "label_overlaps_node",
                            (
                                "Edge label may overlap node "
                                f"{_node_ref(node_id, nodes_by_id)}."
                            ),
                            edge=segments[0] if segments else None,
                            node=node_id,
                            node_ref=_node_ref(node_id, nodes_by_id),
                        )
                    )

    flat_segments = [
        segment
        for segments in edge_segments.values()
        for segment in segments
    ]

    for index, first in enumerate(flat_segments):
        for second in flat_segments[index + 1:]:
            if first.edge_id == second.edge_id:
                continue

            crosses, point = _segments_cross_perpendicular(
                first,
                second,
            )
            first_edge = edges_by_id.get(first.edge_id, {})
            second_edge = edges_by_id.get(second.edge_id, {})
            is_local_retry_branch_crossing = (
                _is_local_retry_response_branch_crossing(
                    first_edge,
                    second_edge,
                    graph_context,
                )
            )

            if crosses:
                issues.append(
                    _issue(
                        "error",
                        (
                            "local_retry_crosses_response_branch"
                            if is_local_retry_branch_crossing
                            else "lane_crossing"
                        ),
                        (
                            "A local retry/return lane crosses a sibling "
                            "response branch lane inside the same FDS section."
                            if is_local_retry_branch_crossing
                            else "Two edge lanes cross each other away from a node handle."
                        ),
                        first,
                        other_edge_id=second.edge_id,
                        crossing=point,
                    )
                )
            elif is_local_retry_branch_crossing:
                too_close, near_point = _segments_have_low_perpendicular_clearance(
                    first,
                    second,
                    MIN_SIBLING_BRANCH_CLEARANCE,
                )

                if too_close:
                    issues.append(
                        _issue(
                            "error",
                            "local_retry_crosses_response_branch",
                            (
                                "A local retry/return lane is too close to a "
                                "sibling response branch lane inside the same "
                                "FDS section."
                            ),
                            first,
                            other_edge_id=second.edge_id,
                            crossing=near_point,
                        )
                    )

            shares_lane, overlap = _segments_share_lane(first, second)

            if not shares_lane:
                continue

            if (
                first.source == second.source
                and first.routing_type == second.routing_type
                and first.routing_type in {"RIGHT_EXTERNAL", "OUTER_LOOP"}
            ):
                continue

            issues.append(
                _issue(
                    "warning",
                    "lane_overlap",
                    "Two unrelated edge segments appear to share the same lane.",
                    first,
                    other_edge_id=second.edge_id,
                    overlap=round(overlap, 1),
                )
            )

    for edge in edges:
        if not _is_branch_route(edge):
            continue

        current_target_handle = edge.get("targetHandle") or "target"

        if edge.get("source") == edge.get("target"):
            continue

        current_segments = edge_segments.get(
            edge.get("id", ""),
            [],
        )

        if not current_segments:
            continue

        other_segments = [
            segment
            for segment in flat_segments
            if segment.edge_id != edge.get("id", "")
        ]

        current_score = _route_score(
            current_segments,
            boxes,
            other_segments,
        )
        best_handle = current_target_handle
        best_score = current_score

        for candidate_handle in TARGET_SIDE_CANDIDATES:
            if candidate_handle == current_target_handle:
                continue

            candidate_edge = _edge_with_target_handle(
                edge,
                candidate_handle,
            )
            candidate_segments = _orthogonal_segments(
                candidate_edge,
                boxes,
            )

            if not candidate_segments:
                continue

            candidate_score = _route_score(
                candidate_segments,
                boxes,
                other_segments,
            )

            if candidate_score < best_score:
                best_score = candidate_score
                best_handle = candidate_handle

        improvement = current_score - best_score

        if improvement >= TARGET_SIDE_IMPROVEMENT_THRESHOLD:
            first_segment = current_segments[0]

            issues.append(
                _issue(
                    "warning",
                    "cleaner_target_side_available",
                    (
                        "Another target side appears cleaner for this "
                        "branch route."
                    ),
                    first_segment,
                    current_target_handle=current_target_handle,
                    suggested_target_handle=best_handle,
                    current_score=round(current_score, 1),
                    suggested_score=round(best_score, 1),
                )
            )

    incoming_by_target_side = {}

    for edge in edges:
        key = (
            edge.get("target"),
            edge.get("targetHandle") or "center",
        )
        incoming_by_target_side.setdefault(key, []).append(edge)

    for (target, target_handle), grouped_edges in incoming_by_target_side.items():
        if target_handle in {"target", "top"}:
            continue

        if len(grouped_edges) <= 1:
            continue

        labels = [
            _edge_label(edge)
            for edge in grouped_edges
            if _edge_label(edge)
        ]

        issues.append(
            {
                "severity": "warning",
                "rule": "target_side_congestion",
                "message": (
                    f"{len(grouped_edges)} edges enter {target} through "
                    f"the same {target_handle} side."
                ),
                "target": target,
                "target_ref": _node_ref(target, nodes_by_id),
                "target_handle": target_handle,
                "labels": labels,
            }
        )

    issues.extend(
        _build_response_section_issues(
            edges,
            nodes_by_id,
            issues,
        )
    )

    return _finalize_issues(
        issues,
        nodes_by_id,
    )


def format_fds_visual_report(issues, max_items=30):
    if not issues:
        return "FDS visual validation report: no visual issues detected."

    error_count = len(
        [
            issue
            for issue in issues
            if issue.get("severity") == "error"
        ]
    )
    warning_count = len(
        [
            issue
            for issue in issues
            if issue.get("severity") == "warning"
        ]
    )

    lines = [
        "FDS visual validation report",
        f"- errors: {error_count}",
        f"- warnings: {warning_count}",
    ]

    for issue_number, issue in enumerate(
        issues[:max_items],
        start=1,
    ):
        edge_text = ""

        if issue.get("edge_id"):
            edge_text = (
                f" [{issue.get('edge_id')}]"
            )

        label_text = ""

        if issue.get("label"):
            label_text = f" label={issue.get('label')}"
        elif issue.get("labels"):
            label_text = (
                " labels="
                + ", ".join(
                    issue.get("labels", [])[:6]
                )
            )

        suggestion_text = ""

        if issue.get("suggested_target_handle"):
            suggestion_text = (
                f" current={issue.get('current_target_handle')}"
                f" suggested={issue.get('suggested_target_handle')}"
            )

        if issue.get("other_edge_id"):
            suggestion_text += f" other={issue.get('other_edge_id')}"

        if issue.get("action"):
            suggestion_text += f" action={issue.get('action')}"

        route_text = ""

        if issue.get("source_ref") and issue.get("target_ref"):
            route_text = (
                f" {issue.get('source_ref', issue.get('source', ''))}"
                f" -> {issue.get('target_ref', issue.get('target', ''))}"
            )
        elif issue.get("source_ref"):
            route_text = f" source={issue.get('source_ref')}"
        elif issue.get("target_ref"):
            route_text = f" target={issue.get('target_ref')}"

        lines.append(
            f"{issue_number}. {issue.get('priority')} "
            f"{issue.get('severity')} "
            f"{issue.get('rule')}{edge_text}{route_text}: "
            f"{issue.get('message')}{label_text}{suggestion_text}"
        )

        if issue.get("repair_hint"):
            lines.append(
                f"   repair: {issue.get('repair_hint')}"
            )

    if len(issues) > max_items:
        lines.append(
            f"- ... {len(issues) - max_items} more visual issue(s)"
        )

    return "\n".join(lines)
