import { Handle, Position } from "reactflow";

export default function StartNode({ data }) {

  return (

    <div
      style={{
        background: "#0F827F",
        color: "white",
        padding: "14px 40px",
        borderRadius: "999px",
        fontWeight: "bold",
        border: "2px solid #0B5F5C",
        position: "relative"
      }}
    >

      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
      />

      {data.label}

    </div>
  );
}