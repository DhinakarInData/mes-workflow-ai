import { Handle, Position } from "reactflow";

export default function EndNode({ data }) {

  return (

    <div
      style={{
        background: "#27344A",
        color: "white",
        padding: "14px 40px",
        borderRadius: "999px",
        fontWeight: "bold",
        border: "2px solid #0c111c",
        position: "relative"
      }}
    >

      <Handle
        type="target"
        position={Position.Top}
        id="target"
      />

      {data.label}

    </div>
  );
}
