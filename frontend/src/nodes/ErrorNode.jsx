import {

  Handle,

  Position

} from "reactflow";


// ===================================
// ERROR NODE
// ===================================

export default function ErrorNode({

  data
}) {

  return (

    <div

      style={{

        width: data.width || 240,

        minHeight: data.height || 100,

        background: "#7F1D1D",

        color: "white",

        border: "2px solid #DC2626",

        borderRadius: "10px",

        overflow: "hidden",

        position: "relative",

        display: "flex",

        flexDirection: "column",

        boxShadow:

          "0 4px 10px rgba(0,0,0,0.18)"
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
          HEADER
      =================================== */}

      <div

        style={{

          background: "#DC2626",

          padding: "10px",

          textAlign: "center",

          fontWeight: "bold",

          borderBottom:
            "1px solid #EF4444",

          fontSize: "13px",

          letterSpacing: "0.5px"
        }}
      >

        ERROR

      </div>


      {/* ===================================
          LABEL
      =================================== */}

      <div

        style={{

          padding: "16px",

          textAlign: "center",

          fontWeight: "bold",

          display: "flex",

          alignItems: "center",

          justifyContent: "center",

          flex: 1,

          whiteSpace: "normal",

          wordBreak: "break-word",

          overflowWrap: "break-word",

          lineHeight: "1.5",

          fontSize: "14px"
        }}
      >

        {data.label}

      </div>

    </div>
  );
}