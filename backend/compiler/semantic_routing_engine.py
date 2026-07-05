from models.workflow_models import (
    WorkflowEdge,
    WorkflowNode
)


def normalize_text(value):

    return (
        value
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )


def edge_label(edge):

    return normalize_text(
        edge.condition
        or edge.edge_label
    )


def node_label(node):

    return normalize_text(
        node.label
        if node
        else ""
    )


def explicit_routing_role(edge):

    value = (
        edge.routing_role
        or ""
    ).strip().upper().replace(
        " ",
        "_"
    )

    if value in {
        "SUCCESS",
        "ERROR",
        "LOOPBACK",
        "MAIN_FLOW",
        "SIDE_BRANCH",
        "LOCAL_CONTINUATION",
        "TERMINAL"
    }:

        return value

    return None


def is_backward_edge(graph, edge):

    source_index = graph.metadata.get(
        "node_order",
        {}
    ).get(
        edge.source
    )

    target_index = graph.metadata.get(
        "node_order",
        {}
    ).get(
        edge.target
    )

    if source_index is None or target_index is None:

        return True

    return target_index <= source_index


def is_terminal_target(graph, edge):

    target = graph.get_node(
        edge.target
    )

    return target is not None and target.type == "END"


def target_index(graph, node_id):

    return graph.metadata.get(
        "node_order",
        {}
    ).get(
        node_id
    )


def is_forward_edge(graph, edge):

    source_index = target_index(
        graph,
        edge.source
    )

    target_index_value = target_index(
        graph,
        edge.target
    )

    if source_index is None or target_index_value is None:

        return False

    return target_index_value > source_index


def source_has_backward_retry(graph, edge):

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        if outgoing_edge is edge:

            continue

        if outgoing_edge.edge_type != "LOOPBACK":

            continue

        if is_backward_edge(
            graph,
            outgoing_edge
        ):

            return True

    return False


def source_has_success_rejoin(graph, edge):

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        if outgoing_edge is edge:

            continue

        if outgoing_edge.routing_role == "SUCCESS":

            return True

    return False


def is_local_retry_continuation(graph, edge, label):

    return (
        label in {
            "NO",
            "N"
        }
        and is_forward_edge(
            graph,
            edge
        )
        and source_has_backward_retry(
            graph,
            edge
        )
    )


def is_exception_local_continuation(graph, edge, label, exception_nodes):

    return (
        edge.source in exception_nodes
        and
        is_forward_edge(
            graph,
            edge
        )
        and source_has_success_rejoin(
            graph,
            edge
        )
        and (
            is_failure_outcome(
                label
            )
            or target_is_exception_work(
                graph,
                edge
            )
        )
    )


def is_neutral_valid_outcome(label):

    exact_outcomes = {
        "APPLICABLE",
        "NOT APPLICABLE",
        "NA",
        "N A",
        "N/A",
        "COMPLY OR NA",
        "COMPLY OR N A",
        "COMPLY OR N/A",
        "OPERATOR CHECKS",
        "OPERATOR CHECK",
        "PERFORMER IS OPERATOR",
        "SUPERVISOR QA CHECKS",
        "SUPERVISOR/QA CHECKS",
        "SUPERVISOR OR QA CHECKS",
        "PERFORMER IS SUPERVISOR OR QA",
        "PERFORMER IS SUPERVISOR/QA",
    }

    if label in exact_outcomes:

        return True

    actor_route_terms = [
        "SUPERVISOR",
        "QA",
        "OPERATOR",
        "PERFORMER"
    ]

    actor_selection_terms = [
        "CHECK",
        "CHECKS",
        "SELECT",
        "SELECTED",
        "PERFORMER"
    ]

    return (
        any(
            term in label
            for term in actor_route_terms
        )
        and any(
            term in label
            for term in actor_selection_terms
        )
    )


