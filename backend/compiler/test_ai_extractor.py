import json
from pathlib import Path

from compiler.ai_workflow_extractor import (
    extract_workflow
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)

from engines.topology_layout_engine import build_topology_layout


if __name__ == "__main__":

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

    with open(
    "test_workflows/09_dispensing_exception_review.txt",
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
