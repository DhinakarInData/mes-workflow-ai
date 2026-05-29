from typing import Optional, List

from pydantic import BaseModel



# ==========================================
# ISA88 STRUCTURE
# ==========================================

class ISA88Hierarchy(BaseModel):

    procedure: Optional[str] = None

    unit_procedure: Optional[str] = None

    operation: Optional[str] = None

    phase: Optional[str] = None




# ==========================================
# OPERATION MODEL
# ==========================================

class Operation(BaseModel):

    operation_name: str

    phases: List[str]




# ==========================================
# NODE MODEL
# ==========================================

class Node(BaseModel):

    # --------------------------------------
    # CORE
    # --------------------------------------

    id: str

    label: str

    workflow_type: str



    # --------------------------------------
    # ISA-88
    # --------------------------------------

    isa88_level: Optional[str] = None

    isa88_hierarchy: Optional[ISA88Hierarchy] = None



    # --------------------------------------
    # ROLE / OWNERSHIP
    # --------------------------------------

    actor_role: Optional[str] = None

    system_owner: Optional[str] = None

    equipment: Optional[str] = None



    # --------------------------------------
    # GAMP5 / GXP
    # --------------------------------------

    gxp_critical: bool = False

    requires_signature: bool = False

    audit_required: bool = True



    # --------------------------------------
    # EXECUTION SEMANTICS
    # --------------------------------------

    retryable: bool = False

    loop_target: Optional[str] = None

    connector: Optional[str] = None

    event_type: Optional[str] = None

    retry_limit: Optional[int] = None

    retry_count: Optional[int] = None

    failure_path: Optional[str] = None

    exception_type: Optional[str] = None



    # --------------------------------------
    # VISUALIZATION
    # --------------------------------------

    visual_type: Optional[str] = None




# ==========================================
# EDGE MODEL
# ==========================================

class Edge(BaseModel):

    source: str

    target: str

    condition: Optional[str] = None

    edge_type: Optional[str] = None




# ==========================================
# WORKFLOW CONTEXT
# ==========================================

class WorkflowContext(BaseModel):

    procedure: Optional[str] = None

    unit_procedure: Optional[str] = None

    operation: Optional[str] = None

    equipment: Optional[str] = None

    area: Optional[str] = None

    site: Optional[str] = None

    enterprise: Optional[str] = None




# ==========================================
# WORKFLOW MODEL
# ==========================================

class Workflow(BaseModel):

    workflow_name: Optional[str] = None

    version: Optional[str] = "1.0"

    status: Optional[str] = "DRAFT"



    # --------------------------------------
    # ISA95 CONTEXT
    # --------------------------------------

    context: WorkflowContext



    # --------------------------------------
    # OPERATIONS
    # --------------------------------------

    operations: Optional[List[Operation]] = []



    # --------------------------------------
    # EXECUTION
    # --------------------------------------

    nodes: List[Node]

    edges: List[Edge]