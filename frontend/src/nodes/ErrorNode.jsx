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

      <Handle
        type="target"
        position={Position.Top}
        id="top"
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