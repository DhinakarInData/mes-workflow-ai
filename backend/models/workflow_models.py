from dataclasses import dataclass, field
from typing import Optional, Dict, List


# ===================================
# WORKFLOW NODE
# ===================================

@dataclass
class WorkflowNode:

    id: str

    type: str

    label: str

    step_number: str

    lane: str

    group: str

    actor: Optional[str] = None

    event_type: Optional[str] = None

    metadata: Dict = field(default_factory=dict)


# ===================================
# WORKFLOW EDGE
# ===================================

@dataclass
class WorkflowEdge:

    source: str

    target: str

    edge_type: str

    condition: Optional[str] = None

    metadata: Dict = field(default_factory=dict)


# ===================================
# WORKFLOW GRAPH
# ===================================

@dataclass
class WorkflowGraph:

    nodes: Dict[str, WorkflowNode]

    edges: List[WorkflowEdge]

    adjacency_map: Dict[str, List[WorkflowEdge]] = field(
        default_factory=dict
    )

    reverse_adjacency_map: Dict[str, List[WorkflowEdge]] = field(
        default_factory=dict
    )


    # ===================================
    # BUILD GRAPH MAPS
    # ===================================

    def build_maps(self):

        self.adjacency_map = {}

        self.reverse_adjacency_map = {}


        for edge in self.edges:

            # OUTGOING

            if edge.source not in self.adjacency_map:

                self.adjacency_map[
                    edge.source
                ] = []


            self.adjacency_map[
                edge.source
            ].append(edge)


            # INCOMING

            if edge.target not in self.reverse_adjacency_map:

                self.reverse_adjacency_map[
                    edge.target
                ] = []


            self.reverse_adjacency_map[
                edge.target
            ].append(edge)


    # ===================================
    # GET NODE
    # ===================================

    def get_node(
        self,
        node_id
    ):

        return self.nodes.get(node_id)


    # ===================================
    # GET START NODE
    # ===================================

    def get_start_node(self):

        for node in self.nodes.values():

            if node.type == "START":

                return node


        return None


    # ===================================
    # GET END NODES
    # ===================================

    def get_end_nodes(self):

        result = []


        for node in self.nodes.values():

            if node.type == "END":

                result.append(node)


        return result