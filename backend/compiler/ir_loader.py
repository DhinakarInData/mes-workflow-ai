import json

from compiler.ir_validator import (
    validate_ir
)

def load_ir(path):

    with open(path, "r") as f:

        return json.load(f)


if __name__ == "__main__":

    data = load_ir(
        "schemas/sample_bin_picking_ir.json"
    )

    print(data["workflow_name"])

    print(
        len(data["nodes"])
    )

    print(
        len(data["edges"])
    )
    
    errors = validate_ir(data)

    if len(errors) == 0:

        print(
        "\nIR VALID"
    )

    else:

        print(
        "\nIR INVALID"
    )

    for error in errors:

        print(error)