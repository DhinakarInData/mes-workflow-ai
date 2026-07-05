MAJOR_NODE_TYPES = {
    "SYSTEM_CHECK",
    "SYSTEM_ACTIVITY",
    "MANUAL_ACTIVITY"
}

SUBSTEP_NODE_TYPES = {
    "RESPONSE",
    "DECISION"
}

DISPLAY_MESSAGE_TERMS = [
    "DISPLAY",
    "PRESENT",
    "SHOW",
    "MESSAGE",
    "INDICATE"
]


def normalize_text(value):

    return (
        value
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )


def is_loopback(edge):

    return (
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
    )


def base_number(display_number):

    if not display_number:

        return None

    return str(display_number).split(
        ".",
        1
    )[0]


def is_display_message_node(node):

    label = normalize_text(
        node.label
    )

    return any(
        term in label
        for term in DISPLAY_MESSAGE_TERMS
    )


def was_system_activity(node):

    return (
        getattr(
            node,
            "metadata",
            {}
        ).get(
            "original_type"
        ) == "SYSTEM_ACTIVITY"
    )


def is_human_verification_activity(node):

    if not node or node.type != "MANUAL_ACTIVITY":

        return False

    label = normalize_text(
        node.label
    )

    verification_terms = [
        "VERIFY",
        "VERIFICATION",
        "REVIEW",
        "CHECK",
        "APPROVAL",
        "APPROVE"
    ]

    return any(
        term in label
        for term in verification_terms
    )


def visible_workflow_nodes(nodes):

    return [
        node
        for node in nodes
        if node.type != "MERGE"
    ]


def non_loopback_incoming(edges):

    incoming = {}

    for edge in edges or []:

        if is_loopback(
            edge
        ):

            continue

        incoming.setdefault(
            edge.target,
            []
        ).append(
            edge
        )

    return incoming


def non_loopback_incoming_count(edges):

    incoming = non_loopback_incoming(
        edges
    )

    return {
        node_id: len(node_edges)
        for node_id, node_edges in incoming.items()
    }


def ordered_nodes(nodes, node_positions):

    node_order = {
        node.id: index
        for index, node in enumerate(
            nodes
        )
    }

    return sorted(
        visible_workflow_nodes(
            nodes
        ),
        key=lambda node: (
            node_positions.get(
                node.id,
                {}
            ).get(
                "y",
                0
            ),
            node_order.get(
                node.id,
                0
            ),
            node_positions.get(
                node.id,
                {}
            ).get(
                "x",
                0
            ),
            node.id
        )
    )


def node_lookup(nodes):

    return {
        node.id: node
        for node in nodes
    }


def edge_sort_key(edge, node_positions):

    target_position = node_positions.get(
        edge.target,
        {}
    )

    role_priority = {
        "MAIN_FLOW": 0,
        "SUCCESS": 1,
        "SIDE_BRANCH": 2,
        "LOCAL_CONTINUATION": 3,
        "ERROR": 4
    }

    return (
        role_priority.get(
            edge.routing_role,
            9
        ),
        target_position.get(
            "x",
            0
        ),
        target_position.get(
            "y",
            0
        ),
        edge.target
    )


def traversal_ordered_nodes(nodes, edges, node_positions):

    nodes_by_id = node_lookup(
        nodes
    )

    visible_ids = {
        node.id
        for node in visible_workflow_nodes(
            nodes
        )
    }

    outgoing = {}

    incoming = non_loopback_incoming(
        edges
    )

    for edge in edges or []:

        if is_loopback(
            edge
        ):

            continue

        outgoing.setdefault(
            edge.source,
            []
        ).append(
            edge
        )

    for edge_list in outgoing.values():

        edge_list.sort(
            key=lambda edge: edge_sort_key(
                edge,
                node_positions
            )
        )

    start = next(
        (
            node
            for node in nodes
            if node.type == "START"
        ),
        None
    )

    ordered = []

    visited = set()

    visiting = set()

    def incoming_ready(node_id):

        required_sources = [
            edge.source
            for edge in incoming.get(
                node_id,
                []
            )
            if edge.source in visible_ids
        ]

        return all(
            source in visited
            for source in required_sources
        )

    def visit(node_id):

        if node_id in visited or node_id in visiting:

            return

        node = nodes_by_id.get(
            node_id
        )

        if not node or node_id not in visible_ids:

            return

        if (
            incoming.get(
                node_id
            )
            and not incoming_ready(
                node_id
            )
        ):

            return

        visiting.add(
            node_id
        )

        ordered.append(
            node
        )

        visited.add(
            node_id
        )

        visiting.remove(
            node_id
        )

        for edge in outgoing.get(
            node_id,
            []
        ):

            visit(
                edge.target
            )

    if start:

        visit(
            start.id
        )

    changed = True

    while changed:

        changed = False

        for node in ordered_nodes(
            nodes,
            node_positions
        ):

            before_count = len(
                visited
            )

            visit(
                node.id
            )

            if len(
                visited
            ) > before_count:

                changed = True

    for node in ordered_nodes(
        nodes,
        node_positions
    ):

        if node.id not in visited:

            ordered.append(
                node
            )

            visited.add(
                node.id
            )

    return ordered


