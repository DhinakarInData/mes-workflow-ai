import {

  Handle,

  Position

} from "reactflow";


export default function ManualActivityNode({ data }) {

  return (

    <div
      style={{
        width: "180px",
        background: "#111827",
        color: "white",
        border: "2px solid #374151",
        borderRadius: "8px",
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
          padding: "8px",
          fontWeight: "bold",
          textAlign: "center",
          background: "#1F2937"
        }}
      >
        {data.step_number}
      </div>


      <div
        style={{
          padding: "18px",
          textAlign: "center"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}