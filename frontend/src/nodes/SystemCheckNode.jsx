import {
  Handle,
  Position
} from "reactflow";

export default function SystemCheckNode({ data }) {

  const stepNumber =
    data.display_step_number || data.step_number;

  const displayLabel =
    stepNumber
      ? `${stepNumber}: ${data.label}`
      : data.label;

  const hiddenHandleStyle = {
    opacity: 0,
    pointerEvents: "none"
  };

  return (

    <div
      style={{
        width: data.width || 240,

        minHeight: 72,

        background: "#C2410C",

        color: "white",

        border: "2px solid #EA580C",

        borderRadius: "999px",

        overflow: "hidden",

        position: "relative",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        boxShadow:
          "0 4px 10px rgba(0,0,0,0.15)"
      }}
    >

      <Handle

        type="target"

        position={Position.Top}

        id="target"
      />


      {/* ===================================
          LEFT TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Left}

        id="loopback"

        style={{
          top: "50%"
        }}
      />


      <Handle

        type="source"

        position={Position.Left}

        id="restart"

        style={{
          top: "50%",
          ...hiddenHandleStyle
        }}
      />


      {/* ===================================
          RIGHT RETURN TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Right}

        id="return"

        style={{
          top: "50%"
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
          ...hiddenHandleStyle
        }}
      />


      {/* ===================================
          BOTTOM SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Bottom}

        id="success"
      />

      <Handle

        type="target"

        position={Position.Bottom}

        id="bottom"

        style={{
          left: "50%",
          ...hiddenHandleStyle
        }}
      />


      <div
        style={{
          padding: "14px 18px",

          textAlign: "center",

          display: "flex",

          alignItems: "center",

          justifyContent: "center",

          whiteSpace: "normal",

          wordBreak: "break-word",

          overflowWrap: "break-word",

          lineHeight: "1.5",

          fontSize: "13px",

          fontWeight: 700
        }}
      >
        {displayLabel}
      </div>

    </div>
  );
}
