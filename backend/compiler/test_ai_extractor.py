import json

from compiler.ai_workflow_extractor import (
    extract_workflow
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)

from engines.topology_layout_engine import build_topology_layout


if __name__ == "__main__":

    with open(
    "test_workflows/startup_checks.txt",
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

    with open(
    "../frontend/src/data/test_graph.json",
    "w",
    encoding="utf-8"
    ) as f:

        json.dump(
        reactflow_graph,
        f,
        indent=4
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