def edge_context(
    edge,
    base_by_node,
    context_by_node
):

    source_base = base_by_node.get(
        edge.source
    )

    source_context = context_by_node.get(
        edge.source,
        "MAIN"
    )

    if not source_base:

        return None

    if edge.routing_role == "ERROR":

        if source_context == "EXCEPTION":

            return {
                "mode": "SUBSTEP",
                "base": source_base,
                "context": "EXCEPTION"
            }

        return {
            "mode": "NEW_EXCEPTION",
            "context": "EXCEPTION"
        }

    if source_context == "EXCEPTION":

        return {
            "mode": "SUBSTEP",
            "base": source_base,
            "context": "EXCEPTION"
        }

    if edge.routing_role == "SIDE_BRANCH":

        return {
            "mode": "SIDE_BRANCH",
            "base": source_base,
            "context": "SIDE"
        }

    return {
        "mode": "MAIN",
        "base": source_base,
        "context": source_context
    }


def choose_incoming_context(
    node_id,
    incoming_edges,
    base_by_node,
    context_by_node
):

    contexts = [
        edge_context(
            edge,
            base_by_node,
            context_by_node
        )
        for edge in incoming_edges.get(
            node_id,
            []
        )
    ]

    contexts = [
        context
        for context in contexts
        if context is not None
    ]

    if not contexts:

        return None

    priority = {
        "NEW_EXCEPTION": 4,
        "SUBSTEP": 3,
        "SIDE_BRANCH": 2,
        "MAIN": 1
    }

    return max(
        contexts,
        key=lambda context: priority.get(
            context["mode"],
            0
        )
    )


def has_substep_source(
    node_id,
    incoming_edges,
    display_numbers
):

    for edge in incoming_edges.get(
        node_id,
        []
    ):

        source_number = display_numbers.get(
            edge.source
        )

        if source_number and "." in source_number:

            return True

    return False


def has_human_verification_source(
    node_id,
    incoming_edges,
    nodes_by_id
):

    for edge in incoming_edges.get(
        node_id,
        []
    ):

        if is_human_verification_activity(
            nodes_by_id.get(
                edge.source
            )
        ):

            return True

    return False


def has_terminal_and_loopback_options(
    node_id,
    edges,
    nodes_by_id
):

    has_terminal_option = False

    has_loopback_option = False

    for edge in edges or []:

        if edge.source != node_id:

            continue

        target_node = nodes_by_id.get(
            edge.target
        )

        if target_node and target_node.type == "END":

            has_terminal_option = True

        if is_loopback(
            edge
        ):

            has_loopback_option = True

    return (
        has_terminal_option
        and has_loopback_option
    )


def assign_substep(
    node_id,
    base,
    display_numbers,
    base_by_node,
    context_by_node,
    substep_counts,
    context
):

    substep_counts[base] = (
        substep_counts.get(
            base,
            0
        ) + 1
    )

    display_numbers[node_id] = (
        f"{base}.{substep_counts[base]}"
    )

    base_by_node[node_id] = base

    context_by_node[node_id] = context


def assign_major(
    node_id,
    major_counter,
    display_numbers,
    base_by_node,
    context_by_node,
    substep_counts,
    context="MAIN"
):

    major_counter += 1

    number = f"A{major_counter}"

    display_numbers[node_id] = number

    base_by_node[node_id] = number

    context_by_node[node_id] = context

    substep_counts.setdefault(
        number,
        0
    )

    return major_counter


