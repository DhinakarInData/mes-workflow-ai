import {
  Handle,
  Position
} from "reactflow";


export default function ManualActivityNode({ data }) {

  const width = data.width || 220;

  const height = data.height || 100;


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


      {/* ===================================
          LEFT TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Left}

        id="loopback"
      />


      {/* ===================================
          RIGHT SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Right}

        id="error"
      />


      {/* ===================================
          BOTTOM SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Bottom}

        id="success"
      />



      {/* HEADER */}
      <div
        style={{
          padding: "8px",
          fontWeight: "bold",
          textAlign: "center",
          background: "#1F2937",
          fontSize: "11px"
        }}
      >
        {data.step_number}
      </div>


      {/* BODY */}
      <div
        style={{
          padding: "18px",
          textAlign: "center",
          lineHeight: "1.5",
          wordBreak: "break-word",
          whiteSpace: "normal",
          fontSize: "13px"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}