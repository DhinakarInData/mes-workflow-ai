# ===================================
# EXTRACT NODES
# ===================================

def extract_nodes(raw_text):

    return []


# ===================================
# EXTRACT EDGES
# ===================================

def extract_edges(raw_text):

    return []


# ===================================
# GENERATE WORKFLOW JSON
# ===================================

def generate_workflow_json(raw_text):

    return {

        "nodes": extract_nodes(raw_text),

        "edges": extract_edges(raw_text)
    }
    
    
if __name__ == "__main__":

    with open("test_fds.txt", "r") as f:

        raw_text = f.read()

    nodes = extract_nodes(raw_text)

    for node in nodes:

        print(node)