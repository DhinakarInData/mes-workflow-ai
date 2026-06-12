
import os

from compiler.merge_engine import (
    inject_merge_nodes
)
from compiler.grouping_engine import (

    build_semantic_groups,

    print_group_report
)
from compiler.connector_engine import (
    inject_loopback_connectors
)
from engines.topology_layout_engine import (
    build_topology_layout,
    print_topology_layout
)
from compiler.layout_engine import (

    build_layout,

    print_layout_report
)
from compiler.reactflow_adapter import (

    build_reactflow_graph,

    print_reactflow_report
)

from compiler.merge_engine import (
    inject_merge_nodes
)
from compiler.normalization_engine import (
    print_ir_report
)
from compiler.topology_engine import (
    print_topology_report
)

from compiler.semantic_engine import (
    print_semantic_report
)

from compiler.workflow_parser import (
    parse_workflow
)

from compiler.graph_analyzer import (
    print_graph_summary,
    bfs_traversal,
    find_merge_nodes,
    find_decision_nodes,
    find_loopback_edges
)


# ===================================
# BUILD WORKFLOW GRAPH
# ===================================

def build_graph():

    # ===================================
    # WORKFLOW PATH
    # ===================================

    current_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    workflow_path = os.path.join(
        current_dir,
        "..",
        "schemas",
        "fds_nway_test.json"
    )

    # ===================================
    # PARSE DSL
    # ===================================

    graph = parse_workflow(
    workflow_path
    )

    graph = inject_merge_nodes(
    graph
    )

    graph = inject_loopback_connectors(
    graph
    )
    print_semantic_report(
    graph
)
    semantic_groups = build_semantic_groups(
        graph
    )
    print_group_report(

        graph,

    semantic_groups
    )
    # ===================================
    # GRAPH SUMMARY
    # ===================================

    print_graph_summary(graph)

    # ===================================
    # TOPOLOGY REPORT
    # ===================================

    print_topology_report(graph)

    # ===================================
    # SEMANTIC REPORT
    # ===================================

    print_semantic_report(graph)
    
    print_ir_report(graph)
    
    node_positions = build_topology_layout(
    graph
)

    print_topology_layout(
        graph,
        node_positions
)

  
    print_layout_report(
            graph,
            node_positions
    )
    reactflow_graph = build_reactflow_graph(

        graph,

        node_positions,
        semantic_groups
    )

    print_reactflow_report(
        reactflow_graph
    )
    # ===================================
    # BFS ORDER
    # ===================================

    traversal_order = bfs_traversal(graph)

    print("\n===== BFS ORDER =====\n")

    for node_id in traversal_order:

        print(node_id)

    # ===================================
    # DECISION ANALYSIS
    # ===================================

    print("\n===== DECISION ANALYSIS =====\n")

    decision_nodes = find_decision_nodes(
        graph
    )

    for node in decision_nodes:

        outgoing = graph.adjacency_map.get(
            node.id,
            []
        )

        print(
            f"\n{node.id} | {node.label}"
        )

        print("Outgoing Branches:")

        for edge in outgoing:

            print(
                "  ->",
                edge.target,
                "|",
                edge.edge_type,
                "|",
                edge.condition
            )

    # ===================================
    # MERGE ANALYSIS
    # ===================================

    print("\n===== MERGE ANALYSIS =====\n")

    merge_nodes = find_merge_nodes(graph)

    for node in merge_nodes:

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )

        print(
            f"\n{node.id} | {node.label}"
        )

        print("Incoming Paths:")

        for edge in incoming:

            print(
                "  <-",
                edge.source,
                "|",
                edge.edge_type,
                "|",
                edge.condition
            )

    # ===================================
    # LOOPBACK ANALYSIS
    # ===================================

    print("\n===== LOOPBACK ANALYSIS =====\n")

    loopbacks = find_loopback_edges(graph)

    for edge in loopbacks:

        print(
            edge.source,
            "->",
            edge.target,
            "|",
            edge.condition
        )

    # ===================================
    # RETURN GRAPH
    # ===================================

    return graph


# ===================================
# TEST GRAPH BUILDER
# ===================================

if __name__ == "__main__":

    build_graph()