def is_normal_success_outcome(label):

    exact_outcomes = {
        "YES",
        "Y",
        "TRUE",
        "VALID",
        "CORRECT",
        "AVAILABLE",
        "DONE",
        "PASS",
        "PASSED",
        "SUCCESS",
        "SUCCESSFUL",
        "COMPLY",
        "COMPLIES",
        "COMPLIANT",
        "APPROVED",
        "CONFIRMED",
        "MATCH",
        "MATCHED",
        "ACCEPTED"
    }

    if label in exact_outcomes:

        return True

    success_phrases = [
        "IS VALID",
        "ARE VALID",
        "DETAILS VALID",
        "STATUS VALID",
        "IS AVAILABLE",
        "ARE AVAILABLE",
        "IS CORRECT",
        "ARE CORRECT",
        "QTY COMPLIES",
        "QUANTITY COMPLIES",
        "WEIGHT COMPLIES",
        "MATCHES",
        "MATCH FOUND"
    ]

    return any(
        phrase in label
        for phrase in success_phrases
    )


def is_valid_side_branch(label):

    if label in {
        "APPLICABLE",
        "NOT APPLICABLE",
        "NA",
        "N A",
        "N/A",
        "SUPERVISOR QA CHECKS",
        "SUPERVISOR/QA CHECKS",
        "SUPERVISOR OR QA CHECKS",
        "PERFORMER IS SUPERVISOR OR QA",
        "PERFORMER IS SUPERVISOR/QA",
    }:

        return True

    return (
        (
            "SUPERVISOR" in label
            or "QA" in label
        )
        and (
            "CHECK" in label
            or "PERFORMER" in label
            or "SELECT" in label
        )
    )


def is_applicability_bypass_branch(graph, edge, label):

    if label not in {
        "NOT APPLICABLE",
        "NA",
        "N A",
        "N/A"
    }:

        return False

    source_node = graph.get_node(
        edge.source
    )

    if not source_node or source_node.type != "RESPONSE":

        return False

    sibling_labels = {
        edge_label(
            outgoing_edge
        )
        for outgoing_edge in graph.adjacency_map.get(
            edge.source,
            []
        )
        if outgoing_edge is not edge
    }

    return "APPLICABLE" in sibling_labels


def is_applicability_main_branch(graph, edge, label):

    if label != "APPLICABLE":

        return False

    source_node = graph.get_node(
        edge.source
    )

    if not source_node or source_node.type != "RESPONSE":

        return False

    sibling_labels = {
        edge_label(
            outgoing_edge
        )
        for outgoing_edge in graph.adjacency_map.get(
            edge.source,
            []
        )
        if outgoing_edge is not edge
    }

    return bool(
        sibling_labels.intersection(
            {
                "NOT APPLICABLE",
                "NA",
                "N A",
                "N/A"
            }
        )
    )


def is_failure_outcome(label):

    failure_terms = [
        "INVALID",
        "INCORRECT",
        "REJECT",
        "REJECTED",
        "FAIL",
        "FAILED",
        "DOES NOT COMPLY",
        "NOT COMPLY",
        "NOT CORRECT",
        "NOT VALID",
        "NOT DONE",
        "NOT AVAILABLE",
        "UNAVAILABLE",
        "NOT COMPLETE",
        "NOT COMPLETED",
        "NOT ASSIGNED",
        "NOT CALIBRATED",
        "DOES NOT EXIST",
        "NOT EXIST",
        "OUTSIDE RANGE",
        "OUTSIDE THE RANGE",
        "OUTSIDE SCALE RANGE",
        "OUTSIDE THE SCALE RANGE",
        "ABOVE LIMIT",
        "BELOW LIMIT",
        "MISMATCH",
        "BREAKDOWN",
        "ERROR"
    ]

    return any(
        term in label
        for term in failure_terms
    )


