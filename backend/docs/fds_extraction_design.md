# FDS Extraction Design

## 1. Supported Inputs

Phase 1:
- Text Input
- Voice Input (converted to text)

Future:
- PDF
- Word
- Screenshot

---

## 2. Output Schema

{
  "nodes": [],
  "edges": []
}

---

## 3. Node Detection Rules

START -> START

END -> END

System Response -> DECISION

Get / Check / Validate / Retrieve -> SYSTEM_ACTIVITY

Perform / Execute / Enter / Update -> MANUAL_ACTIVITY

---

## 4. Edge Detection Rules

Applicable -> Edge Label

Not Applicable -> Edge Label

Yes -> Edge Label

No -> Edge Label

Option 1 / Option 2 / Option 3 -> Edge Label

---

## 5. Step Number Rules

A1 -> a1

A1.1 -> a1_1

A1.2 -> a1_2

A2 -> a2