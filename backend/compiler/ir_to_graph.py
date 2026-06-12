from models.workflow_models import (
    WorkflowNode,
    WorkflowEdge,
    WorkflowGraph
)


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

    return graph