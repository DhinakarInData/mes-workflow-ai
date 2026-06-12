from compiler.ir_loader import (
    load_ir
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)


if __name__ == "__main__":

    ir = load_ir(
        "schemas/sample_bin_picking_ir.json"
    )

    graph = build_graph_from_ir(
        ir
    )

    print(
        "Nodes:",
        len(graph.nodes)
    )

    print(
        "Edges:",
        len(graph.edges)
    )

    start_node = graph.get_start_node()

    print(
        "Start:",
        start_node.id
    )