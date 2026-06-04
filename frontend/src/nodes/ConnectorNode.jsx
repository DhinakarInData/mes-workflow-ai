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

    70,

    Math.min(
      (data.width || 70),
      100
    )
  );


  return (

    <div

      style={{

        width: nodeSize,

        height: nodeSize,

        borderRadius: "50%",

        background: "#374151",

        border: "3px solid #9CA3AF",

        color: "white",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        fontWeight: "bold",

        fontSize: "18px",

        position: "relative",

        boxShadow:

          "0 4px 10px rgba(0,0,0,0.15)",

        textAlign: "center",

        padding: "6px",

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