START Start

ACTIVITY Scan Barcode

DECISION Verified?

ACTIVITY Charge Material

ACTIVITY Re-Scan Barcode

END End

FLOW:
Start -> Scan Barcode
Scan Barcode -> Verified?
Verified? -> Charge Material [YES]
Verified? -> Re-Scan Barcode [NO]
Re-Scan Barcode -> Scan Barcode [LOOPBACK]
Charge Material -> End