def is_restart_loop_label(label):

    restart_labels = {
        "YES",
        "Y",
        "CONTINUE",
        "CONTINUE WITH NEXT EQUIPMENT",
        "CONFIRM NEXT EQUIPMENT",
        "NEXT EQUIPMENT",
        "RETRY",
        "REDO",
        "REWORK",
        "REQUIRED",
        "REWEIGH",
        "REWEIGHING",
        "SCAN ANOTHER",
        "SCAN ANOTHER PRODUCT CONTAINER",
        "SCAN ANOTHER EMPTY CONTAINER",
        "GO FOR REWEIGHING",
        "PROCESS CORRECTED",
        "CORRECT PROCESS"
    }

    if label in restart_labels:

        return True

    restart_phrases = [
        "SCAN ANOTHER",
        "RETURN TO",
        "BACK TO",
        "RE-SCAN",
        "RESCAN",
        "RE VERIFY",
        "RE-VERIFY",
        "REVERIFICATION",
        "RE-VERIFICATION",
        "REWEIGH",
        "RE-WEIGH",
        "CORRECTED",
        "CORRECTION"
    ]

    return any(
        phrase in label
        for phrase in restart_phrases
    )


def is_response_backward_branch(graph, edge):

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
        "MERGE"
    ]:

        return False

    return is_backward_edge(
        graph,
        edge
    )


def has_backward_retry_from_node(
    graph,
    start_id,
    source_edge=None,
    max_depth=8
):

    visited = set()

    queue = [
        (
            start_id,
            0
        )
    ]

    start_index = target_index(
        graph,
        start_id
    )

    while queue:

        node_id, depth = queue.pop(0)

        if depth > max_depth:

            continue

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        for outgoing_edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if outgoing_edge is source_edge:

                continue

            outgoing_label = edge_label(
                outgoing_edge
            )

            if (
                outgoing_edge.edge_type == "LOOPBACK"
                or outgoing_edge.routing_role == "LOOPBACK"
                or is_restart_loop_label(
                    outgoing_label
                )
            ):

                outgoing_target_index = target_index(
                    graph,
                    outgoing_edge.target
                )

                if (
                    outgoing_target_index is None
                    or start_index is None
                    or outgoing_target_index <= start_index
                ):

                    return True

            if outgoing_edge.edge_type == "LOOPBACK":

                continue

            target_node = graph.get_node(
                outgoing_edge.target
            )

            if target_node and target_node.type == "END":

                continue

            queue.append(
                (
                    outgoing_edge.target,
                    depth + 1
                )
            )

    return False


def response_has_success_or_neutral_branch(graph, edge):

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        if outgoing_edge is edge:

            continue

        label = edge_label(
            outgoing_edge
        )

        if outgoing_edge.routing_role == "SUCCESS":

            return True

        if is_neutral_valid_outcome(
            label
        ):

            return True

    return False


def is_business_option_branch(graph, edge, label):

    if edge.edge_type != "CONDITIONAL":

        return False

    if is_terminal_target(
        graph,
        edge
    ):

        return False

    if is_restart_loop_label(
        label
    ):

        return False

    if is_failure_outcome(
        label
    ):

        return False

    if target_is_exception_work(
        graph,
        edge
    ):

        return False

    source_node = graph.get_node(
        edge.source
    )

    if not source_node or source_node.type != "RESPONSE":

        return False

    forward_options = 0

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        if outgoing_edge.edge_type != "CONDITIONAL":

            continue

        if is_terminal_target(
            graph,
            outgoing_edge
        ):

            continue

        outgoing_label = edge_label(
            outgoing_edge
        )

        if (
            is_restart_loop_label(
                outgoing_label
            )
            or is_failure_outcome(
                outgoing_label
            )
            or target_is_exception_work(
                graph,
                outgoing_edge
            )
        ):

            continue

        forward_options += 1

    return forward_options > 1


def is_human_response_retry_loop(graph, edge, label):

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

    if source_node.response_actor == "SYSTEM":

        return False

    if target_node.type != "MANUAL_ACTIVITY":

        return False

    return (
        is_backward_edge(
            graph,
            edge
        )
        and (
            is_failure_outcome(
                label
            )
            or "NOT" in label
        )
    )


