# ===================================
# BUILD REACTFLOW NODES
# ===================================

def build_reactflow_nodes(

    graph,

    node_positions
):

    reactflow_nodes = []


    for node in graph.nodes.values():

        position = node_positions.get(

            node.id,

            {
                "x": 0,
                "y": 0
            }
        )


        reactflow_node = {

            "id": node.id,

            "type": node.type.lower(),

            "position": {

                "x": position["x"],

                "y": position["y"]
            },

            "data": {

                "label": node.label,

                "step_number": node.step_number,

                "lane": node.lane,

                "group": node.group,

                "actor": node.actor,

                "event_type": node.event_type
            }
        }


        reactflow_nodes.append(
            reactflow_node
        )


    return reactflow_nodes


# ===================================
# BUILD REACTFLOW EDGES
# ===================================

def build_reactflow_edges(graph):

    reactflow_edges = []


    for index, edge in enumerate(graph.edges):

        edge_color = "#555555"


        # ===================================
        # EDGE COLORS
        # ===================================

        if edge.edge_type == "CONDITIONAL":

            edge_color = "green"


        elif edge.edge_type == "ERROR_FLOW":

            edge_color = "red"


        elif edge.edge_type == "LOOPBACK":

            edge_color = "blue"


        elif edge.edge_type == "CONTINUATION":

            edge_color = "orange"


        # ===================================
        # DEFAULT HANDLES
        # ===================================

        source_handle = "bottom"

        target_handle = "top"


        # ===================================
        # CONDITIONAL FLOW
        # ===================================

        if edge.edge_type == "CONDITIONAL":

            source_handle = "right"

            target_handle = "left"


        # ===================================
        # ERROR FLOW
        # ===================================

        elif edge.edge_type == "ERROR_FLOW":

            source_handle = "left"

            target_handle = "right"


        # ===================================
        # LOOPBACK FLOW
        # ===================================

        elif edge.edge_type == "LOOPBACK":

            source_handle = "right"

            target_handle = "left"


        # ===================================
        # CONTINUATION FLOW
        # ===================================

        elif edge.edge_type == "CONTINUATION":

            source_handle = "bottom"

            target_handle = "top"


        # ===================================
        # BUILD EDGE
        # ===================================

        reactflow_edge = {

            "id": f"EDGE_{index}",

            "source": edge.source,

            "target": edge.target,

            "sourceHandle": source_handle,

            "targetHandle": target_handle,

            "label": edge.condition,

            "type": "smoothstep",

            "animated": (

                edge.edge_type == "LOOPBACK"
            ),

            "style": {

                "stroke": edge_color,

                "strokeWidth": 2
            },

            "labelStyle": {

                "fill": edge_color,

                "fontWeight": "bold"
            }
        }


        reactflow_edges.append(
            reactflow_edge
        )


    return reactflow_edges


# ===================================
# BUILD REACTFLOW GRAPH
# ===================================

def build_reactflow_graph(

    graph,

    node_positions
):

    return {

        "nodes": build_reactflow_nodes(

            graph,

            node_positions
        ),

        "edges": build_reactflow_edges(
            graph
        )
    }


# ===================================
# PRINT REACTFLOW REPORT
# ===================================

def print_reactflow_report(

    reactflow_graph
):

    print(
        "\n===== REACTFLOW GRAPH =====\n"
    )


    print(

        "Total Nodes:",

        len(
            reactflow_graph["nodes"]
        )
    )


    print(

        "Total Edges:",

        len(
            reactflow_graph["edges"]
        )
    )