def build_fds_display_step_numbers(
    nodes,
    edges=None,
    node_positions=None
):

    node_positions = node_positions or {}

    nodes_by_id = node_lookup(
        nodes
    )

    incoming_edges = non_loopback_incoming(
        edges
    )

    incoming_count = non_loopback_incoming_count(
        edges
    )

    display_numbers = {}

    base_by_node = {}

    context_by_node = {}

    substep_counts = {}

    major_counter = 0

    last_major_base = None

    for node in traversal_ordered_nodes(
        nodes,
        edges,
        node_positions
    ):

        if node.type == "START":

            display_numbers[node.id] = "START"

            context_by_node[node.id] = "MAIN"

            continue

        if node.type == "END":

            display_numbers[node.id] = "END"

            context_by_node[node.id] = "MAIN"

            continue

        incoming_context = choose_incoming_context(
            node.id,
            incoming_edges,
            base_by_node,
            context_by_node
        )

        is_join = incoming_count.get(
            node.id,
            0
        ) > 1

        if node.type in SUBSTEP_NODE_TYPES:

            if has_human_verification_source(
                node.id,
                incoming_edges,
                nodes_by_id
            ) or (
                node.type == "RESPONSE"
                and has_terminal_and_loopback_options(
                    node.id,
                    edges,
                    nodes_by_id
                )
            ):

                major_counter = assign_major(
                    node.id,
                    major_counter,
                    display_numbers,
                    base_by_node,
                    context_by_node,
                    substep_counts,
                    (
                        incoming_context.get(
                            "context",
                            "MAIN"
                        )
                        if incoming_context
                        else "MAIN"
                    )
                )

                last_major_base = display_numbers[node.id]

                continue

            base = (
                incoming_context.get(
                    "base"
                )
                if incoming_context
                else last_major_base
            )

            if not base:

                major_counter = assign_major(
                    node.id,
                    major_counter,
                    display_numbers,
                    base_by_node,
                    context_by_node,
                    substep_counts
                )

                last_major_base = display_numbers[node.id]

                continue

            assign_substep(
                node.id,
                base,
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                (
                    incoming_context.get(
                        "context",
                        "MAIN"
                    )
                    if incoming_context
                    else "MAIN"
                )
            )

            continue

        if node.type not in MAJOR_NODE_TYPES:

            display_numbers[node.id] = (
                node.step_number
                or node.id
            )

            continue

        if (
            incoming_context
            and incoming_context["mode"] == "SUBSTEP"
            and not is_join
        ):

            assign_substep(
                node.id,
                incoming_context["base"],
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                incoming_context.get(
                    "context",
                    "MAIN"
                )
            )

            continue

        if (
            incoming_context
            and incoming_context["mode"] == "SIDE_BRANCH"
            and (
                node.type == "SYSTEM_ACTIVITY"
                or was_system_activity(
                    node
                )
            )
            and is_display_message_node(
                node
            )
        ):

            assign_substep(
                node.id,
                incoming_context["base"],
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                "SIDE"
            )

            continue

        if (
            incoming_context
            and incoming_context["mode"] == "MAIN"
            and not is_join
            and has_substep_source(
                node.id,
                incoming_edges,
                display_numbers
            )
        ):

            assign_substep(
                node.id,
                incoming_context["base"],
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                incoming_context.get(
                    "context",
                    "MAIN"
                )
            )

            continue

        if (
            incoming_context
            and incoming_context["mode"] == "MAIN"
            and not is_join
            and (
                node.type == "SYSTEM_ACTIVITY"
                or was_system_activity(
                    node
                )
            )
            and is_display_message_node(
                node
            )
            and incoming_context.get(
                "base"
            )
        ):

            assign_substep(
                node.id,
                incoming_context["base"],
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                incoming_context.get(
                    "context",
                    "MAIN"
                )
            )

            continue

        if (
            incoming_context
            and incoming_context["mode"] == "NEW_EXCEPTION"
        ):

            major_counter = assign_major(
                node.id,
                major_counter,
                display_numbers,
                base_by_node,
                context_by_node,
                substep_counts,
                "EXCEPTION"
            )

            last_major_base = display_numbers[node.id]

            continue

        major_counter = assign_major(
            node.id,
            major_counter,
            display_numbers,
            base_by_node,
            context_by_node,
            substep_counts
        )

        last_major_base = display_numbers[node.id]

    return display_numbers
