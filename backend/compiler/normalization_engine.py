# ===================================
# NORMALIZE NODE TYPES
# ===================================

NODE_NORMALIZATION_MAP = {

    "START": "ROOT_NODE",

    "END": "TERMINAL_NODE",

    "MANUAL_ACTIVITY": "HUMAN_TASK",

    "SYSTEM_ACTIVITY": "AUTOMATED_TASK",

    "DECISION": "CONDITIONAL_GATEWAY",

    "ERROR": "TERMINAL_EXCEPTION",

    "CONNECTOR": "CONTINUATION_NODE"
}


# ===================================
# NORMALIZE EDGE TYPES
# ===================================

EDGE_NORMALIZATION_MAP = {

    "SEQUENCE": "FORWARD_FLOW",

    "CONDITIONAL": "CONDITIONAL_FLOW",

    "LOOPBACK": "CYCLIC_FLOW",

    "ERROR_FLOW": "EXCEPTION_FLOW",

    "CONTINUATION": "CONTINUATION_FLOW"
}


# ===================================
# NORMALIZE NODES
# ===================================

def normalize_nodes(graph):

    normalized_nodes = []


    for node in graph.nodes.values():

        normalized_type = NODE_NORMALIZATION_MAP.get(
            node.type,
            "UNKNOWN_NODE"
        )


        normalized_node = {

            "id": node.id,

            "normalized_type": normalized_type,

            "original_type": node.type,

            "label": node.label,

            "lane": node.lane,

            "group": node.group,

            "actor": node.actor,

            "event_type": node.event_type
        }


        normalized_nodes.append(
            normalized_node
        )


    return normalized_nodes


# ===================================
# NORMALIZE EDGES
# ===================================

def normalize_edges(graph):

    normalized_edges = []


    for edge in graph.edges:

        normalized_type = EDGE_NORMALIZATION_MAP.get(
            edge.edge_type,
            "UNKNOWN_FLOW"
        )


        normalized_edge = {

            "source": edge.source,

            "target": edge.target,

            "normalized_type": normalized_type,

            "original_type": edge.edge_type,

            "condition": edge.condition
        }


        normalized_edges.append(
            normalized_edge
        )


    return normalized_edges


# ===================================
# BUILD INTERMEDIATE REPRESENTATION
# ===================================

def build_intermediate_representation(graph):

    ir = {

        "normalized_nodes": normalize_nodes(
            graph
        ),

        "normalized_edges": normalize_edges(
            graph
        )
    }


    return ir


# ===================================
# PRINT IR REPORT
# ===================================

def print_ir_report(graph):

    ir = build_intermediate_representation(
        graph
    )


    print(
        "\n===== INTERMEDIATE REPRESENTATION =====\n"
    )


    # ===================================
    # NORMALIZED NODES
    # ===================================

    print(
        "===== NORMALIZED NODES =====\n"
    )


    for node in ir["normalized_nodes"]:

        print(

            node["id"],

            "|",

            node["original_type"],

            "->",

            node["normalized_type"]
        )


    # ===================================
    # NORMALIZED EDGES
    # ===================================

    print(
        "\n===== NORMALIZED EDGES =====\n"
    )


    for edge in ir["normalized_edges"]:

        print(

            edge["source"],

            "->",

            edge["target"],

            "|",

            edge["original_type"],

            "->",

            edge["normalized_type"]
        )