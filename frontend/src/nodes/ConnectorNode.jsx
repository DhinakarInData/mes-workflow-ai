import {

  Handle,

  Position

} from "reactflow";


// ===================================
// CONNECTOR NODE
// ===================================

export default function ConnectorNode({

  data
}) {

  const nodeSize = Math.max(
    34,
    Math.min(
      (data.width || 44),
      52
    )
  );


  return (

    <div

      style={{

        width: nodeSize,

        height: nodeSize,

        borderRadius: "50%",

        background: "white",

        border: "2px solid #111827",

        color: "#111827",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        fontWeight: "bold",

        fontSize: "14px",

        position: "relative",

        boxShadow: "none",

        textAlign: "center",

        padding: "2px",

        whiteSpace: "normal",

        wordBreak: "break-word",

        overflowWrap: "break-word",

        lineHeight: "1.2"
      }}
    >

      {/* ===================================
          TOP TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Top}

        id="top"
      />


      {/* ===================================
          LEFT TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Left}

        id="left"
      />


      {/* ===================================
          RIGHT SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Right}

        id="right"
      />


      {/* ===================================
          BOTTOM SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Bottom}

        id="bottom"
      />


      {/* ===================================
          LABEL
      =================================== */}

      <div

        style={{

          width: "100%",

          display: "flex",

          alignItems: "center",

          justifyContent: "center"
        }}
      >

        {data.label}

      </div>

    </div>
  );
}
