from models.workflow_models import (
    WorkflowNode,
    WorkflowEdge
)


def inject_merge_nodes(graph):
    print("MERGE ENGINE RUNNING")

    target_map = {}

    # ===================================
    # COLLECT LOOPBACKS BY TARGET
    # ===================================

    for edge in graph.edges:

        if edge.edge_type == "LOOPBACK":

            target_map.setdefault(
                edge.target,
                []
            ).append(edge)

    merge_counter = 1

    # ===================================
    # PROCESS TARGETS
    # ===================================

    for target_id, loopbacks in target_map.items():

        if len(loopbacks) <= 1:
            continue

        merge_node = WorkflowNode(

            id=f"MERGE_{merge_counter}",

            type="MERGE",

            label="",

            step_number=f"MERGE_{merge_counter}",

            lane="MAIN",

            group="MERGE"
        )

        graph.nodes[
            merge_node.id
        ] = merge_node

        # ===================================
        # REMOVE ORIGINAL LOOPBACKS
        # ===================================

        graph.edges = [

            edge

            for edge in graph.edges

            if edge not in loopbacks
        ]

        # ===================================
        # SOURCE -> MERGE
        # ===================================

        for loopback_edge in loopbacks:

            graph.edges.append(

                WorkflowEdge(

                    source=loopback_edge.source,

                    target=merge_node.id,

                    edge_type="SEQUENCE",

                    condition=loopback_edge.condition,

                    routing_role="MAIN_FLOW",

                    edge_label=(
                        loopback_edge.edge_label
                        or loopback_edge.condition
                    ),

                    metadata={
                        **(
                            loopback_edge.metadata
                            or {}
                        ),
                        "merge_incoming_loopback": True,
                        "semantic_target": loopback_edge.target
                    }
                )
            )

        # ===================================
        # MERGE -> TARGET
        # ===================================

        graph.edges.append(

            WorkflowEdge(

                source=merge_node.id,

                target=target_id,

                edge_type="LOOPBACK",

                routing_role="LOOPBACK"
            )
        )

        merge_counter += 1

    # ===================================
    # REBUILD MAPS
    # ===================================

    graph.build_maps()

    return graph
