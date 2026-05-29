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
        border: "2px solid #1B2433",
        position: "relative"
      }}
    >

      <Handle
        type="target"
        position={Position.Top}
        id="top"
      />

      {data.label}

    </div>
  );
}