# AI Workflow Extraction Contract

## Purpose

Convert natural language MES workflow descriptions into a standardized Intermediate Representation (IR).

The AI must not generate diagrams.

The AI must only generate workflow IR JSON.

---

## Input

Natural language workflow description.

Example:

User scan material barcode

System checks material exists

If valid proceed

If invalid show error

End workflow

---

## Output

Valid JSON only.

```json
{
  "workflow_name": "Material Verification",
  "nodes": [],
  "edges": []
}
```

---

## Node Types

### START

Workflow start node.

Example:

```json
{
  "id": "START",
  "type": "START",
  "label": "Start"
}
```

---

### END

Workflow end node.

Example:

```json
{
  "id": "END",
  "type": "END",
  "label": "End"
}
```

---

### MANUAL_ACTIVITY

User action.

Examples:

* Scan material
* Select batch
* Enter quantity
* Confirm transaction

Example:

```json
{
  "id": "A1",
  "type": "MANUAL_ACTIVITY",
  "label": "Scan material"
}
```

---

### SYSTEM_CHECK

System validation.

Examples:

* Check material exists
* Check inventory available
* Check equipment status

Example:

```json
{
  "id": "A2",
  "type": "SYSTEM_CHECK",
  "label": "Check material exists"
}
```

---

### SYSTEM_ACTIVITY

System action.

Examples:

* Update inventory
* Create transaction
* Fetch material details

Example:

```json
{
  "id": "A3",
  "type": "SYSTEM_ACTIVITY",
  "label": "Update inventory"
}
```

---

### DECISION

Branching node.

Example:

```json
{
  "id": "D1",
  "type": "DECISION",
  "label": "Material Valid?"
}
```

---

## Edge Types

### SEQUENCE

Normal flow.

Example:

```json
{
  "source": "A1",
  "target": "A2",
  "edge_type": "SEQUENCE"
}
```

---

### CONDITIONAL

Decision branch.

Example:

```json
{
  "source": "D1",
  "target": "A3",
  "condition": "YES",
  "edge_type": "CONDITIONAL"
}
```

---

### LOOPBACK

Retry or rework path.

Example:

```json
{
  "source": "A5",
  "target": "A2",
  "edge_type": "LOOPBACK"
}
```

---

## AI Requirements

The AI must identify:

* Manual activities
* System checks
* System activities
* Decisions
* Decision branches
* Loopbacks
* End conditions

The AI must not generate ReactFlow JSON.

The AI must not generate coordinates.

The AI must not generate layout information.

The AI must only generate workflow IR.

```
```