def is_structural_retry_branch(graph, edge):

    if edge.edge_type != "CONDITIONAL":

        return False

    if is_terminal_target(
        graph,
        edge
    ):

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

    label = edge_label(
        edge
    )

    if is_neutral_valid_outcome(
        label
    ):

        return False

    if is_restart_loop_label(
        label
    ):

        return False

    if (
        target_node.type == "MANUAL_ACTIVITY"
        and not is_failure_outcome(
            label
        )
        and not target_is_exception_work(
            graph,
            edge
        )
    ):

        return False

    return (
        response_has_success_or_neutral_branch(
            graph,
            edge
        )
        and has_backward_retry_from_node(
            graph,
            edge.target,
            edge
        )
    )


def is_neutral_retry_error_branch(graph, edge, label):

    if not is_neutral_valid_outcome(
        label
    ):

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

    return has_backward_retry_from_node(
        graph,
        edge.target,
        edge
    )


def target_is_exception_work(graph, edge):

    target = graph.get_node(
        edge.target
    )

    label = node_label(
        target
    )

    exception_terms = [
        "DEVIATION",
        "BREAKDOWN",
        "REJECT",
        "REWORK",
        "REDO",
        "RE-PERFORM",
        "REPERFORM",
        "AGAIN",
        "NOT COMPLETED",
        "NOT DONE"
    ]

    return any(
        term in label
        for term in exception_terms
    )


def node_has_retry_outgoing(graph, node_id):

    return any(
        edge.edge_type == "LOOPBACK"
        or edge.routing_role == "LOOPBACK"
        for edge in graph.adjacency_map.get(
            node_id,
            []
        )
    )


def is_manual_exception_status_node(graph, node):

    if not node or node.type != "SYSTEM_ACTIVITY":

        return False

    if node.group == "ERROR_HANDLING":

        return False

    label = node_label(
        node
    )

    status_terms = [
        "NOT COMPLETED",
        "NOT COMPLETE",
        "NOT DONE",
        "INCOMPLETE",
        "NOT COMPLY",
        "DOES NOT COMPLY"
    ]

    exception_terms = [
        "BREAKDOWN",
        "CLEANING",
        "DEVIATION",
        "MAINTENANCE",
        "REJECT",
        "REWORK",
        "CORRECTION"
    ]

    return (
        any(
            term in label
            for term in status_terms
        )
        and any(
            term in label
            for term in exception_terms
        )
        and node_has_retry_outgoing(
            graph,
            node.id
        )
    )


def is_linked_workflow_node(node):

    label = node_label(
        node
    )

    linked_workflow_terms = [
        "LINKED WORKFLOW",
        "DEVIATION WORKFLOW",
        "LAUNCH DEVIATION"
    ]

    return any(
        term in label
        for term in linked_workflow_terms
    )


def is_system_automation_label(label):

    automation_prefixes = [
        "GET ",
        "CHECK ",
        "SET ",
        "CALCULATE ",
        "VALIDATE ",
        "GENERATE ",
        "CREATE ",
        "UPDATE ",
        "SAVE ",
        "POST ",
        "SEND ",
        "RETRIEVE ",
        "FETCH "
    ]

    return any(
        label.startswith(prefix)
        for prefix in automation_prefixes
    )


def is_manual_presentation_or_status_node(node):

    if not node or node.type != "SYSTEM_ACTIVITY":

        return False

    if node.group == "ERROR_HANDLING":

        return False

    if is_linked_workflow_node(
        node
    ):

        return False

    label = node_label(
        node
    )

    if is_system_automation_label(
        label
    ):

        return False

    presentation_terms = [
        "DISPLAY ",
        "PRESENT ",
        "SHOW "
    ]

    presentation_objects = [
        "INSTRUCTION",
        "INSTRUCTIONS",
        "PROCEDURE",
        "DETAILS",
        "MESSAGE"
    ]

    if (
        any(
            label.startswith(term)
            for term in presentation_terms
        )
        and any(
            term in label
            for term in presentation_objects
        )
    ):

        return False

    status_phrases = [
        "ALL ",
        "INDICATE ",
        "CONFIRM ",
        "RECORD "
    ]

    status_terms = [
        "PERFORMED",
        "COMPLETED",
        "COMPLETE",
        "DONE"
    ]

    return (
        any(
            label.startswith(phrase)
            for phrase in status_phrases
        )
        and any(
            term in label
            for term in status_terms
        )
    )


