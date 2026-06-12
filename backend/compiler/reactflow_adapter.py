from compiler.routing_engine import (
    get_routing_config
)
# ===================================
# ESTIMATE NODE SIZE
# ===================================

def estimate_node_size(label):

    if not label:

        return 220, 100


    char_count = len(label)


    # ===================================
    # WIDTH
    # ===================================

    width = min(

        max(
            220,
            char_count * 7
        ),

        420
    )


    # ===================================
    # LINES
    # ===================================

    line_count = (

        char_count // 24
    ) + 1


    # ===================================
    # HEIGHT
    # ===================================

    height = max(

        100,

        line_count * 32
    )


    return width, height

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

        node_width, node_height = estimate_node_size(
    node.label
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
                "response_actor": node.response_actor,

                "event_type": node.event_type,
                "width": node_width,

                "height": node_height,
            }
        }


        reactflow_nodes.append(
            reactflow_node
        )


    return reactflow_nodes


# ===================================
# GET EDGE STYLE
# ===================================

def get_edge_style(routing_type):

    edge_color = "#6B7280"

    animated = False


    # ===================================
    # STRAIGHT FLOW
    # ===================================

    if routing_type == "STRAIGHT":

        edge_color = "#16A34A"


    # ===================================
    # RIGHT BRANCH
    # ===================================

    elif routing_type == "RIGHT_BRANCH":

        edge_color = "#16A34A"


    # ===================================
    # ERROR BRANCH
    # ===================================

    elif routing_type == "ERROR_BRANCH":

        edge_color = "#DC2626"


    # ===================================
    # OUTER LOOP
    # ===================================

    elif routing_type == "OUTER_RIGHT_LOOP":

        edge_color = "#2563EB"

        animated = True


    # ===================================
    # BOTTOM LOOP
    # ===================================

    elif routing_type == "BOTTOM_RETURN_LOOP":

        edge_color = "#7C3AED"

        animated = True


    # ===================================
    # CONNECTOR FLOW
    # ===================================

    elif routing_type == "CONNECTOR_FLOW":

        edge_color = "#EA580C"

        animated = True


    return {

        "edge_color": edge_color,

        "animated": animated
    }
    

# ===================================
# BUILD REACTFLOW EDGES
# ===================================

def build_reactflow_edges(graph):

    reactflow_edges = []

    
    for index, edge in enumerate(graph.edges):
            
        # ===================================
        # ROUTING METADATA
        # =
            print(
                "EDGE DEBUG:",
                    edge.source,
                "->",
            edge.target,
            "ROLE=",
            edge.routing_role
           
        )
           
            routing = get_routing_config(edge)

            routing_type = routing["routing_type"]

            lane_offset = routing["lane_offset"]


        # ERROR BRANCH SEPARATION

            if edge.routing_role == "ERROR":

                if edge.target.endswith("1"):

                    lane_offset = 1

                elif edge.target.endswith("2"):

                    lane_offset = 2

                elif edge.target.endswith("3"):

                    lane_offset = 3


        # ===================================
        # STYLE
        # ===================================

            style_config = get_edge_style(
            routing_type
        )


            edge_color = style_config["edge_color"]

            animated = style_config["animated"]

            print(
                edge.source,
                "->",
                edge.target,
                routing_type,
                lane_offset
                )

        # ===================================
        # BUILD EDGE
        # ===================================

            reactflow_edge = {

            "id": f"EDGE_{index}",

            "source": edge.source,

            "target": edge.target,

            "label": edge.edge_label or edge.condition,

            "type": "semantic",

            "animated": animated,
             #"sourceHandle": source_handle,
             
             "targetHandle": "target",


            # ===================================
            # VISUAL STYLE
            # ===================================

            "style": {

                "stroke": edge_color,

                "strokeWidth": 2
            },


            "labelStyle": {

                "fill": edge_color,

                "fontWeight": "bold"
            },


            # ===================================
            # ROUTING METADATA
            # ===================================

            "data": {

                "routing_type": routing_type,

                "lane_offset": lane_offset
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

    node_positions,

    semantic_groups
):

    return {

        "nodes": build_reactflow_nodes(

            graph,

            node_positions
        ),

        "edges": build_reactflow_edges(
            graph
        ),

        "semantic_groups": semantic_groups
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