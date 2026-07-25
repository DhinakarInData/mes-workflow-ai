import json
import argparse
from pathlib import Path

from compiler.ai_workflow_extractor import (
    extract_workflow
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)

from engines.topology_layout_engine import build_topology_layout


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Generate ReactFlow JSON from a test workflow input."
    )
    parser.add_argument(
        "workflow_file",
        nargs="?",
        default="test_workflows/11_line_reconciliation_with_rework.txt",
        help=(
            "Workflow text file path. Relative paths are resolved from "
            "the backend folder."
        )
    )
    args = parser.parse_args()

    backend_dir = Path(
        __file__
    ).resolve().parents[1]

    project_root = backend_dir.parent

    output_path = (
        project_root
        / "frontend"
        / "src"
        / "data"
        / "test_graph.json"
    )

    workflow_path = Path(
        args.workflow_file
    )

    if not workflow_path.is_absolute():

        workflow_path = backend_dir / workflow_path

    with workflow_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        workflow_text = file.read()

    import json

    response = extract_workflow(
        workflow_text
)

    print(
    "\nAI RESPONSE\n"
)

    print(response)

    ir = json.loads(
        response
    )

    print(response)

    print(
        "\nIR Generated"
    )

    graph = build_graph_from_ir(
    ir
)

    from compiler.merge_engine import (
        inject_merge_nodes
    )

    graph = inject_merge_nodes(
        graph
)

    print(
        "Graph Created"
    )

    layout = build_topology_layout(
        graph
    )

    print(
        "Layout Created"
    )
    from compiler.reactflow_adapter import (
    build_reactflow_graph
)

    reactflow_graph = build_reactflow_graph(
    graph,
    layout,
    []
)

    from compiler.fds_stability_validator import (
        validate_reactflow_graph
    )

    violations = validate_reactflow_graph(
        reactflow_graph
    )

    from compiler.fds_visual_validator import (
        format_fds_visual_report,
        validate_fds_visual_layout
    )

    visual_issues = validate_fds_visual_layout(
        reactflow_graph
    )

    print(
        "\n" + format_fds_visual_report(
            visual_issues
        )
    )

    blocking_violations = [
        violation
        for violation in violations
        if violation.get(
            "severity"
        ) == "error"
    ]

    if blocking_violations:

        print(
            "\nFDS layout stability validation failed"
        )

        for violation in blocking_violations[:20]:

            print(
                f"- {violation.get('rule')}: "
                f"{violation.get('message')}"
            )

        raise RuntimeError(
            "ReactFlow JSON was not written because FDS layout "
            "stability invariants failed"
        )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temp_output_path = output_path.with_suffix(
        output_path.suffix + ".tmp"
    )

    with temp_output_path.open(
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
        reactflow_graph,
        f,
        indent=4,
        allow_nan=False
    )

    temp_output_path.replace(
        output_path
    )

    print(
    "ReactFlow JSON Generated"
)
    print(
        "\nNodes:",
        len(graph.nodes)
    )

    print(
        "Edges:",
        len(graph.edges)
    )

    print(
        "\nLayout:"
    )

    for node_id, pos in layout.items():

        print(
            node_id,
            pos
        )
