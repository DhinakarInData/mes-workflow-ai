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

    "SIDE_BRANCH": {

        "routing_type": "BUSINESS_BRANCH",

        "lane_offset": 1
    },

    "LOCAL_CONTINUATION": {

        "routing_type": "DOWN",

        "lane_offset": 0
    },

    "ERROR_FLOW": {

        "routing_type": "RIGHT_EXTERNAL",

        "lane_offset": 2
    },

    "LOOPBACK": {

        "routing_type": "OUTER_LOOP",

        "lane_offset": 3
    },

    "RESTART_FLOW": {

        "routing_type": "RESTART_FLOW",

        "lane_offset": 0
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


RESTART_CONDITIONS = [

    "YES",

    "CONTINUE_WITH_NEXT_EQUIPMENT",

    "CONTINUE WITH NEXT EQUIPMENT",

    "CONFIRM_NEXT_EQUIPMENT",

    "CONFIRM NEXT EQUIPMENT",

    "NEXT_EQUIPMENT",

    "NEXT EQUIPMENT",

    "REQUIRED",

    "REQURIED",

    "APPROVE_REWEIGHING",

    "APPROVES_REWEIGHING",

    "APPROVE REWEIGHING",

    "APPROVES REWEIGHING",

    "REWEIGH",

    "REWEIGHING",

    "SCAN_ANOTHER",

    "SCAN ANOTHER",

    "SCAN_ANOTHER_PRODUCT_CONTAINER",

    "SCAN ANOTHER PRODUCT CONTAINER",

    "SCAN_ANOTHER_EMPTY_CONTAINER",

    "SCAN ANOTHER EMPTY CONTAINER",

    "RETURN_TO_SCAN_PRODUCT_CONTAINER",

    "RETURN TO SCAN PRODUCT CONTAINER",

    "GO_FOR_REWEIGHING",

    "GO FOR REWEIGHING",

    "PROCESS_CORRECTED",

    "PROCESS CORRECTED",

    "CORRECT_PROCESS",

    "CORRECT PROCESS"
]


def is_restart_loop(edge):

    values = [
        edge.edge_label,
        edge.condition
    ]

    for value in values:

        condition = (
            value
            or ""
        ).strip().upper().replace(
            "_",
            " "
        )

        normalized_conditions = [
            item.replace(
                "_",
                " "
            )
            for item in RESTART_CONDITIONS
        ]

        if condition in normalized_conditions:

            return True

        if any(
            phrase in condition
            for phrase in [
                "SCAN ANOTHER",
                "RETURN TO",
                "BACK TO",
                "RE-SCAN",
                "RESCAN",
                "REWEIGH",
                "RE-WEIGH",
                "CORRECTED"
            ]
        ):

            return True

    return False


# ===================================
# GET ROUTING CONFIG
# ===================================

def get_routing_config(edge):

    # ===================================
    # LOOPBACKS
    # ===================================

    if edge.edge_type == "LOOPBACK":

        if is_restart_loop(edge):

            return ROUTING_RULES["RESTART_FLOW"]

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

    # ===================================
# CONDITIONAL
# ===================================

    if edge.edge_type == "CONDITIONAL":

        if edge.routing_role == "ERROR":

            return ROUTING_RULES["ERROR_FLOW"]

        elif edge.routing_role == "SUCCESS":

            return ROUTING_RULES["CONDITIONAL_YES"]

        elif edge.routing_role == "SIDE_BRANCH":

            return ROUTING_RULES["SIDE_BRANCH"]

        elif edge.routing_role == "LOCAL_CONTINUATION":

            return ROUTING_RULES["LOCAL_CONTINUATION"]

        elif edge.routing_role == "LOOPBACK":

            if is_restart_loop(edge):

                return ROUTING_RULES["RESTART_FLOW"]

            return ROUTING_RULES["LOOPBACK"]
        

    # ===================================
    # DEFAULT
    # ===================================

    return ROUTING_RULES["SEQUENCE"]
