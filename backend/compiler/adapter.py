def calculate_subtree_width(
    node_id,
    outgoing_map
):

    children = outgoing_map.get(node_id, [])

    if len(children) == 0:

        return 1

    total_width = 0

    for child in children:

        child_id = child["target"]

        total_width += calculate_subtree_width(
            child_id,
            outgoing_map
        )

    return total_width


def layout_node(
    node_id,
    x,
    y,
    node_positions,
    outgoing_map,
    visited,
    node_lookup
):

    # PREVENT INFINITE LOOPS

    if node_id in visited:

        return

    visited.add(node_id)

    current_node = node_lookup[node_id]

    # END NODE

    if current_node.type == "END":

        return

    # POSITION CURRENT NODE

    node_positions[node_id] = {

        "x": x,
        "y": y
    }

    children = outgoing_map.get(node_id, [])

    # LEAF NODE

    if len(children) == 0:

        return

    # SINGLE CHILD

    if len(children) == 1:

        child_id = children[0]["target"]

        layout_node(
            child_id,
            x,
            y + 220,
            node_positions,
            outgoing_map,
            visited,
            node_lookup
        )

    # DECISION NODE

    elif len(children) == 2:

        yes_child = None
        no_child = None

        for child in children:

            if child["edge_type"] == "YES":

                yes_child = child["target"]

            elif child["edge_type"] == "NO":

                no_child = child["target"]

        # NO → LEFT

        if no_child:

            layout_node(
                no_child,
                x - 250,
                y + 220,
                node_positions,
                outgoing_map,
                visited,
                node_lookup
            )

        # YES → RIGHT

        if yes_child:

            layout_node(
                yes_child,
                x + 250,
                y + 220,
                node_positions,
                outgoing_map,
                visited,
                node_lookup
            )


def graph_to_reactflow(graph):

    reactflow_nodes = []
    reactflow_edges = []

    # ===================================
    # NODE LOOKUP
    # ===================================

    node_lookup = {}

    for node in graph["nodes"]:

        node_lookup[node.id] = node

    # ===================================
    # OUTGOING MAP
    # ===================================

    outgoing_map = {}

    for edge in graph["edges"]:

        # IGNORE RETRY FOR LAYOUT

        if edge.edge_type == "RETRY":

            continue

        if edge.source not in outgoing_map:

            outgoing_map[edge.source] = []

        outgoing_map[edge.source].append({

            "target": edge.target,

            "edge_type": edge.edge_type
        })

    # ===================================
    # POSITION ENGINE
    # ===================================

    node_positions = {}

    visited = set()

    # FIND START NODE

    start_node = None

    for node in graph["nodes"]:

        if node.type == "START":

            start_node = node.id

            break

    # RUN LAYOUT

    layout_node(
        start_node,
        500,
        50,
        node_positions,
        outgoing_map,
        visited,
        node_lookup
    )

    # ===================================
    # CENTER END NODE
    # ===================================

    end_node_id = None

    for node in graph["nodes"]:

        if node.type == "END":

            end_node_id = node.id

            break

    if end_node_id:

        branch_x = []
        branch_y = []

        for node_id, position in node_positions.items():

            current_node = node_lookup[node_id]

            if current_node.type in [

                "START",
                "DECISION"
            ]:

                continue

            branch_x.append(position["x"])
            branch_y.append(position["y"])

        if len(branch_x) > 0:

            node_positions[end_node_id] = {

                "x": sum(branch_x) / len(branch_x),

                "y": max(branch_y) + 220
            }

    # ===================================
    # CONVERT NODES
    # ===================================

    for node in graph["nodes"]:

        if node.id not in node_positions:

            node_positions[node.id] = {

                "x": 100,
                "y": 100
            }

        reactflow_node = {

            "id": node.id,

            "type": node.type.lower(),

            "position": node_positions[node.id],

            "data": {

                "label": node.label,

                "step_number": node.step_number,

                "lane": node.lane,

                "group": node.group
            }
        }

        reactflow_nodes.append(
            reactflow_node
        )

    # ===================================
    # CONVERT EDGES
    # ===================================

    for index, edge in enumerate(graph["edges"]):

        edge_color = "#555555"

        # EDGE COLORS

        if edge.edge_type == "YES":

            edge_color = "green"

        elif edge.edge_type == "NO":

            edge_color = "red"

        elif edge.edge_type == "RETRY":

            edge_color = "blue"

        # EDGE TYPE

        edge_type = "step"
        

        if edge.edge_type == "RETRY":

            edge_type = "smoothstep"

        # CREATE EDGE

        reactflow_edge = {

            "id": f"EDGE_{index}",

            "source": edge.source,

            "target": edge.target,

            "label": edge.edge_type,

            "type": edge_type,

            "style": {

                "stroke": edge_color,

                "strokeWidth": 2
            },

            "labelStyle": {

                "fill": edge_color,

                "fontWeight": "bold"
            }
        }

        # ===================================
        # DEFAULT FLOW
        # ===================================

        reactflow_edge["sourceHandle"] = "bottom"
        reactflow_edge["targetHandle"] = "top"

        # YES

        if edge.edge_type == "YES":

            reactflow_edge["sourceHandle"] = "yes"

        # NO

        elif edge.edge_type == "NO":

            reactflow_edge["sourceHandle"] = "no"

        # RETRY

        elif edge.edge_type == "RETRY":

            reactflow_edge["sourceHandle"] = "retry"

            reactflow_edge["animated"] = True

        reactflow_edges.append(
            reactflow_edge
        )

    # ===================================
    # FINAL OUTPUT
    # ===================================

    return {

        "nodes": reactflow_nodes,

        "edges": reactflow_edges
    }