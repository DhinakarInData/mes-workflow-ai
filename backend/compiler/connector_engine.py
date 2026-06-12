from copy import deepcopy


# ===================================
# INJECT LOOPBACK CONNECTORS
# ===================================

def inject_loopback_connectors(graph):

    # ===================================
    # COPY GRAPH
    # ===================================

    transformed_graph = deepcopy(graph)


    # ===================================
    # NEW COLLECTIONS
    # ===================================

    new_nodes = {}

    new_edges = []


    connector_counter = 1


    # ===================================
    # PROCESS EDGES
    # ===================================
    for edge in transformed_graph.edges:


        # ===================================
        # LOOPBACK DETECTED
        # ===================================

        if edge.edge_type == "LOOPBACK":


            connector_label = (
                f"C{connector_counter}"
            )


            connector_out_id = (
                f"CONN_OUT_{connector_counter}"
            )


            connector_in_id = (
                f"CONN_IN_{connector_counter}"
            )


            connector_counter += 1


            # ===================================
            # SOURCE NODE
            # ===================================

            source_node = (
                transformed_graph.nodes[
                    edge.source
                ]
            )


            # ===================================
            # TARGET NODE
            # ===================================

            target_node = (
                transformed_graph.nodes[
                    edge.target
                ]
            )


            # ===================================
            # CONNECTOR OUT NODE
            # ===================================

            connector_out_node = deepcopy(
                source_node
            )


            connector_out_node.id = (
                connector_out_id
            )

            connector_out_node.label = (
                f"({connector_label})"
            )

            connector_out_node.type = (
                "CONNECTOR"
            )

            connector_out_node.group = (
                "CONNECTOR"
            )


            # ===================================
            # CONNECTOR IN NODE
            # ===================================

            connector_in_node = deepcopy(
                target_node
            )


            connector_in_node.id = (
                connector_in_id
            )

            connector_in_node.label = (
                f"({connector_label})"
            )

            connector_in_node.type = (
                "CONNECTOR"
            )

            connector_in_node.group = (
                "CONNECTOR"
            )


            # ===================================
            # STORE CONNECTOR NODES
            # ===================================

            new_nodes[
                connector_out_id
            ] = connector_out_node


            new_nodes[
                connector_in_id
            ] = connector_in_node


            # ===================================
            # EDGE:
            # SOURCE -> CONNECTOR OUT
            # ===================================

            edge_to_connector = deepcopy(
                edge
            )


            edge_to_connector.target = (
                connector_out_id
            )

            edge_to_connector.edge_type = (
                "CONTINUATION"
            )


            # ===================================
            # EDGE:
            # CONNECTOR OUT -> CONNECTOR IN
            # ===================================

            connector_bridge = deepcopy(
                edge
            )


            connector_bridge.source = (
                connector_out_id
            )

            connector_bridge.target = (
                connector_in_id
            )

            connector_bridge.edge_type = (
                "CONNECTOR_FLOW"
            )


            # ===================================
            # EDGE:
            # CONNECTOR IN -> TARGET
            # ===================================

            connector_to_target = deepcopy(
                edge
            )


            connector_to_target.source = (
                connector_in_id
            )

            connector_to_target.edge_type = (
                "CONTINUATION"
            )


            # ===================================
            # STORE NEW EDGES
            # ===================================

            new_edges.append(
                edge_to_connector
            )

            new_edges.append(
                connector_bridge
            )

            new_edges.append(
                connector_to_target
            )


        # ===================================
        # NORMAL EDGE
        # ===================================

        else:

            new_edges.append(edge)


    # ===================================
    # ADD CONNECTOR NODES
    # ===================================

    transformed_graph.nodes.update(
        new_nodes
    )


    # ===================================
    # REPLACE EDGES
    # ===================================

    transformed_graph.edges = new_edges


    # ===================================
    # RETURN
    # ===================================

    return transformed_graph