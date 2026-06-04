START Start

ACTIVITY Scan Barcode

DECISION Valid Material?

ACTIVITY Charge Material

ERROR Invalid Material

END End

FLOW:
Start -> Scan Barcode
Scan Barcode -> Valid Material?
Valid Material? -> Charge Material [YES]
Valid Material? -> Invalid Material [NO]
Charge Material -> End