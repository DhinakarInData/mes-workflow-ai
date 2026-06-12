import {
  Handle,
  Position
} from "reactflow";

export default function SystemCheckNode({ data }) {

  return (

    <div
      style={{
        minWidth: 220,
        minHeight: 70,

        padding: "12px 20px",

        background: "#C2410C",

        border: "2px solid #EA580C",

        borderRadius: "40px",

        color: "white",

        textAlign: "center",

        fontWeight: "bold",

        position: "relative",

        display: "flex",

        alignItems: "center",

        justifyContent: "center"
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


      <div>

        <div
          style={{
            fontSize: "11px",
            marginBottom: "4px"
          }}
        >
          CHECK
        </div>

        <div
          style={{
            fontSize: "12px",
            lineHeight: "1.3"
          }}
        >
          {data.label}
        </div>

      </div>

    </div>
  );
}