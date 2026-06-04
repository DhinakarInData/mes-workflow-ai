# ===================================
# CLASSIFY NODE SEMANTICS
# ===================================

def classify_node_semantics(graph):

    semantics = {}


    for node in graph.nodes.values():

        outgoing = graph.adjacency_map.get(
            node.id,
            []
        )

        incoming = graph.reverse_adjacency_map.get(
            node.id,
            []
        )


        # ===================================
        # START NODE
        # ===================================

        if node.type == "START":

            semantics[node.id] = "ROOT"


        # ===================================
        # END NODE
        # ===================================

        elif node.type == "END":

            semantics[node.id] = "TERMINAL"


        # ===================================
        # ERROR NODE
        # ===================================

        elif node.type == "ERROR":

            semantics[node.id] = "ERROR_TERMINAL"


        # ===================================
        # DECISION NODE
        # ===================================

        elif node.type == "DECISION":

            semantics[node.id] = "DECISION_GATEWAY"


        # ===================================
        # MERGE NODE
        # ===================================

        elif len(incoming) > 1:

            semantics[node.id] = "MERGE_POINT"


        # ===================================
        # BRANCH NODE
        # ===================================

        elif len(outgoing) >= 2:

            semantics[node.id] = "BRANCH_POINT"


        # ===================================
        # LOOP PARTICIPANT
        # ===================================

        elif has_loopback_connection(
            graph,
            node.id
        ):

            semantics[node.id] = "LOOP_NODE"


        # ===================================
        # STANDARD ACTIVITY
        # ===================================

        else:

            semantics[node.id] = "ACTIVITY"


    return semantics


# ===================================
# LOOPBACK DETECTION
# ===================================

def has_loopback_connection(
    graph,
    node_id
):

    incoming = graph.reverse_adjacency_map.get(
        node_id,
        []
    )


    for edge in incoming:

        if edge.edge_type == "LOOPBACK":

            return True


    return False


# ===================================
# FIND SEMANTIC CLUSTERS
# ===================================

def find_semantic_clusters(graph):

    clusters = {}


    for node in graph.nodes.values():

        group = node.group


        if group not in clusters:

            clusters[group] = []


        clusters[group].append(node)


    return clusters


# ===================================
# DETECT EVENT NODES
# ===================================

def find_event_nodes(graph):

    result = []


    for node in graph.nodes.values():

        if node.event_type is not None:

            result.append(node)


    return result


# ===================================
# DETECT SYSTEM NODES
# ===================================

def find_system_nodes(graph):

    result = []


    for node in graph.nodes.values():

        if node.type == "SYSTEM_ACTIVITY":

            result.append(node)


    return result


# ===================================
# DETECT HUMAN TASKS
# ===================================

def find_human_tasks(graph):

    result = []


    for node in graph.nodes.values():

        if node.type == "MANUAL_ACTIVITY":

            result.append(node)


    return result


# ===================================
# PRINT SEMANTIC REPORT
# ===================================



    print_semantic_report(
        graph
    )


    # ===================================
    # NODE SEMANTICS
    # ===================================

    semantics = classify_node_semantics(
        graph
    )


    print(
        "===== NODE SEMANTICS =====\n"
    )


    for node_id, semantic_type in semantics.items():

        node = graph.get_node(node_id)

        print(

            node.id,

            "|",

            node.label,

            "|",

            semantic_type
        )


    # ===================================
    # SEMANTIC CLUSTERS
    # ===================================

    print(
        "\n===== SEMANTIC CLUSTERS =====\n"
    )


    clusters = find_semantic_clusters(
        graph
    )


    for group, nodes in clusters.items():

        print(f"\n{group}:")


        for node in nodes:

            print(

                "  ",

                node.id,

                "|",

                node.label
            )


    # ===================================
    # EVENT NODES
    # ===================================

    print(
        "\n===== EVENT NODES =====\n"
    )


    event_nodes = find_event_nodes(
        graph
    )


    if len(event_nodes) == 0:

        print(
            "No event nodes"
        )


    else:

        for node in event_nodes:

            print(

                node.id,

                "|",

                node.label,

                "|",

                node.event_type
            )


    # ===================================
    # SYSTEM ACTIVITIES
    # ===================================

    print(
        "\n===== SYSTEM ACTIVITIES =====\n"
    )


    system_nodes = find_system_nodes(
        graph
    )


    if len(system_nodes) == 0:

        print(
            "No system activities"
        )


    else:

        for node in system_nodes:

            print(

                node.id,

                "|",

                node.label
            )


    # ===================================
    # HUMAN TASKS
    # ===================================

    print(
        "\n===== HUMAN TASKS =====\n"
    )


    human_tasks = find_human_tasks(
        graph
    )


    if len(human_tasks) == 0:

        print(
            "No human tasks"
        )


    else:

        for node in human_tasks:

            print(

                node.id,

                "|",

                node.label
            )