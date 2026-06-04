import json

from models.workflow_models import (

    WorkflowNode,

    WorkflowEdge,

    WorkflowGraph
)


# ===================================
# PARSE WORKFLOW DSL
# ===================================

def parse_workflow(
    file_path
):

    # ===================================
    # LOAD JSON
    # ===================================

    with open(
        file_path,
        "r"
    ) as file:

        data = json.load(file)


    # ===================================
    # PARSE NODES
    # ===================================

    workflow_nodes = {}


    for node_data in data["nodes"]:

        node = WorkflowNode(

            id=node_data["id"],

            type=node_data["type"],

            label=node_data["label"],

            step_number=node_data["step_number"],

            lane=node_data["lane"],

            group=node_data["group"],

            actor=node_data.get(
                "actor"
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


    # ===================================
    # PARSE EDGES
    # ===================================

    workflow_edges = []


    for edge_data in data["edges"]:

        edge = WorkflowEdge(

    source=edge_data["source"],

    target=edge_data["target"],

    edge_type=edge_data["edge_type"],

    condition=edge_data.get(
        "condition"
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


    # ===================================
    # BUILD WORKFLOW GRAPH
    # ===================================

    graph = WorkflowGraph(

        nodes=workflow_nodes,

        edges=workflow_edges
    )


    # ===================================
    # BUILD GRAPH MAPS
    # ===================================

    graph.build_maps()


    # ===================================
    # RETURN GRAPH
    # ===================================

    return graph


# ===================================
# TEST PARSER
# ===================================

if __name__ == "__main__":

    graph = parse_workflow(

        "workflow_schema.json"
    )


    print("\n===== WORKFLOW NODES =====\n")


    for node_id, node in graph.nodes.items():

        print(

            node_id,

            "->",

            node.type,

            "|",

            node.label
        )


    print("\n===== WORKFLOW EDGES =====\n")


    for edge in graph.edges:

        print(

            edge.source,

            "->",

            edge.target,

            "|",

            edge.edge_type,

            "|",

            edge.condition
        )


    print("\n===== ADJACENCY MAP =====\n")


    for node_id, edges in graph.adjacency_map.items():

        print(

            node_id,

            "=>",

            [

                edge.target

                for edge in edges
            ]
        )