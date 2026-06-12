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
  const laneOffset = Number(data?.lane_offset || 0);

  let edgePath;
  let labelX;
  let labelY;

  if (data?.routing_type === "RIGHT_EXTERNAL") {

    const labelLift = 18 + ((laneOffset - 1) % 2) * 16;

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${targetX} ${sourceY}
      L ${targetX} ${targetY}
    `;

    labelX = sourceX + ((targetX - sourceX) * 0.52);
    labelY = sourceY - labelLift;

  } else if (data?.routing_type === "MERGE_JOIN") {

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${targetX} ${sourceY}
      L ${targetX} ${targetY}
    `;

    labelX = targetX;
    labelY = sourceY;

  } else if (data?.routing_type === "OUTER_LOOP") {

    const returnLaneX =
      Math.max(sourceX, targetX) +
      220 +
      laneOffset * 80;

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${returnLaneX} ${sourceY}
      L ${returnLaneX} ${targetY}
      L ${targetX} ${targetY}
    `;

    labelX = returnLaneX - 90;
    labelY = sourceY - 18;

  } else if (data?.routing_type === "DOWN") {

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${sourceX} ${targetY}
    `;

    labelX = sourceX + 38;
    labelY = sourceY + ((targetY - sourceY) * 0.32);

  } else if (data?.routing_type === "VERTICAL") {

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${targetX} ${targetY}
    `;

    labelX = sourceX;
    labelY = sourceY + ((targetY - sourceY) * 0.5);

  } else {

    const pathResult =
      getSmoothStepPath({

        sourceX,
        sourceY,

        targetX,
        targetY,

        sourcePosition,
        targetPosition,

        borderRadius: 16,

        offset: 30
      });

    edgePath = pathResult[0];
    labelX = pathResult[1];
    labelY = pathResult[2];
  }

  // ===================================
  // EDGE COLOR
  // ===================================

  let edgeColor = "#6B7280";

  if (data?.routing_type === "RIGHT_EXTERNAL") {

    edgeColor = "#DC2626";

  } else if (data?.routing_type === "OUTER_LOOP") {

    edgeColor = "#2563EB";

  } else if (data?.routing_type === "MERGE_JOIN") {

    edgeColor = "#6B7280";

  } else if (data?.routing_type === "DOWN") {

    edgeColor = "#16A34A";
  }

  const isMergeJoin =
    data?.routing_type === "MERGE_JOIN";

  const strokeWidth =
    data?.routing_type === "OUTER_LOOP"
      ? 2.5
      : 2;

  const strokeDasharray =
    isMergeJoin
      ? "4 4"
      : undefined;

  return (

    <>

      <BaseEdge

        id={id}

        path={edgePath}

        markerEnd={markerEnd}

        style={{

          stroke: edgeColor,

          strokeWidth,

          strokeDasharray,

          ...style
        }}
      />

      {

        label && !isMergeJoin && (

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
