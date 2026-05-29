import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
} from "reactflow";



export default function CustomWorkflowEdge({

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

  data,
}) {

  // ====================================
  // RETRY FLOW
  // ====================================

  if (

    data?.edgeType ===
    "RETRY_FLOW"

  ) {

    // ================================
    // DEDICATED RETRY LANE
    // ================================

    const retryLaneX =
      sourceX + 260;



    // ================================
    // CLEAN ENTRY POINT
    // ================================

    const retryEntryY =
      targetY - 50;



    // ================================
    // ORTHOGONAL RETRY PATH
    // ================================

    const path = `

      M ${sourceX} ${sourceY}

      L ${retryLaneX} ${sourceY}

      L ${retryLaneX} ${retryEntryY}

      L ${targetX} ${retryEntryY}

      L ${targetX} ${targetY}
    `;



    return (

      <>

        <BaseEdge
          path={path}
          style={style}
          markerEnd={markerEnd}
        />



        {/* ===========================
            RETRY LABEL
        ============================ */}

        <EdgeLabelRenderer>

          <div
            style={{

              position: "absolute",

              transform: `translate(-50%, -50%) translate(${retryLaneX - 40}px, ${sourceY - 20}px)`,

              fontSize: 12,

              fontWeight: 700,

              color: "#2563eb",

              pointerEvents: "all",

              background: "white",

              padding: "2px 6px",

              borderRadius: "6px",

              border:
                "1px solid #cbd5e1",
            }}
          >
            RETRY
          </div>

        </EdgeLabelRenderer>

      </>
    );
  }



  // ====================================
  // NORMAL EDGE
  // ====================================

  const [edgePath, labelX, labelY] =

    getSmoothStepPath({

      sourceX,
      sourceY,

      sourcePosition,

      targetX,
      targetY,

      targetPosition,
    });



  return (

    <>

      <BaseEdge
        path={edgePath}
        style={style}
        markerEnd={markerEnd}
      />



      {/* ===========================
          YES / NO LABELS
      ============================ */}

      {label && (

        <EdgeLabelRenderer>

          <div
            style={{

              position: "absolute",

              transform: `translate(-50%, -50%) translate(${labelX}px, ${labelY}px)`,

              fontSize: 12,

              fontWeight: 700,

              color:

                label === "YES"

                  ? "#16a34a"

                  : label === "NO"

                  ? "#dc2626"

                  : "#334155",

              background: "white",

              padding: "2px 6px",

              borderRadius: "6px",

              border:
                "1px solid #cbd5e1",

              pointerEvents: "all",
            }}
          >
            {label}
          </div>

        </EdgeLabelRenderer>
      )}

    </>
  );
}