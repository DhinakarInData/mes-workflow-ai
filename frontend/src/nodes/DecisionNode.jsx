import {
  Handle,
  Position
} from "reactflow";

export default function DecisionNode({ data }) {

  return (

    <div
      style={{
        width: "110px",
        height: "110px",
        position: "relative"
      }}
    >

      {/* TOP INPUT */}

      <Handle
        type="target"
        position={Position.Top}
        id="top"
      />

      {/* DEFAULT SEQUENCE */}

      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
      />

      {/* YES */}

      <Handle
        type="source"
        position={Position.Right}
        id="yes"
      />

      {/* NO */}

      <Handle
        type="source"
        position={Position.Left}
        id="no"
      />

      <div
        style={{
          width: "100%",
          height: "100%",
          background: "#E11D48",
          transform: "rotate(45deg)",
          border: "2px solid #BE123C",
          display: "flex",
          justifyContent: "center",
          alignItems: "center"
        }}
      >

        <div
          style={{
            transform: "rotate(-45deg)",
            color: "white",
            textAlign: "center",
            fontWeight: "bold",
            width: "70px",
            fontSize: "12px"
          }}
        >
          {data.label}
        </div>

      </div>

    </div>
  );
}