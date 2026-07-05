from models.workflow_models import (
    WorkflowNode,
    WorkflowEdge,
    WorkflowGraph
)
from compiler.semantic_routing_engine import (
    normalize_graph_routing
)


def normalize_text(value):

    return " ".join(
        str(
            value
            or ""
        )
        .upper()
        .replace(
            "_",
            " "
        )
        .split()
    )


def is_retry_helper_node(
    graph,
    node_id
):

    node = graph.get_node(
        node_id
    )

    if not node or node.type != "MANUAL_ACTIVITY":

        return False

    incoming = graph.reverse_adjacency_map.get(
        node_id,
        []
    )

    outgoing = graph.adjacency_map.get(
        node_id,
        []
    )

    if not incoming or len(
        outgoing
    ) != 1:

        return False

    if not all(
        edge.routing_role == "LOOPBACK"
        or edge.edge_type == "LOOPBACK"
        for edge in incoming
    ):

        return False

    outgoing_edge = outgoing[0]

    if outgoing_edge.routing_role not in [
        "MAIN_FLOW",
        None
    ]:

        return False

    label = normalize_text(
        node.label
    )

    if not label:

        return False

    same_step_candidates = [
        candidate
        for candidate in graph.nodes.values()
        if (
            candidate.id != node_id
            and candidate.type == "MANUAL_ACTIVITY"
            and normalize_text(
                candidate.label
            ) == label
            and any(
                candidate_edge.target == outgoing_edge.target
                for candidate_edge in graph.adjacency_map.get(
                    candidate.id,
                    []
                )
            )
        )
    ]

    return bool(
        same_step_candidates
    )


def original_retry_target(
    graph,
    helper_id
):

    helper = graph.get_node(
        helper_id
    )

    outgoing = graph.adjacency_map.get(
        helper_id,
        []
    )

    if not helper or len(
        outgoing
    ) != 1:

        return None

    next_target_id = outgoing[0].target

    candidates = [
        candidate
        for candidate in graph.nodes.values()
        if (
            candidate.id != helper_id
            and candidate.type == "MANUAL_ACTIVITY"
            and normalize_text(
                candidate.label
            ) == normalize_text(
                helper.label
            )
            and any(
                candidate_edge.target == next_target_id
                for candidate_edge in graph.adjacency_map.get(
                    candidate.id,
                    []
                )
            )
        )
    ]

    if not candidates:

        return None

    def candidate_sort_key(candidate):

        return (
            1
            if "RESCAN" in normalize_text(
                candidate.id
            )
            else 0,
            candidate.step_number
            or candidate.id
        )

    candidates.sort(
        key=candidate_sort_key
    )

    return candidates[0].id


def collapse_duplicate_retry_helpers(graph):

    graph.build_maps()

    helper_to_original = {}

    for node_id in list(
        graph.nodes
    ):

        if not is_retry_helper_node(
            graph,
            node_id
        ):

            continue

        original_id = original_retry_target(
            graph,
            node_id
        )

        if not original_id:

            continue

        helper_to_original[node_id] = original_id

    if not helper_to_original:

        return graph

    collapsed_edges = []

    seen_edges = set()

    for edge in graph.edges:

        if edge.source in helper_to_original:

            continue

        source = edge.source

        target = helper_to_original.get(
            edge.target,
            edge.target
        )

        metadata = dict(
            edge.metadata
            or {}
        )

        if edge.target in helper_to_original:

            metadata["collapsed_retry_helper"] = True

            metadata["helper_node_id"] = edge.target

            metadata["semantic_target"] = edge.target

        dedupe_key = (
            source,
            target,
            edge.edge_type,
            edge.condition,
            edge.routing_role,
            edge.edge_label
        )

        if dedupe_key in seen_edges:

            continue

        seen_edges.add(
            dedupe_key
        )

        collapsed_edges.append(
            WorkflowEdge(
                source=source,
                target=target,
                edge_type=edge.edge_type,
                condition=edge.condition,
                routing_role=edge.routing_role,
                edge_label=edge.edge_label,
                metadata=metadata
            )
        )

    for helper_id in helper_to_original:

        graph.nodes.pop(
            helper_id,
            None
        )

    graph.edges = collapsed_edges

    graph.build_maps()

    return graph


def build_graph_from_ir(ir):

    workflow_nodes = {}

    for node_data in ir["nodes"]:

        node = WorkflowNode(

            id=node_data["id"],

            type=node_data["type"],

            label=node_data["label"],

            step_number=node_data.get(
                "step_number",
                node_data["id"]
            ),

            lane=node_data.get(
                "lane",
                "MAIN"
            ),

            group=node_data.get(
                "group",
                "GENERAL"
            ),

            actor=node_data.get(
                "actor"
            ),
            response_actor=node_data.get(
                "response_actor"
            ),


            event_type=node_data.get(
                "event_type"
            ),
            
            metadata=node_data.get(
                "metadata",
                {}
            )
        )

        workflow_nodes[
            node.id
        ] = node

    workflow_edges = []

    for edge_data in ir["edges"]:

        edge = WorkflowEdge(

            source=edge_data["source"],

            target=edge_data["target"],

            edge_type=edge_data["edge_type"],

            condition=edge_data.get(
                "condition"
            ),

            routing_role=edge_data.get(
            "routing_role"
            ),

            edge_label=edge_data.get(
            "edge_label"
            ),

            metadata=edge_data.get(
            "metadata",
            {}
            )
        )
        workflow_edges.append(
            edge
        )

    graph = WorkflowGraph(

        nodes=workflow_nodes,

        edges=workflow_edges
    )

    graph.build_maps()

    graph = collapse_duplicate_retry_helpers(
        graph
    )

    return normalize_graph_routing(
        graph
    )
