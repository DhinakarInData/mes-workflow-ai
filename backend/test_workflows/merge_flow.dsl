START Start

DECISION Material Type?

ACTIVITY Process A

ACTIVITY Process B

MERGE Merge Flow

END End

FLOW:
Start -> Material Type?
Material Type? -> Process A [TYPE_A]
Material Type? -> Process B [TYPE_B]
Process A -> Merge Flow
Process B -> Merge Flow
Merge Flow -> End