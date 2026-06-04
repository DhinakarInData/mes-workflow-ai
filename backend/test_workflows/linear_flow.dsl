START Start

ACTIVITY Scan Barcode

ACTIVITY Verify Material

ACTIVITY Charge Material

END End

FLOW:
Start -> Scan Barcode
Scan Barcode -> Verify Material
Verify Material -> Charge Material
Charge Material -> End