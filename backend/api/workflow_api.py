from fastapi import APIRouter

from compiler.workflow_parser import (
    parse_workflow
)
from engines.topology_layout_engine import (
    build_topology_layout
)

from compiler.reactflow_adapter import (
    build_reactflow_graph
)
from compiler.semantic_engine import (
    find_semantic_clusters
)

import os


router = APIRouter()


# ===================================
# GET WORKFLOW GRAPH
# ===================================

@router.get("/workflow")


def get_workflow_graph():

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
    # PARSE GRAPH
    # ===================================

    graph = parse_workflow(
        workflow_path
    )


    # ===================================
    # BUILD LAYOUT
    # ===================================

    node_positions = build_topology_layout(
        graph
    )


    # ===================================
    # BUILD REACTFLOW GRAPH
    # ===================================
    semantic_clusters = find_semantic_clusters(
        graph
    )

    semantic_groups = {}

    for group_name, nodes in semantic_clusters.items():

        semantic_groups[group_name] = [

        node.id for node in nodes
    ]
    
    reactflow_graph = build_reactflow_graph(

        graph,

        node_positions,
        semantic_groups
    )


    return reactflow_graph