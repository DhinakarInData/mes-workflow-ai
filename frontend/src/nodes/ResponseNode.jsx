import {
  Handle,
  Position
} from "reactflow";





export default function ResponseNode({ data }) {
const actor = data.response_actor || "SYSTEM";

const DIAMOND_WIDTH = 112;
const DIAMOND_HEIGHT = 86;

const colors = {
  SYSTEM: "#1E3A8A",
  OPERATOR: "#EA580C",
  SUPERVISOR: "#7C3AED",
  QA: "#16A34A",
  USER: "#0F766E"
};

const bgColor = colors[actor] || "#1E3A8A";

const rawActor =
  String(data.response_actor || data.actor || "")
    .trim()
    .toUpperCase();

const actorLabels = {
  SYSTEM: "System",
  OPERATOR: "Operator",
  SUPERVISOR: "Supervisor",
  QA: "QA",
  USER: "User"
};

const actorLabel =
  actorLabels[rawActor] || rawActor;

const rawDisplayLabel =
  String(data.label || "Response")
    .trim();

const displayLabel =
  /response$/i.test(rawDisplayLabel)
    ? rawDisplayLabel.replace(
        /^(SYSTEM|USER|OPERATOR|SUPERVISOR|QA)\s+/i,
        actorLabel ? `${actorLabel} ` : ""
      )
    : actorLabel
    ? `${actorLabel} Response`
    : rawDisplayLabel;

const stepNumber =
  data.display_step_number || data.step_number;

const responseLabel =
  stepNumber
    ? `${stepNumber}: ${displayLabel}`
    : displayLabel;

const hiddenHandleStyle = {
  opacity: 0,
  pointerEvents: "none"
};

  return (

    <div

      style={{
        width: DIAMOND_WIDTH,
        height: DIAMOND_HEIGHT,
        position: "relative"
      }}
    >

      <div
        style={{
          position: "absolute",
          inset: 0,

          background: "#3B82F6",

          clipPath: "polygon(50% 0, 100% 50%, 50% 100%, 0 50%)",

          display: "flex",

          alignItems: "center",

          justifyContent: "center",

          color: "white"
        }}
      >

        <div
          style={{
            position: "absolute",

            inset: 3,

            background: bgColor,

            clipPath: "polygon(50% 0, 100% 50%, 50% 100%, 0 50%)",

            display: "flex",

            alignItems: "center",

            justifyContent: "center",

            padding: "10px 18px",

            boxSizing: "border-box"
          }}
        >

          <div
            style={{

              width: "82px",

              boxSizing: "border-box",

              textAlign: "center",

              fontWeight: "bold",

              fontSize: "11px",

              lineHeight: "1.2",

              whiteSpace: "normal",

              wordBreak: "break-word",

              overflowWrap: "break-word"
            }}
          >
            {responseLabel}
          </div>

        </div>

      </div>

       <Handle

        type="target"

        position={Position.Top}

        id="target"

        style={{
          top: 0,
          left: "50%"
        }}
      />


      {/* ===================================
          LEFT TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Left}

        id="loopback"

        style={{
          top: "50%",
          left: 0
        }}
      />


      {/* ===================================
          LEFT RESTART SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Left}

        id="restart"

        style={{
          top: "50%",
          left: 0,
          ...hiddenHandleStyle
        }}
      />


      {/* ===================================
          RIGHT SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Right}

        id="error"

        style={{
          top: "50%",
          right: 0
        }}
      />


      {/* ===================================
          BOTTOM SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Bottom}

        id="success"

        style={{
          bottom: 0,
          left: "50%"
        }}
      />

    </div>
  );
}