def normalize_node_types(graph):

    for node in graph.nodes.values():

        if is_manual_exception_status_node(
            graph,
            node
        ):

            node.metadata = {
                **node.metadata,
                "original_type": node.type,
                "type_normalization_reason": "manual_exception_status_retry"
            }

            node.type = "MANUAL_ACTIVITY"

            continue

        if is_manual_presentation_or_status_node(
            node
        ):

            node.metadata = {
                **node.metadata,
                "original_type": node.type,
                "type_normalization_reason": "manual_presentation_or_status"
            }

            node.type = "MANUAL_ACTIVITY"


def is_state_decision_response_branch(graph, edge, label):

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

    if target_node.type != "RESPONSE":

        return False

    state_terms = [
        "ALREADY",
        "DUPLICATE",
        "EXISTS",
        "EXISTING",
        "PREVIOUSLY",
        "CURRENTLY"
    ]

    return any(
        term in label
        for term in state_terms
    )


def normalize_edge_routing(graph, edge):

    if edge.edge_type != "CONDITIONAL":

        return

    label = edge_label(
        edge
    )

    if not label:

        return

    declared_role = explicit_routing_role(
        edge
    )

    if is_terminal_target(
        graph,
        edge
    ):

        edge.routing_role = "TERMINAL"

        return

    if declared_role == "LOOPBACK":

        edge.edge_type = "LOOPBACK"
        edge.routing_role = "LOOPBACK"

        return

    if is_response_backward_branch(
        graph,
        edge
    ):

        edge.edge_type = "LOOPBACK"
        edge.routing_role = "LOOPBACK"

        return

    if is_human_response_retry_loop(
        graph,
        edge,
        label
    ):

        edge.edge_type = "LOOPBACK"
        edge.routing_role = "LOOPBACK"

        return

    if is_local_retry_continuation(
        graph,
        edge,
        label
    ):

        edge.routing_role = "LOCAL_CONTINUATION"

        return

    if is_applicability_bypass_branch(
        graph,
        edge,
        label
    ):

        edge.routing_role = "SIDE_BRANCH"

        return

    if is_applicability_main_branch(
        graph,
        edge,
        label
    ):

        edge.routing_role = "SUCCESS"

        return

    if (
        declared_role == "SUCCESS"
        and not is_backward_edge(
            graph,
            edge
        )
    ):

        edge.routing_role = "SUCCESS"

        return

    if (
        is_state_decision_response_branch(
            graph,
            edge,
            label
        )
    ):

        edge.routing_role = "SIDE_BRANCH"

        return

    if (
        declared_role == "ERROR"
        and not is_restart_loop_label(
            label
        )
        and not is_neutral_valid_outcome(
            label
        )
    ):

        edge.routing_role = "ERROR"

        return

    if (
        is_normal_success_outcome(
            label
        )
        and not is_backward_edge(
            graph,
            edge
        )
    ):

        edge.routing_role = "SUCCESS"

        return

    if is_business_option_branch(
        graph,
        edge,
        label
    ):

        edge.routing_role = "SIDE_BRANCH"

        return

    if is_structural_retry_branch(
        graph,
        edge
    ):

        edge.routing_role = "ERROR"

        return

    if is_neutral_retry_error_branch(
        graph,
        edge,
        label
    ):

        edge.routing_role = "ERROR"

        return

    if (
        is_neutral_valid_outcome(
            label
        )
        and not is_backward_edge(
            graph,
            edge
        )
    ):

        edge.routing_role = (
            "SIDE_BRANCH"
            if is_valid_side_branch(
                label
            )
            else "SUCCESS"
        )

        return

    if (
        is_failure_outcome(
            label
        )
        or target_is_exception_work(
            graph,
            edge
        )
    ):

        edge.routing_role = "ERROR"

        return

    if edge.routing_role in [
        None,
        "ERROR"
    ]:

        edge.routing_role = "SUCCESS"


