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

  return (

    <div

      style={{

        width: data.width || 240,

        minHeight: data.height || 100,

        background: "#0F766E",

        color: "white",

        border: "2px solid #14B8A6",

        borderRadius: "10px",

        overflow: "hidden",

        position: "relative",

        display: "flex",

        flexDirection: "column",

        boxShadow:

          "0 4px 10px rgba(0,0,0,0.15)"
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

          padding: "10px",

          fontWeight: "bold",

          textAlign: "center",

          background: "#115E59",

          borderBottom:
            "1px solid #14B8A6",

          fontSize: "13px",

          letterSpacing: "0.5px"
        }}
      >

        SYSTEM

      </div>


      {/* ===================================
          LABEL
      =================================== */}

      <div

        style={{

          padding: "16px",

          textAlign: "center",

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