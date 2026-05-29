import {
  Handle,
  Position
} from "reactflow";

export default function ManualActivityNode({ data }) {

  return (

    <div
      style={{
        width: "180px",
        background: "#2E3B52",
        color: "white",
        border: "2px solid #111827",
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

      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
      />

      <Handle
        type="source"
        position={Position.Left}
        id="retry"
      />

      <div
        style={{
          background: "#111827",
          padding: "8px",
          textAlign: "center",
          fontWeight: "bold"
        }}
      >
        {data.step_number}
      </div>

      <div
        style={{
          padding: "12px",
          textAlign: "center",
          fontSize: "12px"
        }}
      >
        MANUAL ACTIVITY
      </div>

      <div
        style={{
          paddingBottom: "16px",
          textAlign: "center",
          fontWeight: "bold"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}