def normalize_structural_backward_edges(graph):

    for edge in graph.edges:

        if edge.edge_type == "CONDITIONAL":

            continue

        if edge.edge_type == "LOOPBACK":

            edge.routing_role = "LOOPBACK"

            continue

        if not is_backward_edge(
            graph,
            edge
        ):

            continue

        source_node = graph.get_node(
            edge.source
        )

        target_node = graph.get_node(
            edge.target
        )

        if not source_node or not target_node:

            continue

        if target_node.type in [
            "END",
            "MERGE"
        ]:

            continue

        edge.edge_type = "LOOPBACK"
        edge.routing_role = "LOOPBACK"


def is_same_source_retry_failure_candidate(graph, edge):

    if edge.edge_type != "CONDITIONAL":

        return False

    if is_terminal_target(
        graph,
        edge
    ):

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
        "MERGE"
    ]:

        return False

    label = edge_label(
        edge
    )

    if is_state_decision_response_branch(
        graph,
        edge,
        label
    ):

        return False

    if (
        explicit_routing_role(
            edge
        ) == "SUCCESS"
        or is_normal_success_outcome(
            label
        )
    ):

        return False

    if (
        is_restart_loop_label(
            label
        )
        or is_neutral_valid_outcome(
            label
        )
    ):

        return False

    if not has_backward_retry_from_node(
        graph,
        edge.target,
        edge
    ):

        return False

    target_label = node_label(
        target_node
    )

    return (
        edge.routing_role == "ERROR"
        or is_failure_outcome(
            label
        )
        or is_failure_outcome(
            target_label
        )
        or target_is_exception_work(
            graph,
            edge
        )
        or node_has_retry_outgoing(
            graph,
            edge.target
        )
    )


def promote_same_source_retry_failures(graph):

    candidates_by_source = {}

    for edge in graph.edges:

        if not is_same_source_retry_failure_candidate(
            graph,
            edge
        ):

            continue

        candidates_by_source.setdefault(
            edge.source,
            []
        ).append(
            edge
        )

    for edges in candidates_by_source.values():

        if len(
            edges
        ) < 2:

            continue

        for edge in edges:

            edge.routing_role = "ERROR"


def collect_exception_nodes(graph):

    roots = [
        edge.target
        for edge in graph.edges
        if edge.routing_role in [
            "ERROR",
            "LOCAL_CONTINUATION"
        ]
    ]

    visited = set()

    queue = list(
        roots
    )

    while queue:

        node_id = queue.pop(0)

        if node_id in visited:

            continue

        visited.add(
            node_id
        )

        for edge in graph.adjacency_map.get(
            node_id,
            []
        ):

            if (
                edge.edge_type == "LOOPBACK"
                or edge.routing_role == "LOOPBACK"
                or is_restart_loop_label(
                    edge_label(
                        edge
                    )
                )
            ):

                continue

            if edge.routing_role == "SUCCESS":

                incoming = graph.reverse_adjacency_map.get(
                    edge.target,
                    []
                )

                if len(
                    [
                        incoming_edge
                        for incoming_edge in incoming
                        if incoming_edge.edge_type != "LOOPBACK"
                    ]
                ) > 1:

                    continue

            queue.append(
                edge.target
            )

    return visited


def refine_exception_local_continuations(graph):

    exception_nodes = collect_exception_nodes(
        graph
    )

    for edge in graph.edges:

        if edge.edge_type != "CONDITIONAL":

            continue

        label = edge_label(
            edge
        )

        if is_exception_local_continuation(
            graph,
            edge,
            label,
            exception_nodes
        ):

            edge.routing_role = "LOCAL_CONTINUATION"


def next_system_activity_id(graph):

    max_index = 0

    for node_id in graph.nodes:

        if not node_id.startswith(
            "SA"
        ):

            continue

        suffix = node_id[2:]

        if not suffix.isdigit():

            continue

        max_index = max(
            max_index,
            int(
                suffix
            )
        )

    return f"SA{max_index + 1}"


