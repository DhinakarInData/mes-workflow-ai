import React from "react";

import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath
} from "reactflow";


export default function CustomOrthogonalEdge(props) {

  console.log("FULL EDGE PROPS =", props);

  const {
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
    labelStyle,
    data
  } = props;

  console.log(
  "ROUTING",
  label,
  data?.routing_type,
  data?.lane_offset
);
  // ===================================
  // ROUTING OFFSET
  // ===================================

  let offset = 30;

    if (data?.routing_type === "RIGHT_EXTERNAL") {

      offset = 150 + (data.lane_offset || 0 * 120);

      }

    else if (data?.routing_type === "OUTER_LOOP") {

    offset = 250 + (data.lane_offset * 50);

    }

  // } else if (data?.routing_type === "DOWN") {

  //   offset = 30;

  // } else if (data?.routing_type === "VERTICAL") {

  //   offset = 30;
  // }

  // ===================================
  // EDGE PATH
  // ===================================

  const [edgePath, labelX, labelY] =
    getSmoothStepPath({

      sourceX,
      sourceY,

      targetX,
      targetY,

      sourcePosition,
      targetPosition,

      borderRadius: 16,

      offset
    });

  // ===================================
  // EDGE COLOR
  // ===================================

  let edgeColor = "#6B7280";

  if (data?.routing_type === "RIGHT_EXTERNAL") {

    edgeColor = "#DC2626";

  } else if (data?.routing_type === "OUTER_LOOP") {

    edgeColor = "#2563EB";

  } else if (data?.routing_type === "DOWN") {

    edgeColor = "#16A34A";
  }
  return (

    <>

      <BaseEdge

        id={id}

        path={edgePath}

        markerEnd={markerEnd}

        style={{

          stroke: edgeColor,

          strokeWidth: 2,

          ...style
        }}
      />

      {

        label && (

          <EdgeLabelRenderer>

            <div

              style={{

                position: "absolute",

                transform: `translate(-50%, -50%) 
                translate(${labelX}px, ${labelY}px)`,

                background: "white",

                padding: "4px 8px",

                borderRadius: "6px",

                fontSize: "11px",

                fontWeight: 700,

                color: edgeColor,

                border: `1px solid ${edgeColor}`,

                whiteSpace: "nowrap",

                pointerEvents: "all",

                zIndex: 9999,

                ...labelStyle
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