# ===================================
# ROUTING RULES
# ===================================

ROUTING_RULES = {

    "SEQUENCE": {

        "routing_type": "VERTICAL",

        "lane_offset": 0
    },

    "CONDITIONAL_YES": {

        "routing_type": "DOWN",

        "lane_offset": 0
    },

    "CONDITIONAL_NO": {

        "routing_type": "RIGHT",

        "lane_offset": 1
    },

    "ERROR_FLOW": {

        "routing_type": "RIGHT_EXTERNAL",

        "lane_offset": 2
    },

    "LOOPBACK": {

        "routing_type": "OUTER_LOOP",

        "lane_offset": 3
    },

    "REWORK": {

        "routing_type": "BOTTOM_LOOP",

        "lane_offset": 4
    },

    "REJECTED": {

        "routing_type": "LEFT_RETURN",

        "lane_offset": -2
    }
}


# ===================================
# GET ROUTING CONFIG
# ===================================

def get_routing_config(edge):

    # ===================================
    # LOOPBACKS
    # ===================================

    if edge.edge_type == "LOOPBACK":

        if edge.condition == "REWORK":

            return ROUTING_RULES["REWORK"]

        elif edge.condition == "REJECTED":

            return ROUTING_RULES["REJECTED"]

        return ROUTING_RULES["LOOPBACK"]


    # ===================================
    # ERROR FLOW
    # ===================================

    if edge.edge_type == "ERROR_FLOW":

        return ROUTING_RULES["ERROR_FLOW"]


    # ===================================
    # CONDITIONAL
    # ===================================

    if edge.edge_type == "CONDITIONAL":

        if edge.condition == "YES":

            return ROUTING_RULES["CONDITIONAL_YES"]

        elif edge.condition == "NO":

            return ROUTING_RULES["CONDITIONAL_NO"]


    # ===================================
    # DEFAULT
    # ===================================

    return ROUTING_RULES["SEQUENCE"]