def is_simple_response_option(label):

    simple_options = {
        "YES",
        "Y",
        "NO",
        "N",
        "VALID",
        "INVALID",
        "CORRECT",
        "INCORRECT",
        "TRUE",
        "FALSE",
        "PASS",
        "FAIL",
        "SUCCESS",
        "DONE",
        "COMPLETE",
        "EXIT",
        "FINISH"
    }

    return label in simple_options


def is_display_message_outcome(label):

    if not label or is_simple_response_option(
        label
    ):

        return False

    message_terms = [
        "ALREADY",
        "SCANNED",
        "MISMATCH",
        "NOT FOUND",
        "NOT AVAILABLE",
        "NOT VALID",
        "INVALID",
        "INCORRECT",
        "FAILED",
        "FAIL",
        "EXPIRED",
        "DUE",
        "BLOCKED",
        "EXISTS",
        "LIMIT",
        "ABOVE",
        "BELOW"
    ]

    return any(
        term in label
        for term in message_terms
    )


def display_message_node_exists(
    graph,
    edge,
    label
):

    for outgoing_edge in graph.adjacency_map.get(
        edge.source,
        []
    ):

        candidate = graph.get_node(
            outgoing_edge.target
        )

        if not candidate or candidate.type != "SYSTEM_ACTIVITY":

            continue

        if node_label(
            candidate
        ) != label:

            continue

        if any(
            next_edge.target == edge.target
            for next_edge in graph.adjacency_map.get(
                candidate.id,
                []
            )
        ):

            return True

    return False


def should_expand_display_message_edge(
    graph,
    edge
):

    if edge.edge_type == "LOOPBACK" or edge.routing_role == "LOOPBACK":

        return False

    source = graph.get_node(
        edge.source
    )

    target = graph.get_node(
        edge.target
    )

    if not source or not target:

        return False

    if source.type != "RESPONSE" or target.type != "RESPONSE":

        return False

    if source.response_actor != "SYSTEM":

        return False

    if target.response_actor == "SYSTEM":

        return False

    label = edge_label(
        edge
    )

    if not is_display_message_outcome(
        label
    ):

        return False

    return not display_message_node_exists(
        graph,
        edge,
        label
    )


def expand_display_message_edges(graph):

    graph.build_maps()

    expanded_edges = []

    changed = False

    for edge in graph.edges:

        if not should_expand_display_message_edge(
            graph,
            edge
        ):

            expanded_edges.append(
                edge
            )

            continue

        message_node_id = next_system_activity_id(
            graph
        )

        label = (
            edge.condition
            or edge.edge_label
            or message_node_id
        )

        graph.nodes[message_node_id] = WorkflowNode(
            id=message_node_id,
            type="SYSTEM_ACTIVITY",
            label=label,
            step_number=message_node_id,
            lane="MAIN",
            group="GENERAL",
            metadata={
                "generated_display_message": True,
                "semantic_source": edge.source,
                "semantic_target": edge.target
            }
        )

        expanded_edges.append(
            WorkflowEdge(
                source=edge.source,
                target=message_node_id,
                edge_type="CONDITIONAL",
                condition=edge.condition,
                routing_role="SIDE_BRANCH",
                edge_label=edge.edge_label,
                metadata={
                    **edge.metadata,
                    "expanded_display_message": True
                }
            )
        )

        expanded_edges.append(
            WorkflowEdge(
                source=message_node_id,
                target=edge.target,
                edge_type="SEQUENCE",
                routing_role="MAIN_FLOW",
                metadata={
                    "display_message_continuation": True
                }
            )
        )

        changed = True

    if changed:

        graph.edges = expanded_edges

        graph.build_maps()


def non_loopback_incoming(graph, node_id):

    return [
        edge
        for edge in graph.reverse_adjacency_map.get(
            node_id,
            []
        )
        if edge.edge_type != "LOOPBACK"
        and edge.routing_role != "LOOPBACK"
    ]


