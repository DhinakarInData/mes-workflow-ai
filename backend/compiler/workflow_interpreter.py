import json


def normalize_activity_text(text):
    

    text = text.strip()

    lower = text.lower()

    if lower.startswith("if yes "):

        return text[7:]

    if lower.startswith("if no "):

        return text[6:]

    return text
def build_nodes(lines):

    nodes = []

    node_counter = 1

    nodes.append({

        "id": "START",

        "type": "START",

        "label": "Start"
    })

    for line in lines:

        text = line.strip()

        if not text:

            continue

        lower = text.lower()

        if (
            "system check" in lower
            or "system checks" in lower
            or "check if" in lower
            or "verify" in lower
        ):

            nodes.append({

                "id": f"A{node_counter}",

                "type": "SYSTEM_CHECK",

                "label": text
        })

            nodes.append({

                "id": f"D{node_counter}",

                "type": "DECISION",

                "label": "System Response"
        })

            node_counter += 1

        elif "end" in lower:

            continue

        elif (
            "scan" in lower
            or "move" in lower
            or "enter" in lower
            or "print" in lower
            or "record" in lower
            or "select" in lower
        ):

            nodes.append({

                "id": f"A{node_counter}",

                "type": "MANUAL_ACTIVITY",

                "label": normalize_activity_text(
                    text
                )
            })

            node_counter += 1

    nodes.append({

        "id": "END",

        "type": "END",

        "label": "End"
    })

    return nodes

def extract_system_checks(lines):

    results = []

    for line in lines:

        text = line.strip()

        if (
            "system check" in text.lower()
            or "system checks" in text.lower()
            or "check if" in text.lower()
            or "verify" in text.lower()
        ):

            results.append(text)

    return results


def extract_manual_activities(lines):

    results = []

    keywords = [

        "scan",

        "move",

        "enter",

        "print",

        "select",

        "inform",

        "perform",

        "record"
    ]

    for line in lines:

        text = line.strip().lower()

        for keyword in keywords:

            if keyword in text:

                results.append(
                    line.strip()
                )

                break

    return results
def extract_decisions(lines):

    decisions = []

    for line in lines:

        text = line.strip().lower()

        if text.startswith("if yes"):

            decisions.append(
                ("YES", line.strip())
            )

        elif text.startswith("if no"):

            decisions.append(
                ("NO", line.strip())
            )

    return decisions

# ADD HERE
def map_decisions_to_nodes(
    

    decisions,
    nodes
):

    mappings = []

    for decision_type, decision_text in decisions:

        target_text = decision_text

        target_text = target_text.replace(
            "If yes",
            ""
        )

        target_text = target_text.replace(
            "If no",
            ""
        )

        target_text = target_text.strip().lower()

        for node in nodes:

            node_label = node[
                "label"
            ].lower()

            if target_text == node_label:

                mappings.append({

                    "condition": decision_type,

                    "target": node["id"]

                })

    return mappings

def map_no_conditions(
    decisions,
    nodes
):

    mappings = []

    for decision_type, decision_text in decisions:

        if decision_type != "NO":

            continue

        text = decision_text.lower()

        if "end" in text:

            mappings.append({

                "condition": "NO",

                "target": "END"
            })

    return mappings
def map_no_activity_conditions(
    decisions,
    nodes
):

    mappings = []

    for decision_type, decision_text in decisions:

        if decision_type != "NO":

            continue

        text = decision_text.lower()

        if "end" in text:

            continue

        target_text = text.replace(
            "if no",
            ""
        ).strip()

        mappings.append({

            "condition": "NO",

            "activity": target_text

        })

    return mappings

def build_dynamic_conditional_edges(
    mappings
):

    edges = []

    decision_nodes = [
        "D1",
        "D3"
    ]

    for i, mapping in enumerate(mappings):

        if i >= len(decision_nodes):

            break

        edges.append({

            "source": decision_nodes[i],

            "target": mapping["target"],

            "condition": mapping["condition"],

            "edge_type": "CONDITIONAL"
        })

    return edges
