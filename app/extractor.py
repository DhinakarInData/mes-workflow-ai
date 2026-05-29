from schema import (
    Workflow,
    Node,
    Edge,
    WorkflowContext,
    ISA88Hierarchy
)

from workflow_graph import WorkflowGraph


# ==========================================
# CONTEXT PREFIXES
# ==========================================

CONTEXT_PREFIXES = [
    "ENTERPRISE:",
    "SITE:",
    "AREA:",
    "PROCEDURE:",
    "UNIT_PROCEDURE:",
    "OPERATION:",
    "EQUIPMENT:",
]


# ==========================================
# NODE KEYWORDS
# ==========================================

NODE_KEYWORDS = {

    "scan":      "SYSTEM_SCAN",
    "barcode":   "SYSTEM_SCAN",

    "verify":    "QA_CHECK",
    "validate":  "QA_CHECK",
    "check":     "QA_CHECK",

    "approve":   "SIGNATURE",

    "login":     "MANUAL_ACTIVITY",
    "record":    "MANUAL_ACTIVITY",
    "start":     "MANUAL_ACTIVITY",
    "add":       "MANUAL_ACTIVITY",
    "charge":    "MANUAL_ACTIVITY",
    "transfer":  "MANUAL_ACTIVITY",
    "close":     "MANUAL_ACTIVITY",

    "retry":     "LOOP",
}


# ==========================================
# DETECT WORKFLOW TYPE
# ==========================================

def detect_workflow_type(step: str):

    step_lower = step.lower()

    for keyword, workflow_type in NODE_KEYWORDS.items():

        if keyword in step_lower:

            return workflow_type

    return "MANUAL_ACTIVITY"


# ==========================================
# CREATE NODE
# ==========================================

def create_node(

    node_id,
    workflow_type,
    label,
    context
):

    actor_role = "Operator"

    if workflow_type == "QA_CHECK":

        actor_role = "QA"

    elif workflow_type == "SIGNATURE":

        actor_role = "Supervisor"

    elif workflow_type in [

        "AUTO_STEP",
        "SYSTEM_RESPONSE"

    ]:

        actor_role = "System"

    return Node(

        id=node_id,

        label=label,

        workflow_type=workflow_type,

        isa88_level="PHASE",

        isa88_hierarchy=ISA88Hierarchy(

            procedure=context.procedure,

            unit_procedure=context.unit_procedure,

            operation=context.operation,

            phase=label
        ),

        actor_role=actor_role,

        system_owner="Syncade",

        equipment=context.equipment,

        gxp_critical=False,

        requires_signature=False,

        audit_required=True,

        retryable=False,

        retry_limit=None,

        event_type=None,

        visual_type=workflow_type
    )


# ==========================================
# CREATE EDGE
# ==========================================

def create_edge(

    source,
    target,
    condition=None,
    edge_type="SEQUENCE_FLOW"
):

    return Edge(

        source=source,

        target=target,

        condition=condition,

        edge_type=edge_type
    )


# ==========================================
# IS CONTEXT LINE
# ==========================================

def is_context_line(line):

    return any(

        line.startswith(prefix)

        for prefix in CONTEXT_PREFIXES
    )


# ==========================================
# STRIP NUMBERING
# ==========================================

def strip_numbering(line):

    if "." in line:

        parts = line.split(".", 1)

        if parts[0].strip().isdigit():

            return parts[1].strip()

    return line


# ==========================================
# FIND RETRY TARGET
# ==========================================

def find_retry_target(

    created_nodes
):

    executable_types = [

        "MANUAL_ACTIVITY",

        "SYSTEM_SCAN",

        "QA_CHECK",
    ]

    for node in reversed(created_nodes):

        if node.workflow_type in executable_types:

            if "retry" in node.label.lower():

                continue

            return node.id

    return None


# ==========================================
# FIND NODE BY LABEL
# ==========================================

def find_node_by_label(

    target_label,

    created_nodes
):

    target_label = target_label.lower()

    for node in reversed(created_nodes):

        if target_label in node.label.lower():

            return node.id

    return None


# ==========================================
# EXTRACT WORKFLOW
# ==========================================

