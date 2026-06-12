from compiler.ir_loader import load_ir
from compiler.ir_to_graph import build_graph_from_ir

from engines.topology_layout_engine import (
    build_topology_layout
)

from compiler.reactflow_adapter import (
    build_reactflow_graph
)

import json


ir = load_ir(
    "test_data/equipment_lineclearence.json"
)

graph = build_graph_from_ir(ir)

node_positions = build_topology_layout(
    graph
)

print("\nLayout:\n")

for node_id, pos in node_positions.items():

    print(
        node_id,
        pos
    )


reactflow_graph = build_reactflow_graph(
    graph,
    node_positions,
    []
)

with open(
    "test_graph.json",
    "w"
) as f:

    json.dump(
        reactflow_graph,
        f,
        indent=4
    )

print(
    "\nReactFlow JSON generated successfully."
)