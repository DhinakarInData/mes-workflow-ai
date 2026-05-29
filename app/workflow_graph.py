class WorkflowGraph:

    def __init__(self):

        self.nodes = []

        self.edges = []



        # ==================================
        # REGISTRIES
        # ==================================

        self.step_registry = {}



        # ==================================
        # EXECUTION TRACKING
        # ==================================

        self.previous_node_id = None

        self.current_branch = None



        # ==================================
        # DECISION TRACKING
        # ==================================

        self.decision_node_id = None



        # ==================================
        # BRANCH TRACKING
        # ==================================

        self.yes_last_node = None

        self.no_last_node = None



    # ======================================
    # ADD NODE
    # ======================================

    def add_node(self, node):

        self.nodes.append(node)



        self.step_registry[
            node.label.lower()
        ] = node.id



        self.previous_node_id = node.id



    # ======================================
    # ADD EDGE
    # ======================================

    def add_edge(self, edge):

        self.edges.append(edge)



    # ======================================
    # FIND STEP BY LABEL
    # ======================================

    def find_step(self, keyword):

        for label, node_id in reversed(

            list(self.step_registry.items())
        ):

            if keyword.lower() in label:

                return node_id



        return None



    # ======================================
    # FIND NODE BY TYPE
    # ======================================

    def find_node_by_type(self, workflow_type):

        for node in reversed(self.nodes):

            if node.workflow_type == workflow_type:

                return node.id



        return None
    # ======================================
# FIND FIRST NODE BY TYPE
# ======================================

    def find_first_node_by_type(self, workflow_type):

        for node in self.nodes:

            if node.workflow_type == workflow_type:

                return node.id

        return None