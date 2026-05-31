import {

  Handle,

  Position

} from "reactflow";


export default function ErrorNode({ data }) {

  return (

    <div
      style={{
        width: "190px",
        background: "#7F1D1D",
        color: "white",
        border: "2px solid #DC2626",
        borderRadius: "6px",
        overflow: "hidden",
        position: "relative"
      }}
    >

      {/* TOP TARGET */}

      <Handle
        type="target"
        position={Position.Top}
        id="top"
      />


      {/* LEFT TARGET */}

      <Handle
        type="target"
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
          background: "#DC2626",
          padding: "8px",
          textAlign: "center",
          fontWeight: "bold"
        }}
      >
        ERROR
      </div>


      <div
        style={{
          padding: "16px",
          textAlign: "center",
          fontWeight: "bold"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}