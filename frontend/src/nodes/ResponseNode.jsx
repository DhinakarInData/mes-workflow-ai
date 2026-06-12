import {
  Handle,
  Position
} from "reactflow";





export default function ResponseNode({ data }) {
const actor = data.response_actor || "SYSTEM";

const colors = {
  SYSTEM: "#1E3A8A",
  OPERATOR: "#EA580C",
  SUPERVISOR: "#7C3AED",
  QA: "#16A34A",
  USER: "#0F766E"
};

const bgColor = colors[actor] || "#1E3A8A";
  return (

    <div

    
      style={{
        width: 110,
        height: 110,

        background: bgColor,

        border: "2px solid #3B82F6",

        transform: "rotate(45deg)",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        color: "white",

        position: "relative"
        
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

      <div
        style={{
          transform: "rotate(-45deg)",

          width: "95px",

          padding: "4px",

          boxSizing: "border-box",

          textAlign: "center",

          fontWeight: "bold",

          fontSize: "12px",

          lineHeight: "1.3",

          whiteSpace: "normal",

          wordBreak: "break-word",

          overflowWrap: "break-word"
        }}
      >
        <div>
  <div>{data.response_actor || "SYSTEM"}</div>
  <div>{data.label}</div>
</div>
      </div>

    </div>
  );
}