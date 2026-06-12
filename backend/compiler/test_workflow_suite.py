import json

from compiler.workflow_interpreter import (
    generate_ir
)

from compiler.ir_loader import (
    load_ir
)

from compiler.layout_engine import (
    build_layout
)
from compiler.ir_to_graph import (
    build_graph_from_ir
)

import os


WORKFLOW_FOLDER = "test_workflows"


for file_name in os.listdir(
    WORKFLOW_FOLDER
):

    if not file_name.endswith(".txt"):

        continue

    print("\n" + "=" * 50)

    print(
        "WORKFLOW:",
        file_name
    )

    print("=" * 50)

    file_path = os.path.join(
        WORKFLOW_FOLDER,
        file_name
    )

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        workflow_text = file.read()

    lines = workflow_text.splitlines()

    ir = generate_ir(
        lines
    )
    
    print(
        "\nIR Generated"
    )
    
    print(
    "\nGENERATED IR\n"
    )
    if file_name == "startup_checks.txt":
        print(
        json.dumps(
        ir,
        indent=4
    )
)

    graph = build_graph_from_ir(
        ir
    )

    print(
        "Graph Created"
    )

    layout = build_layout(
        graph
    )

    print(
        "Layout Created"
    )

    print(
        "\nNodes:",
        len(ir["nodes"])
    )

    print(
        "Edges:",
        len(ir["edges"])
    )