def extract_workflow(text: str):

    context = WorkflowContext()

    graph = WorkflowGraph()

    created_nodes = []

    # ======================================
    # EXTRACT CONTEXT
    # ======================================

    for line in text.split("\n"):

        clean = line.strip()

        if clean.startswith("ENTERPRISE:"):

            context.enterprise = clean.replace(

                "ENTERPRISE:",
                ""

            ).strip()

        elif clean.startswith("SITE:"):

            context.site = clean.replace(

                "SITE:",
                ""

            ).strip()

        elif clean.startswith("AREA:"):

            context.area = clean.replace(

                "AREA:",
                ""

            ).strip()

        elif clean.startswith("PROCEDURE:"):

            context.procedure = clean.replace(

                "PROCEDURE:",
                ""

            ).strip()

        elif clean.startswith("UNIT_PROCEDURE:"):

            context.unit_procedure = clean.replace(

                "UNIT_PROCEDURE:",
                ""

            ).strip()

        elif clean.startswith("OPERATION:"):

            context.operation = clean.replace(

                "OPERATION:",
                ""

            ).strip()

        elif clean.startswith("EQUIPMENT:"):

            context.equipment = clean.replace(

                "EQUIPMENT:",
                ""

            ).strip()

    # ======================================
    # NODE COUNTER
    # ======================================

    node_counter = [1]

    def next_node_id():

        nid = f"N{node_counter[0]}"

        node_counter[0] += 1

        return nid

    # ======================================
    # START NODE
    # ======================================

    start_id = next_node_id()

    start_node = create_node(

        start_id,
        "START",
        "Start",
        context
    )

    graph.add_node(start_node)

    created_nodes.append(start_node)

    graph.previous_node_id = start_id

    # ======================================
    # BRANCH STATE
    # ======================================

    graph.current_branch = None

    graph.decision_node_id = None

    graph.yes_last_node = None

    graph.no_last_node = None

    # ======================================
    # PARSE WORKFLOW
    # ======================================

    for raw_line in text.split("\n"):

        clean_line = raw_line.strip()

        if not clean_line:

            continue

        if is_context_line(clean_line):

            continue

        clean_line = strip_numbering(clean_line)

        if not clean_line:

            continue

        # ==================================
        # DECISION
        # ==================================

        if clean_line.upper().startswith("DECISION:"):

            question = clean_line.replace(

                "DECISION:",
                ""

            ).strip()

            node_id = next_node_id()

            node = create_node(

                node_id,
                "DECISION",
                question,
                context
            )

            graph.add_edge(

                create_edge(

                    graph.previous_node_id,

                    node_id
                )
            )

            graph.add_node(node)

            created_nodes.append(node)

            graph.previous_node_id = node_id

            graph.decision_node_id = node_id

            graph.yes_last_node = node_id

            graph.no_last_node = node_id

            continue

        # ==================================
        # YES
        # ==================================

        if clean_line.upper() == "YES:":

            graph.current_branch = "YES"

            continue

        # ==================================
        # NO
        # ==================================

        if clean_line.upper() == "NO:":

            graph.current_branch = "NO"

            continue

        # ==================================
        # CONTINUE
        # ==================================

        if clean_line.upper() == "CONTINUE:":

            graph.current_branch = "CONTINUE"

            continue

        # ==================================
        # EXPLICIT RETRY TARGET
        # ==================================

        explicit_retry_target = None

        if "->" in clean_line:

            parts = clean_line.split("->")

            clean_line = parts[0].strip()

            explicit_retry_target = (

                parts[1]
                .strip()
                .lower()
            )

        # ==================================
        # CREATE NODE
        # ==================================

        workflow_type = detect_workflow_type(

            clean_line
        )

        node_id = next_node_id()

        node = create_node(

            node_id,
            workflow_type,
            clean_line,
            context
        )

        graph.add_node(node)

        created_nodes.append(node)

        # ==================================
        # MAIN FLOW
        # ==================================

        if graph.current_branch is None:

            graph.add_edge(

                create_edge(

                    graph.previous_node_id,

                    node_id
                )
            )

            graph.previous_node_id = node_id

        # ==================================
        # YES FLOW
        # ==================================

        elif graph.current_branch == "YES":

            graph.add_edge(

                create_edge(

                    graph.yes_last_node,

                    node_id,

                    "YES"
                )
            )

            graph.yes_last_node = node_id

        # ==================================
        # NO FLOW
        # ==================================

        elif graph.current_branch == "NO":

            graph.add_edge(

                create_edge(

                    graph.no_last_node,

                    node_id,

                    "NO",

                    "EXCEPTION_FLOW"
                )
            )

            graph.no_last_node = node_id

        # ==================================
        # CONTINUE FLOW
        # ==================================

        elif graph.current_branch == "CONTINUE":

            merge_id = next_node_id()

            merge_node = create_node(

                merge_id,
                "MERGE",
                "MERGE",
                context
            )

            graph.add_node(merge_node)

            created_nodes.append(merge_node)

            if graph.yes_last_node:

                graph.add_edge(

                    create_edge(

                        graph.yes_last_node,

                        merge_id,

                        "MERGE"
                    )
                )

            if graph.no_last_node:

                graph.add_edge(

                    create_edge(

                        graph.no_last_node,

                        merge_id,

                        "MERGE"
                    )
                )

            graph.add_edge(

                create_edge(

                    merge_id,

                    node_id
                )
            )

            graph.previous_node_id = node_id

            graph.current_branch = None

            graph.decision_node_id = None

            graph.yes_last_node = None

            graph.no_last_node = None

        # ==================================
        # RETRY LOOP
        # ==================================

        if "retry" in clean_line.lower():

            retry_target = None

            # ==============================
            # EXPLICIT TARGET
            # ==============================

            if explicit_retry_target:

                retry_target = find_node_by_label(

                    explicit_retry_target,

                    created_nodes
                )

            # ==============================
            # FALLBACK TARGET
            # ==============================

            if not retry_target:

                retry_target = find_retry_target(

                    created_nodes
                )

            # ==============================
            # CREATE RETRY EDGE
            # ==============================

            if retry_target:

                graph.add_edge(

                    create_edge(

                        node_id,

                        retry_target,

                        "RETRY",

                        "RETRY_FLOW"
                    )
                )

    # ======================================
    # END NODE
    # ======================================

    end_id = next_node_id()

    end_node = create_node(

        end_id,
        "END",
        "End",
        context
    )

    graph.add_edge(

        create_edge(

            graph.previous_node_id,

            end_id
        )
    )

    graph.add_node(end_node)

    created_nodes.append(end_node)

    # ======================================
    # RETURN WORKFLOW
    # ======================================

    return Workflow(

        workflow_name=
        context.procedure or
        "Unnamed Workflow",

        version="1.0",

        status="DRAFT",

        context=context,

        operations=[],

        nodes=graph.nodes,

        edges=graph.edges
    )