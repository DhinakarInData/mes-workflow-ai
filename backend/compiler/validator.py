allowed_node_types = [

    "START",

    "END",

    "MANUAL_ACTIVITY",

    "SYSTEM_ACTIVITY",

    "DECISION",

    "ERROR",

    "CONNECTOR"
]


allowed_edge_types = [

    "SEQUENCE",

    "CONDITIONAL",

    "LOOPBACK",

    "ERROR_FLOW",

    "CONTINUATION"
]



def validate_workflow_schema(data):

    # ===================================
    # ROOT VALIDATION
    # ===================================

    required_root_keys = [

        "workflow_name",

        "nodes",

        "edges"
    ]


    for key in required_root_keys:

        if key not in data:

            raise ValueError(

                f"Missing root key: {key}"
            )


    # ===================================
    # NODE VALIDATION
    # ===================================

    node_ids = set()


    for node in data["nodes"]:

        required_node_keys = [

            "id",

            "type",

            "label",

            "step_number",

            "lane",

            "group"
        ]


        for key in required_node_keys:

            if key not in node:

                raise ValueError(

                    f"Missing node key: {key}"
                )


        if node["type"] not in allowed_node_types:

            raise ValueError(

                f"Invalid node type: {node['type']}"
            )


        node_ids.add(
            node["id"]
        )


    # ===================================
    # EDGE VALIDATION
    # ===================================

    for edge in data["edges"]:

        required_edge_keys = [

            "source",

            "target",

            "edge_type"
        ]


        for key in required_edge_keys:

            if key not in edge:

                raise ValueError(

                    f"Missing edge key: {key}"
                )


        if edge["edge_type"] not in allowed_edge_types:

            raise ValueError(

                f"Invalid edge type: {edge['edge_type']}"
            )


        # VALID NODE REFERENCES

        if edge["source"] not in node_ids:

            raise ValueError(

                f"Invalid source node: {edge['source']}"
            )


        if edge["target"] not in node_ids:

            raise ValueError(

                f"Invalid target node: {edge['target']}"
            )


        # CONDITIONAL VALIDATION

        if edge["edge_type"] == "CONDITIONAL":

            if "condition" not in edge:

                raise ValueError(

                    "CONDITIONAL edge requires condition"
                )


        # LOOPBACK VALIDATION

        if edge["edge_type"] == "LOOPBACK":

            if "condition" not in edge:

                raise ValueError(

                    "LOOPBACK edge requires condition"
                )


    print(
        "Workflow schema validation successful"
    )