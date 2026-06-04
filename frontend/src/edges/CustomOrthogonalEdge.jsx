import React from "react";

import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath
} from "reactflow";


export default function CustomOrthogonalEdge({

  id,

  sourceX,
  sourceY,

  targetX,
  targetY,

  sourcePosition,
  targetPosition,

  style = {},

  markerEnd,

  label,
  labelStyle

}) {

  // ===================================
  // ORTHOGONAL PATH
  // ===================================

  const [edgePath, labelX, labelY] = getSmoothStepPath({

    sourceX,
    sourceY,

    sourcePosition,

    targetX,
    targetY,

    targetPosition,

    borderRadius: 12,

    offset: 30
  });


  return (

    <>

      {/* EDGE */}

      <BaseEdge

        path={edgePath}

        markerEnd={markerEnd}

        style={{

          strokeWidth: 2,

          ...style
        }}
      />


      {/* LABEL */}

      {label && (

        <EdgeLabelRenderer>

          <div
            style={{

              position: "absolute",

              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,

              background: "white",

              padding: "2px 6px",

              border: "1px solid #CBD5E1",

              borderRadius: "4px",

              fontSize: "11px",

              fontWeight: 700,

              pointerEvents: "all",

              whiteSpace: "nowrap",

              ...labelStyle
            }}
          >
            {label}
          </div>

        </EdgeLabelRenderer>
      )}

    </>
  );
}