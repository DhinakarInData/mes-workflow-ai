import google.generativeai as genai

import json

from pathlib import Path

import time

from config import GEMINI_API_KEY

genai.configure(
    api_key=GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

GENERATE_TIMEOUT_SECONDS = 90

RETRY_SLEEP_SECONDS = 5



def extract_json_object(result):

    start = result.find("{")
    end = result.rfind("}")

    if start == -1 or end == -1 or end < start:

        raise ValueError(
            "AI response did not contain a JSON object"
        )

    return result[start:end+1]


def find_collapsed_response_branches(ir):

    nodes_by_id = {
        node.get("id"): node
        for node in ir.get(
            "nodes",
            []
        )
    }

    node_order = {
        node.get("id"): index
        for index, node in enumerate(
            ir.get(
                "nodes",
                []
            )
        )
    }

    conditional_targets = {}

    for edge in ir.get(
        "edges",
        []
    ):

        if edge.get("edge_type") != "CONDITIONAL":

            continue

        source = nodes_by_id.get(
            edge.get("source")
        )

        target = nodes_by_id.get(
            edge.get("target")
        )

        if not source or source.get("type") != "RESPONSE":

            continue

        if not target or target.get("type") == "END":

            continue

        key = (
            edge.get("source"),
            edge.get("target")
        )

        conditional_targets.setdefault(
            key,
            set()
        ).add(
            edge.get("condition") or ""
        )

    collapsed = []

    for (
        source,
        target
    ), conditions in conditional_targets.items():

        cleaned_conditions = {
            condition
            for condition in conditions
            if condition
        }

        if len(cleaned_conditions) < 2:

            continue

        if is_retry_return_option_group(
            nodes_by_id,
            node_order,
            source,
            target,
            cleaned_conditions
        ):

            continue

        collapsed.append(
            {
                "source": source,
                "target": target,
                "conditions": sorted(
                    cleaned_conditions
                )
            }
        )

    return collapsed


def normalize_condition_text(value):

    return (
        value
        or ""
    ).strip().upper().replace(
        "_",
        " "
    )


def is_retry_failure_condition(condition):

    label = normalize_condition_text(
        condition
    )

    if not label:

        return False

    success_terms = {
        "YES",
        "NO",
        "VALID",
        "CORRECT",
        "PASS",
        "APPROVED",
        "COMPLETE",
        "CONTINUE"
    }

    if label in success_terms:

        return False

    retry_failure_terms = [
        "INVALID",
        "INCORRECT",
        "MISMATCH",
        "NOT",
        "FAIL",
        "FAILED",
        "ERROR",
        "DUE",
        "EXPIRED",
        "ABOVE",
        "BELOW",
        "OUT OF RANGE",
        "OUTSIDE RANGE",
        "ALREADY",
        "DUPLICATE"
    ]

    return any(
        term in label
        for term in retry_failure_terms
    )


def is_retry_return_option_group(
    nodes_by_id,
    node_order,
    source,
    target,
    conditions
):

    source_node = nodes_by_id.get(
        source
    )

    target_node = nodes_by_id.get(
        target
    )

    if not source_node or not target_node:

        return False

    if source_node.get("type") != "RESPONSE":

        return False

    if target_node.get("type") == "END":

        return False

    source_index = node_order.get(
        source
    )

    target_index = node_order.get(
        target
    )

    if source_index is None or target_index is None:

        return False

    if target_index >= source_index:

        return False

    return all(
        is_retry_failure_condition(
            condition
        )
        for condition in conditions
    )


def find_non_response_conditional_sources(ir):

    nodes_by_id = {
        node.get("id"): node
        for node in ir.get(
            "nodes",
            []
        )
    }

    violations = []

    for edge in ir.get(
        "edges",
        []
    ):

        if edge.get("edge_type") != "CONDITIONAL":

            continue

        source = nodes_by_id.get(
            edge.get("source")
        )

        target = nodes_by_id.get(
            edge.get("target")
        )

        if not source or not target:

            continue

        if source.get("type") == "RESPONSE":

            continue

        violations.append(
            {
                "source": edge.get("source"),
                "source_type": source.get("type"),
                "target": edge.get("target"),
                "condition": edge.get("condition") or ""
            }
        )

    return violations


def validate_extracted_ir(ir):

    non_response_conditionals = find_non_response_conditional_sources(
        ir
    )

    if non_response_conditionals:

        details = "; ".join(
            f"{item['source']} ({item['source_type']}) -> {item['target']} condition {item['condition']}"
            for item in non_response_conditionals
        )

        raise ValueError(
            "Conditional branches must originate from RESPONSE nodes: "
            + details
        )

    collapsed = find_collapsed_response_branches(
        ir
    )

    if collapsed:

        details = "; ".join(
            f"{item['source']} -> {item['target']} for {', '.join(item['conditions'])}"
            for item in collapsed
        )

        raise ValueError(
            "Collapsed response option branches detected: "
            + details
        )


def correction_instruction(error):

    return (
        "\n\nThe previous JSON was structurally invalid for FDS rendering. "
        + str(error)
        + "\nDo not route multiple distinct response conditions to the same "
        + "non-terminal activity when each condition describes its own branch. "
        + "All CONDITIONAL edges must originate from RESPONSE nodes. Insert "
        + "the appropriate Operator, User, Supervisor, QA, or System Response "
        + "node before branching. "
        + "Create separate branch nodes and converge only at the next explicit "
        + "common activity. Return JSON only."
    )


def extract_workflow(text, write_debug=True):

    prompt_path = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "ai_prompt_v1.txt"
    )

    with open(
        prompt_path,
        "r",
        encoding="utf-8"
    ) as file:

        base_prompt = file.read()

    prompt = base_prompt.replace(
        "{{WORKFLOW_TEXT}}",
        text
    )

    for attempt in range(3):

        try:

            response = model.generate_content(
                prompt,
                request_options={
                    "timeout": GENERATE_TIMEOUT_SECONDS
                }
            )

            result = response.text
            if write_debug:
                with open(
                    "debug_output.json",
                    "w",
                    encoding="utf-8"
                ) as f:
                    f.write(result)

            result = extract_json_object(
                result
            )

            ir = json.loads(
                result
            )

            validate_extracted_ir(
                ir
            )

            return result

        except Exception as e:

            print(
                f"Attempt {attempt+1} failed:",
                e
            )

            prompt = (
                base_prompt.replace(
                    "{{WORKFLOW_TEXT}}",
                    text
                )
                + correction_instruction(
                    e
                )
            )

            if not isinstance(
                e,
                ValueError
            ):

                time.sleep(RETRY_SLEEP_SECONDS)

    raise Exception(
        "Gemini failed after 3 attempts"
    )
