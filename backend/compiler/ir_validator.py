REQUIRED_NODE_FIELDS = [

    "id",

    "type",

    "label"
]


REQUIRED_EDGE_FIELDS = [

    "source",

    "target",

    "edge_type"
]


def validate_nodes(nodes):

    errors = []

    for node in nodes:

        for field in REQUIRED_NODE_FIELDS:

            if field not in node:

                errors.append(

                    f"Missing node field: {field}"
                )

    return errors


def validate_edges(edges):

    errors = []

    for edge in edges:

        for field in REQUIRED_EDGE_FIELDS:

            if field not in edge:

                errors.append(

                    f"Missing edge field: {field}"
                )

    return errors


def validate_ir(ir):

    errors = []

    errors.extend(

        validate_nodes(
            ir["nodes"]
        )
    )

    errors.extend(

        validate_edges(
            ir["edges"]
        )
    )

    return errors