# Equipment Line Clearance

## Reference Screenshot

equipment_lc_error_branch_reference.png

## Expected Behavior

1. Main workflow should remain vertically aligned.
2. Error branches should appear on the right side.
3. Invalid Equipment should loop back to Scan Equipment.
4. Incorrect Equipment should loop back to Scan Equipment.
5. Line Clearance Not Done should loop back to Scan Equipment.
6. Success path should continue downward.

---

## Current Render v1 Observations

1. Error labels overlap near System Response.
2. RIGHT_EXTERNAL branches are not visually separated enough.
3. Loopback lines cross the workflow.
4. Merge routing is visible to the user.
5. Layout does not yet match FDS structure.

### Backend Status

✓ Graph generation

✓ Routing classification

✓ Merge node generation

✓ ReactFlow JSON generation

### Frontend Status

✗ Edge routing

✗ Loopback rendering

✗ Label placement

✗ Error branch spacing

### Current Focus

Investigate CustomOrthogonalEdge.jsx rendering behavior and lane_offset usage.