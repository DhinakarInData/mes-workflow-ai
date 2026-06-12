from compiler.ir_loader import (
    load_ir
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)

from compiler.layout_engine import (
    build_layout
)


if __name__ == "__main__":

    ir = load_ir(
        "schemas/sample_bin_picking_ir.json"
    )

    graph = build_graph_from_ir(
        ir
    )

    node_positions = build_layout(
        graph
    )

    print(
        "\n===== IR LAYOUT =====\n"
    )

    for node_id, pos in node_positions.items():

        print(
            node_id,
            pos
        )