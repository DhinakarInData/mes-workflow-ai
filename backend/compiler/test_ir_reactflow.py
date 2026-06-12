from compiler.ir_loader import load_ir
from compiler.ir_to_graph import build_graph_from_ir
from compiler.layout_engine import build_layout
from compiler.reactflow_adapter import (
    build_reactflow_graph
)

if __name__ == "__main__":

    ir = load_ir(
        "schemas/sample_bin_picking_ir.json"
    )

    graph = build_graph_from_ir(ir)

    node_positions = build_layout(graph)

    reactflow_graph = build_reactflow_graph(

        graph,

        node_positions,

        {}
    )

    print(
        "Nodes:",
        len(
            reactflow_graph["nodes"]
        )
    )

    print(
        "Edges:",
        len(
            reactflow_graph["edges"]
        )
    )