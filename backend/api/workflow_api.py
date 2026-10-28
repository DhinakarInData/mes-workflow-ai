import json
import os

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from compiler.workflow_parser import (
    parse_workflow
)
from compiler.ir_to_graph import (
    build_graph_from_ir
)
from compiler.ir_validator import (
    validate_ir
)
from compiler.merge_engine import (
    inject_merge_nodes
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

router = APIRouter()

MAX_WORKFLOW_TEXT_LENGTH = 20000


class WorkflowGenerationRequest(BaseModel):
    workflow_text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_WORKFLOW_TEXT_LENGTH
    )


def _extract_workflow(workflow_text):
    from compiler.ai_workflow_extractor import (
        extract_workflow
    )

    return extract_workflow(
        workflow_text,
        write_debug=False
    )


@router.post("/workflow/generate")
def generate_workflow_graph(request: WorkflowGenerationRequest):
    workflow_text = request.workflow_text.strip()

    if not workflow_text:
        raise HTTPException(
            status_code=422,
            detail="workflow_text must not be blank."
        )

    try:
        extracted_ir = _extract_workflow(workflow_text)
        ir = (
            json.loads(extracted_ir)
            if isinstance(extracted_ir, str)
            else extracted_ir
        )

        if (
            not isinstance(ir, dict)
            or not isinstance(ir.get("nodes"), list)
            or not isinstance(ir.get("edges"), list)
        ):
            raise ValueError("Extractor returned an invalid workflow.")

        if validate_ir(ir):
            raise ValueError("Extractor returned an invalid workflow.")

        graph = build_graph_from_ir(ir)
        graph = inject_merge_nodes(graph)
        node_positions = build_topology_layout(graph)

        semantic_clusters = find_semantic_clusters(graph)
        semantic_groups = {
            group_name: [
                node.id
                for node in nodes
            ]
            for group_name, nodes in semantic_clusters.items()
        }

        return build_reactflow_graph(
            graph,
            node_positions,
            semantic_groups
        )
    except HTTPException:
        raise
    except ValueError as error:
        raise HTTPException(
            status_code=502,
            detail="Workflow extraction returned invalid workflow data."
        ) from error
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail="Workflow generation failed."
        ) from error


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