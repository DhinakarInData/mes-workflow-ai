import json
from compiler.graph_model import (
    GraphNode,
    GraphEdge,
    Connector
)

from compiler.validator import (
    validate_workflow_schema
)

from compiler.adapter import (
    graph_to_reactflow
)

def build_graph():

    with open(
        "schemas/workflow_schema.json",
        "r"
    ) as file:

        data = json.load(file)


    validate_workflow_schema(data)


    graph_nodes = []
    graph_edges = []
    graph_connectors = []


    # =========================
    # CREATE GRAPH NODES
    # =========================

    for node in data["nodes"]:

        graph_node = GraphNode(
            id=node["id"],
            step_number=node["step_number"],
            type=node["type"],
            label=node["label"],
            lane=node["lane"],
            group=node["group"]
        )

        graph_nodes.append(graph_node)


    # =========================
    # CREATE GRAPH EDGES
    # =========================

    for edge in data["edges"]:

        graph_edge = GraphEdge(
            source=edge["source"],
            target=edge["target"],
            edge_type=edge["edge_type"]
        )

        graph_edges.append(graph_edge)


    # =========================
    # CREATE CONNECTORS
    # =========================

    for connector in data["connectors"]:

        graph_connector = Connector(
            id=connector["id"],
            source=connector["source"],
            target=connector["target"],
            connector_type=connector["type"]
        )

        graph_connectors.append(graph_connector)


    return {
        "nodes": graph_nodes,
        "edges": graph_edges,
        "connectors": graph_connectors
    }


if __name__ == "__main__":

    graph = build_graph()

    reactflow_graph = graph_to_reactflow(
    graph
)

with open(
    "../frontend/public/graph.json",
    "w"
) as file:

    json.dump(
        reactflow_graph,
        file,
        indent=4
    )

print("graph.json generated")