import {

  Handle,

  Position

} from "reactflow";


// ===================================
// SYSTEM ACTIVITY NODE
// ===================================

export default function SystemActivityNode({

  data
}) {

  const stepNumber =
    data.display_step_number || data.step_number;

  const isErrorActivity =
    data.is_error_activity
    || data.group === "ERROR_HANDLING";

  const isLinkedWorkflow =
    data.visual_type === "LINKED_WORKFLOW"
    || data.metadata?.visual_type === "LINKED_WORKFLOW"
    || String(data.label || "")
      .toUpperCase()
      .includes("LINKED WORKFLOW");

  const hiddenHandleStyle = {
    opacity: 0,
    pointerEvents: "none"
  };

  const containerStyle = isErrorActivity
    ? {
        width: data.width || 240,

        minHeight: 72,

        background: "#FFFFFF",

        color: "#111827",

        border: "2px solid #111827",

        borderRadius: "2px",

        overflow: "hidden",

        position: "relative",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        boxShadow: "none"
      }
    : isLinkedWorkflow
    ? {
        width: data.width || 240,

        minHeight: 72,

        background: "#FFFFFF",

        color: "#111827",

        border: "2px solid #8B3A2B",

        borderRadius: "2px",

        overflow: "hidden",

        position: "relative",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        boxShadow: "none"
      }
    : {
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
      };

  return (

    <div

      style={containerStyle}
    >

      {/* ===================================
          TOP TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Top}

        id="target"
      />

      <Handle

        type="source"

        position={Position.Top}

        id="top_retry"

        style={{
          left: "50%",
          ...hiddenHandleStyle
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
          top: "50%"
        }}
      />


      {/* ===================================
          LEFT LOCAL RETRY SOURCE
      =================================== */}

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


      {/* ===================================
          LABEL
      =================================== */}

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

        {stepNumber
          ? `${stepNumber}: ${data.label}`
          : data.label}

      </div>

    </div>
  );
}
