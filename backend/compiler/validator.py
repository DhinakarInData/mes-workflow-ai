def validate_workflow_schema(data):

    node_ids = set()

    for node in data["nodes"]:

        if node["id"] in node_ids:

            raise Exception(
                f'Duplicate node id: {node["id"]}'
            )

        node_ids.add(node["id"])


    for edge in data["edges"]:

        if edge["source"] not in node_ids:

            raise Exception(
                f'Invalid edge source: {edge["source"]}'
            )

        if edge["target"] not in node_ids:

            raise Exception(
                f'Invalid edge target: {edge["target"]}'
            )


    for connector in data["connectors"]:

        if connector["source"] not in node_ids:

            raise Exception(
                f'Invalid connector source: {connector["source"]}'
            )

        if connector["target"] not in node_ids:

            raise Exception(
                f'Invalid connector target: {connector["target"]}'
            )