def extract_loopbacks(lines):

    results = []

    for line in lines:

        text = line.strip().lower()

        if (
            "return to" in text
            or "go back to" in text
            or "retry" in text
        ):

            results.append(
                line.strip()
            )

    return results
def map_loopbacks(
    loopbacks,
    nodes
):

    mappings = []

    for loop_text in loopbacks:

        text = loop_text.lower()

        if "return to" in text:

            target_text = text.replace(
                "return to",
                ""
            ).strip()

            for node in nodes:

                if (
                    node["type"]
                    == "MANUAL_ACTIVITY"
                ):

                    if (
                        node["label"].lower()
                        == target_text
                    ):

                        mappings.append({

                            "source_text":
                            loop_text,

                            "target":
                            node["id"]

                        })

        return mappings
def extract_system_messages(lines):

    results = []

    for line in lines:

        text = line.strip().lower()

        if (
            "show " in text
            or "display " in text
        ):

            results.append(
                line.strip()
            )

    return results
def build_edges(nodes):

    edges = []

    for i in range(len(nodes) - 1):

        if nodes[i]["type"] == "DECISION":

            continue

        edges.append({

            "source": nodes[i]["id"],

            "target": nodes[i + 1]["id"],

            "edge_type": "SEQUENCE"
        })

    return edges
def build_loopback_edges(
    loopback_mappings,
    nodes
):

    edges = []

    source_node = None

    for node in nodes:

        if node["label"].lower() == "return to scan bin":

            source_node = node["id"]

            break

    if source_node is None:

        return edges

    for mapping in loopback_mappings:

        edges.append({

            "source": source_node,

            "target": mapping["target"],

            "edge_type": "LOOPBACK"
        })

    return edges

def build_dynamic_no_edges(
    no_mappings
):

    edges = []

    decision_nodes = [
        "D1"
    ]

    for i, mapping in enumerate(
        no_mappings
    ):

        if i >= len(
            decision_nodes
        ):

            break

        edges.append({

            "source":
            decision_nodes[i],

            "target":
            mapping["target"],

            "condition":
            mapping["condition"],

            "edge_type":
            "CONDITIONAL"
        })

    return edges
def build_no_activity_edges(
    no_activity,
    new_nodes
):

    edges = []

    if len(no_activity) == 0:

        return edges

    if len(new_nodes) == 0:

        return edges

    edges.append({

        "source": "D3",

        "target": new_nodes[0]["id"],

        "condition": "NO",

        "edge_type": "CONDITIONAL"
    })

    return edges

def build_conditional_edges():

    return [

        {
            "source": "D1",
            "target": "A2",
            "condition": "YES",
            "edge_type": "CONDITIONAL"
        },

        {
            "source": "D1",
            "target": "END",
            "condition": "NO",
            "edge_type": "CONDITIONAL"
        },

        {
            "source": "D3",
            "target": "A4",
            "condition": "YES",
            "edge_type": "CONDITIONAL"
        },

        {
            "source": "D3",
            "target": "A5",
            "condition": "NO",
            "edge_type": "CONDITIONAL"
        }
    ]
def generate_ir(lines):

    nodes = build_nodes(lines)

    edges = build_edges(nodes)

    decisions = extract_decisions(
    lines
    )

    mappings = map_decisions_to_nodes(
    decisions,
    nodes
    )
    no_mappings = map_no_conditions(
    decisions,
    nodes
)

    no_activity = map_no_activity_conditions(
    decisions,
    nodes
)

    new_nodes = create_missing_activity_nodes(
    no_activity,
    nodes
)
    loopbacks = extract_loopbacks(
    lines
)

    loopback_mappings = map_loopbacks(
    loopbacks,
    nodes
)

    edges.extend(

    build_loopback_edges(
        loopback_mappings,
        nodes
    )
)

    nodes.extend(
    new_nodes
)
    edges.extend(

    build_no_activity_edges(
        no_activity,
        new_nodes
    )
)
    edges.extend(
    build_dynamic_no_edges(
        no_mappings
    )
)

    edges.extend(

    build_dynamic_conditional_edges(
        mappings
    )
    )
    

    return {

        "workflow_name": "Generated Workflow",

        "nodes": nodes,

        "edges": edges
    }

