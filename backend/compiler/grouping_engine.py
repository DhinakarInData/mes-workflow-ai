from collections import defaultdict


# ===================================
# KEYWORD GROUP RULES
# ===================================

GROUP_RULES = {

    "VERIFICATION": [

        "verify",

        "validation",

        "scan",

        "check"
    ],

    "CLEANING": [

        "clean",

        "wash",

        "sanitize"
    ],

    "MANUFACTURING": [

        "manufacture",

        "usage",

        "execute",

        "process"
    ],

    "SUPERVISOR": [

        "supervisor",

        "approval",

        "confirm"
    ],

    "ERROR_HANDLING": [

        "error",

        "reject",

        "invalid",

        "destroy"
    ]
}


# ===================================
# BUILD SEMANTIC GROUPS
# ===================================

def build_semantic_groups(graph):

    semantic_groups = defaultdict(list)


    # ===================================
    # PROCESS NODES
    # ===================================

    for node in graph.nodes.values():

        label = node.label.lower()


        assigned = False


        # ===================================
        # RULE MATCHING
        # ===================================

        for group_name, keywords in GROUP_RULES.items():

            for keyword in keywords:

                if keyword in label:

                    semantic_groups[
                        group_name
                    ].append(node.id)

                    assigned = True

                    break


            if assigned:

                break


        # ===================================
        # DEFAULT GROUP
        # ===================================

        if not assigned:

            semantic_groups[
                "GENERAL"
            ].append(node.id)


    # ===================================
    # LOOPBACK GROUP
    # ===================================

    for edge in graph.edges:

        if edge.edge_type == "LOOPBACK":

            semantic_groups[
                "RETRY_LOOP"
            ].append(edge.source)

            semantic_groups[
                "RETRY_LOOP"
            ].append(edge.target)


    # ===================================
    # REMOVE DUPLICATES
    # ===================================

    cleaned_groups = {}


    for group_name, node_ids in semantic_groups.items():

        cleaned_groups[group_name] = list(

            set(node_ids)
        )


    return cleaned_groups


# ===================================
# PRINT GROUP REPORT
# ===================================

def print_group_report(

    graph,

    semantic_groups
):

    print(
        "\n===== SEMANTIC GROUPS =====\n"
    )


    for group_name, node_ids in semantic_groups.items():

        print(f"\n{group_name}:")


        for node_id in node_ids:

            node = graph.nodes[node_id]

            print(

                f"   {node.id} | "

                f"{node.label}"
            )