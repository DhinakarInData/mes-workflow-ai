class GraphNode:

    def __init__(
        self,
        id,
        step_number,
        type,
        label,
        lane,
        group
    ):

        self.id = id
        self.step_number = step_number
        self.type = type
        self.label = label
        self.lane = lane
        self.group = group


class GraphEdge:

    def __init__(
        self,
        source,
        target,
        edge_type
    ):

        self.source = source
        self.target = target
        self.edge_type = edge_type


class Connector:

    def __init__(
        self,
        id,
        source,
        target,
        connector_type
    ):

        self.id = id
        self.source = source
        self.target = target
        self.connector_type = connector_type