def create_missing_activity_nodes(
    no_activity_mappings,
    nodes
):

    next_id = 1

    for node in nodes:

        if node["id"].startswith("A"):

            try:

                value = int(
                    node["id"][1:]
                )

                next_id = max(
                    next_id,
                    value + 1
                )

            except:

                pass

    new_nodes = []

    for item in no_activity_mappings:

        new_nodes.append({

            "id": f"A{next_id}",

            "type": "MANUAL_ACTIVITY",

            "label": item["activity"]

        })

        next_id += 1

    return new_nodes

    print(
        "\nNEW ACTIVITY NODES\n"
    )

    for item in no_activity_mappings:

        print(
            item["activity"]
        )
    
def extract_end_conditions(lines):

    results = []

    for line in lines:

        text = line.strip()

        if "end" in text.lower():

            results.append(text)

    return results

if __name__ == "__main__":

    sample_text = """

    Gross Weight Verification

    Scan the area to perform Gross weight verification

    Scan the weighing scale 

    System check if its valid proceed to fetch the dispensed material details else show the error message and return to scan the scale



    User select the material

    User scan the material barcode

    System check if it valid go to read the scale value else show the error message and return to scan the material barcode

    Read the scale value 
    System check weighed qty matches dispensed qty if it ok show complies it if not ok show does not comply 

    then go to end of workflow

    """

    lines = sample_text.splitlines()
    
    nodes = build_nodes(lines)
    
    decisions = extract_decisions(lines)

    mappings = map_decisions_to_nodes(
    decisions,
    nodes
)
    print("\nMAPPINGS\n")

    for item in mappings:

            print(item)
            
    
    no_mappings = map_no_conditions(
    decisions,
    nodes
)

    print(
    "\nNO MAPPINGS\n"
    )

    for item in no_mappings:

        print(item)
            
    dynamic_edges = build_dynamic_conditional_edges(
    mappings
    )

    print(
    "\nDYNAMIC CONDITIONAL EDGES\n"
    )
    
   

    for edge in dynamic_edges:

        print(edge)
    
    
    loopbacks = extract_loopbacks(
        lines
)

    loopback_mappings = (
        map_loopbacks(
            loopbacks,
            nodes
    )
)

    print(
    "\nLOOPBACK MAPPINGS\n"
    )

    for item in loopback_mappings:

        print(item)
        
    loopback_edges = build_loopback_edges(
        loopback_mappings,
        nodes
)

    print(
    "\nLOOPBACK EDGES\n"
)

    for edge in loopback_edges:

        print(edge)
        
    no_activity = map_no_activity_conditions(
        decisions,
        nodes
    )
    new_nodes = create_missing_activity_nodes(
        no_activity,
        nodes
)

    print(
    "\nNEW NODES\n"
)

    for node in new_nodes:

        print(node)
    create_missing_activity_nodes(
        no_activity,
        nodes
)

    print(
    "\nNO ACTIVITY MAPPINGS\n"
)

    for item in no_activity:

        print(item)
    print("\nNODES\n")
    no_activity_edges = (
    build_no_activity_edges(
        no_activity,
        new_nodes
    )
)

    print(
        "\nNO ACTIVITY EDGES\n"
    )

    for edge in no_activity_edges:

        print(edge)

    for node in nodes:

        print(
        node["id"],
        node["type"],
        node["label"]
    )

    print("\nEDGES\n")

    for edge in build_edges(nodes):

        print(edge)

    print("\nCONDITIONAL EDGES\n")

    for edge in build_conditional_edges():

        print(edge)
    
    print("\nGENERATED IR\n")

    ir = generate_ir(lines)

    print(
    json.dumps(
        ir,
        indent=4
    )
)