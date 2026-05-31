import {

  Handle,

  Position

} from "reactflow";


export default function ConnectorNode({ data }) {

  return (

    <div
      style={{
        width: "70px",
        height: "70px",
        borderRadius: "50%",
        background: "#374151",
        border: "3px solid #9CA3AF",
        color: "white",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: "bold",
        fontSize: "20px",
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


      {data.label}

    </div>
  );
}