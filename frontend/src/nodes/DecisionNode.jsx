import {

  Handle,

  Position

} from "reactflow";


export default function DecisionNode({ data }) {

  return (

    <div
      style={{
        width: "180px",
        height: "180px",
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

      {/* TOP TARGET */}

      <Handle
        type="target"
        position={Position.Top}
        id="top"
      />


      {/* LEFT SOURCE */}

      <Handle
        type="source"
        position={Position.Left}
        id="left"
      />


      {/* RIGHT SOURCE */}

      <Handle
        type="source"
        position={Position.Right}
        id="right"
      />


      {/* BOTTOM SOURCE */}

      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
      />


      <div
        style={{
          transform: "rotate(-45deg)",
          textAlign: "center",
          width: "110px",
          fontWeight: "bold"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}