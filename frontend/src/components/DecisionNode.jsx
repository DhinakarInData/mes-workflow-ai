import { Handle, Position } from "reactflow";


export default function DecisionNode({ data }) {

  return (

    <div
      style={{
        width: 120,
        height: 120,

        background: "#fde68a",

        border: "2px solid #d97706",

        transform: "rotate(45deg)",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        position: "relative"
      }}
    >

      {/* ================================
          TOP HANDLE
      ================================= */}

      <Handle
        type="target"
        position={Position.Top}
      />


      {/* ================================
          RIGHT HANDLE
      ================================= */}

      <Handle
        type="source"
        id="yes"
        position={Position.Right}
      />


      {/* ================================
          BOTTOM HANDLE
      ================================= */}

      <Handle
        type="source"
        id="no"
        position={Position.Bottom}
      />


      {/* ================================
          LABEL
      ================================= */}

      <div
        style={{
          transform: "rotate(-45deg)",

          textAlign: "center",

          width: 80,

          fontWeight: 600,

          fontSize: 13,

          lineHeight: "18px"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}