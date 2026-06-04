import {
  Handle,
  Position
} from "reactflow";


export default function DecisionNode({ data }) {

  const width = 160;

  const height = 160;


  return (

    <div
      style={{

        width,

        height,

        background: "#1E3A8A",

        border: "2px solid #3B82F6",

        transform: "rotate(45deg)",

        display: "flex",

        alignItems: "center",

        justifyContent: "center",

        color: "white",

        position: "relative"
      }}
    >

      {/* TARGET */}
      <Handle
        type="target"
        position={Position.Top}
        id="in"
      />


      {/* YES FLOW */}
      <Handle
        type="source"
        position={Position.Bottom}
        id="yes"
        style={{
          left: "50%",
          background: "#16A34A"
        }}
      />


      {/* NO FLOW */}
      <Handle
        type="source"
        position={Position.Right}
        id="no"
        style={{
          top: "35%",
          background: "#DC2626"
        }}
      />


      {/* LOOP FLOW */}
      <Handle
        type="source"
        position={Position.Left}
        id="loop"
        style={{
          top: "65%",
          background: "#2563EB"
        }}
      />


      <div
        style={{

          transform: "rotate(-45deg)",

          width: "120px",

          textAlign: "center",

          fontWeight: "bold",

          fontSize: "13px",

          lineHeight: "1.5",

          whiteSpace: "normal",

          wordBreak: "break-word",

          overflowWrap: "break-word"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}