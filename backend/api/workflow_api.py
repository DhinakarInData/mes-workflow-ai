from fastapi import APIRouter

from compiler.workflow_parser import (
    parse_workflow
)

from compiler.layout_engine import (
    build_layout
)

from compiler.reactflow_adapter import (
    build_reactflow_graph
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

        "workflow_schema.json"
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

    node_positions = build_layout(
        graph
    )


    # ===================================
    # BUILD REACTFLOW GRAPH
    # ===================================

    reactflow_graph = build_reactflow_graph(

        graph,

        node_positions
    )


    return reactflow_graph