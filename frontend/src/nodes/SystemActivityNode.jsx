import {

  Handle,

  Position

} from "reactflow";


export default function SystemActivityNode({ data }) {

  return (

    <div
      style={{
        width: "190px",
        background: "#0F766E",
        color: "white",
        border: "2px solid #14B8A6",
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
          background: "#115E59"
        }}
      >
        SYSTEM
      </div>


      <div
        style={{
          padding: "16px",
          textAlign: "center"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}