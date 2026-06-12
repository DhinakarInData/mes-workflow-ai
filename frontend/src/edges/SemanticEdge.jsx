import React from "react";

import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath
} from "reactflow";


// ===================================
// SEMANTIC EDGE
// ===================================

function SemanticEdge({

  id,

  sourceX,

  sourceY,

  targetX,

  targetY,

  sourcePosition,

  targetPosition,

  markerEnd,

  style,

  label,
  data
})

  {
  console.log("EDGE DEBUG",
      id,
      data
    );


  // ===================================
  // SEMANTIC OFFSET
  // ===================================

  let edgeOffset = 30;


  // ===================================
  // NO FLOW
  // ===================================

  if (label === "NO") {

    edgeOffset = 60;
  }


  // ===================================
  // RETRY / REWORK
  // ===================================

  if (

    label === "RETRY"

    ||

    label === "REWORK"

  ) {

    edgeOffset = 90;
  }


  // ===================================
  // EDGE PATH
  // ===================================

  const [edgePath, labelX, labelY] = getSmoothStepPath({

    sourceX,

    sourceY,

    targetX,

    targetY,

    sourcePosition,

    targetPosition,

    borderRadius: 18,

    offset: edgeOffset
  });


  // ===================================
  // EDGE COLOR
  // ===================================

  let edgeColor = "#64748B";


  // ===================================
  // YES FLOW
  // ===================================

  if (label === "YES") {

    edgeColor = "#16A34A";
  }


  // ===================================
  // NO FLOW
  // ===================================

  else if (label === "NO") {

    edgeColor = "#DC2626";
  }


  // ===================================
  // RETRY / REWORK
  // ===================================

  else if (

    label === "RETRY"

    ||

    label === "REWORK"

  ) {

    edgeColor = "#2563EB";
  }


  // ===================================
  // EDGE WIDTH
  // ===================================

  let edgeWidth = 2;


  // ===================================
  // LOOP EMPHASIS
  // ===================================

  if (

    label === "RETRY"

    ||

    label === "REWORK"

  ) {

    edgeWidth = 3;
  }


  // ===================================
  // DASH STYLE
  // ===================================

  let dashStyle = undefined;


  if (label === "RETRY") {

    dashStyle = "8 4";
  }


  // ===================================
  // RENDER
  // ===================================

  return (

    <>

      {/* ===================================
          EDGE
      =================================== */}

      <BaseEdge

        id={id}

        path={edgePath}

        markerEnd={markerEnd}

        style={{

          stroke: edgeColor,

          strokeWidth: edgeWidth,

          strokeDasharray: dashStyle,

          ...style
        }}
      />


      {/* ===================================
          LABEL
      =================================== */}

      {

        label && (

          <EdgeLabelRenderer>

            <div

              style={{

                position: "absolute",

                transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,

                background: "white",

                padding: "3px 8px",

                borderRadius: "6px",

                fontSize: "11px",

                fontWeight: 700,

                color: edgeColor,

                border: `1px solid ${edgeColor}`,

                boxShadow: "0 1px 4px rgba(0,0,0,0.15)",

                pointerEvents: "all",

                whiteSpace: "nowrap",

                zIndex: 1000
              }}
            >

              {label}

            </div>

          </EdgeLabelRenderer>
        )
      }

    </>
  );
}


export default SemanticEdge;