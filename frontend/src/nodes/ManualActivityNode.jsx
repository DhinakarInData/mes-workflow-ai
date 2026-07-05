import {
  Handle,
  Position
} from "reactflow";


export default function ManualActivityNode({ data }) {

  const width = data.width || 220;

  const height = data.height || 100;

  const stepNumber =
    data.display_step_number || data.step_number;

  const hiddenHandleStyle = {
    opacity: 0,
    pointerEvents: "none"
  };


  return (

    <div
      style={{
        width,
        minHeight: height,
        background: "#111827",
        color: "white",
        border: "2px solid #374151",
        borderRadius: "8px",
        overflow: "hidden",
        position: "relative",

        display: "flex",
        flexDirection: "column",
        justifyContent: "center"
      }}
    >

      {/* TOP TARGET */}
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


      {/* LEFT LOCAL RETRY SOURCE */}
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



      {/* HEADER */}
      <div
        style={{
          padding: "14px 18px",
          textAlign: "center",
          lineHeight: "1.5",
          wordBreak: "break-word",
          whiteSpace: "normal",
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
