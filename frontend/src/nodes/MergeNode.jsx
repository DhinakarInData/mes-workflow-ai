import { Handle, Position } from "reactflow";

export default function MergeNode() {

  return (

    <div
      style={{
        width: 40,
        height:40,
        borderRadius: "50%",
        background: "#111827"
      }}
    >

      <Handle

        type="target"

        position={Position.Top}

        id="target"
      />


      {/* ===================================
          LEFT TARGET
      =================================== */}

      <Handle

        type="target"

        position={Position.Left}

        id="loopback"
      />


      {/* ===================================
          RIGHT SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Right}

        id="error"
      />


      {/* ===================================
          BOTTOM SOURCE
      =================================== */}

      <Handle

        type="source"

        position={Position.Bottom}

        id="success"
      />

    </div>
  );
}