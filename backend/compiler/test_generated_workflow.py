from compiler.workflow_interpreter import (
    generate_ir
)

from compiler.ir_to_graph import (
    build_graph_from_ir
)

from compiler.layout_engine import (
    build_layout
)

from compiler.reactflow_adapter import (
    build_reactflow_graph
)


if __name__ == "__main__":

    sample_text = """

    Gross Weight Verification

    Scan the area to perform Gross weight verification

    Scan the weighing scale 

    System check if its valid proceed to fetch the dispensed material details else show the error message and return to scan the scale



    User select the material

    User scan the material barcode

    System check if it valid go to read the scale value else show the error message and return to scan the material barcode

    Read the scale value 
    System check weighed qty matches dispensed qty if it ok show complies it if not ok show does not comply 

    then go to end of workflow

    """

    lines = sample_text.splitlines()

    ir = generate_ir(lines)

    print(
        "\nIR Generated"
    )

    graph = build_graph_from_ir(
        ir
    )

    print(
        "Graph Created"
    )

    positions = build_topology_layout(
        graph
    )

    print(
        "Layout Created"
    )

    reactflow_graph = build_reactflow_graph(

        graph,

        positions,

        {}
    )

    print(
        "\nReactFlow Summary"
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