def forward_success_targets(graph, response_id):

    result = []

    for edge in graph.adjacency_map.get(
        response_id,
        []
    ):

        if edge.routing_role not in [
            "SUCCESS",
            "LOCAL_CONTINUATION"
        ]:

            continue

        if not is_forward_edge(
            graph,
            edge
        ):

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


def branch_origin_response_candidates(graph, node_id):

    result = []
    visited = set()
    queue = [
        node_id
    ]

    while queue:

        current_id = queue.pop(
            0
        )

        if current_id in visited:

            continue

        visited.add(
            current_id
        )

        for incoming_edge in non_loopback_incoming(
            graph,
            current_id
        ):

            source = graph.get_node(
                incoming_edge.source
            )

            if not source:

                continue

            if source.type == "RESPONSE":

                success_targets = forward_success_targets(
                    graph,
                    source.id
                )

                if success_targets:

                    result.append(
                        (
                            source.id,
                            success_targets
                        )
                    )

            if incoming_edge.routing_role in [
                "ERROR",
                "SIDE_BRANCH",
                "SUCCESS",
                "LOCAL_CONTINUATION",
                "MAIN_FLOW"
            ]:

                queue.append(
                    incoming_edge.source
                )

    return result


def is_generated_display_message_node(node):

    return bool(
        node
        and getattr(
            node,
            "metadata",
            {}
        ).get(
            "generated_display_message"
        )
    )


def is_retargetable_side_branch_continuation(graph, edge):

    if getattr(
        edge,
        "metadata",
        {}
    ).get(
        "display_message_continuation"
    ):

        return True

    source = graph.get_node(
        edge.source
    )

    return is_generated_display_message_node(
        source
    )


def retarget_side_branch_continuations(graph):

    changed = False

    for edge in graph.edges:

        if edge.edge_type == "LOOPBACK" or edge.routing_role == "LOOPBACK":

            continue

        if edge.routing_role not in [
            "MAIN_FLOW",
            "SUCCESS",
            "LOCAL_CONTINUATION"
        ]:

            continue

        if not is_retargetable_side_branch_continuation(
            graph,
            edge
        ):

            continue

        source_index = target_index(
            graph,
            edge.source
        )

        target_index_value = target_index(
            graph,
            edge.target
        )

        if source_index is None or target_index_value is None:

            continue

        if target_index_value <= source_index:

            continue

        source = graph.get_node(
            edge.source
        )

        target = graph.get_node(
            edge.target
        )

        if not source or not target or target.type in [
            "END",
            "MERGE"
        ]:

            continue

        candidate_targets = []

        for _origin_response_id, success_targets in branch_origin_response_candidates(
            graph,
            edge.source
        ):

            for candidate_id in success_targets:

                candidate_index = target_index(
                    graph,
                    candidate_id
                )

                if candidate_index is None:

                    continue

                if source_index < candidate_index < target_index_value:

                    candidate_targets.append(
                        (
                            candidate_index,
                            candidate_id
                        )
                    )

        if not candidate_targets:

            continue

        candidate_targets.sort()
        rejoin_target = candidate_targets[0][1]

        if rejoin_target == edge.target:

            continue

        edge.target = rejoin_target
        edge.metadata = {
            **edge.metadata,
            "retargeted_side_branch_continuation": True,
            "original_target": target.id
        }
        changed = True

    if changed:

        graph.build_maps()


def normalize_graph_routing(graph):

    graph.metadata = getattr(
        graph,
        "metadata",
        {}
    )

    graph.metadata["node_order"] = {
        node_id: index
        for index, node_id in enumerate(
            graph.nodes.keys()
        )
    }

    normalize_node_types(
        graph
    )

    graph.build_maps()

    for edge in graph.edges:

        normalize_edge_routing(
            graph,
            edge
        )

    normalize_structural_backward_edges(
        graph
    )

    promote_same_source_retry_failures(
        graph
    )

    refine_exception_local_continuations(
        graph
    )

    promote_same_source_retry_failures(
        graph
    )

    expand_display_message_edges(
        graph
    )

    graph.build_maps()

    retarget_side_branch_continuations(
        graph
    )

    graph.build_maps()

    return graph
