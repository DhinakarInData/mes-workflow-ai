import {
  Handle,
  Position
} from "reactflow";



// ======================================
// NODE COLORS
// ======================================

function getNodeColor(type) {

  switch (type) {

    case "QA_CHECK":
      return "#f59e0b";

    case "SIGNATURE":
      return "#9333ea";

    case "SYSTEM_SCAN":
      return "#2563eb";

    case "AUTO_STEP":
      return "#16a34a";

    case "NOTIFICATION":
      return "#dc2626";

    case "DECISION":
      return "#e11d48";

    case "CONNECTOR":
      return "#1e293b";

    case "START":
      return "#0f766e";

    case "END":
      return "#374151";

    default:
      return "#475569";
  }
}



// ======================================
// WORKFLOW NODE
// ======================================

export default function WorkflowNode({ data }) {

  const node = data.node;

  const bgColor = getNodeColor(
    node.workflow_type
  );



  // ======================================
  // COMMON HANDLES
  // ======================================

  const handles = (
    <>

      {/* ================================= */}
      {/* TARGET HANDLE */}
      {/* ================================= */}

      <Handle
        type="target"
        position={Position.Top}
      />



      {/* ================================= */}
      {/* DECISION HANDLES */}
      {/* ================================= */}

      {node.workflow_type === "DECISION" ? (

        <>

          {/* YES */}

          <Handle
            type="source"
            position={Position.Left}
            id="yes"
            style={{
              background: "#16a34a",
              width: 10,
              height: 10,
            }}
          />



          {/* NO */}

          <Handle
            type="source"
            position={Position.Right}
            id="no"
            style={{
              background: "#dc2626",
              width: 10,
              height: 10,
            }}
          />

        </>

      ) : (

        /* NORMAL FLOW */

        <Handle
          type="source"
          position={Position.Bottom}
        />
      )}

    </>
  );



  // ======================================
  // CONNECTOR NODE
  // ======================================

  if (node.workflow_type === "CONNECTOR") {

    return (

      <div
        style={{
          width: 60,
          height: 60,
          borderRadius: "50%",
          background: bgColor,
          border: "3px solid white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "white",
          fontWeight: "bold",
          fontSize: "18px",
          position: "relative",
        }}
      >

        {handles}

        {node.label}

      </div>
    );
  }



  // ======================================
  // DECISION NODE
  // ======================================

  if (node.workflow_type === "DECISION") {

    return (

      <div
        style={{
          width: 140,
          height: 140,
          transform: "rotate(45deg)",
          background: bgColor,
          border: "3px solid white",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          borderRadius: "12px",
          position: "relative",
        }}
      >

        {handles}

        <div
          style={{
            transform: "rotate(-45deg)",
            color: "white",
            textAlign: "center",
            fontWeight: "bold",
            fontSize: "12px",
            width: "90px",
          }}
        >
          {node.label}
        </div>

      </div>
    );
  }



  // ======================================
  // START / END NODE
  // ======================================

  if (

    node.workflow_type === "START" ||

    node.workflow_type === "END"

  ) {

    return (

      <div
        style={{
          background: bgColor,
          color: "white",
          borderRadius: "40px",
          border: "2px solid white",
          width: 220,
          padding: 14,
          textAlign: "center",
          fontWeight: "bold",
          fontSize: "14px",
          position: "relative",
        }}
      >

        {handles}

        {node.label}

      </div>
    );
  }



  // ======================================
  // DEFAULT NODE
  // ======================================

  return (

    <div
      style={{
        background: bgColor,
        color: "white",
        borderRadius: "12px",
        border: "2px solid white",
        width: 240,
        padding: 12,
        fontFamily: "Arial",
        position: "relative",
      }}
    >

      {handles}



      {/* ================================= */}
      {/* TITLE */}
      {/* ================================= */}

      <div
        style={{
          fontWeight: "bold",
          fontSize: "13px",
          marginBottom: "6px",
        }}
      >
        {node.label}
      </div>



      {/* ================================= */}
      {/* TYPE */}
      {/* ================================= */}

      <div
        style={{
          fontSize: "10px",
          opacity: 0.9,
        }}
      >
        {node.workflow_type}
      </div>



      {/* ================================= */}
      {/* ROLE */}
      {/* ================================= */}

      {node.actor_role && (

        <div
          style={{
            fontSize: "10px",
            marginTop: "4px",
          }}
        >
          Role: {node.actor_role}
        </div>
      )}



      {/* ================================= */}
      {/* ISA88 */}
      {/* ================================= */}

      {node.isa88_level && (

        <div
          style={{
            marginTop: "5px",
            fontSize: "10px",
            color: "#dbeafe",
          }}
        >
          ISA88: {node.isa88_level}
        </div>
      )}



      {/* ================================= */}
      {/* GXP */}
      {/* ================================= */}

      {node.gxp_critical && (

        <div
          style={{
            marginTop: "7px",
            background: "#991b1b",
            padding: "4px 6px",
            borderRadius: "6px",
            fontSize: "9px",
            fontWeight: "bold",
          }}
        >
          GXP CRITICAL
        </div>
      )}



      {/* ================================= */}
      {/* RETRY LIMIT */}
      {/* ================================= */}

      {node.retryable && (

        <div
          style={{
            marginTop: "5px",
            fontSize: "9px",
            color: "#bfdbfe",
          }}
        >
          Retry Limit: {node.retry_limit}
        </div>
      )}



      {/* ================================= */}
      {/* RETRY INPUT HANDLE */}
      {/* ================================= */}

      {node.workflow_type === "SYSTEM_SCAN" && (

        <Handle
          type="target"
          position={Position.Right}
          id="retryIn"
          style={{
            background: "#2563eb",
            width: 10,
            height: 10,
          }}
        />
      )}



      {/* ================================= */}
      {/* RETRY OUTPUT HANDLE */}
      {/* ================================= */}

      {node.retryable && (

        <Handle
          type="source"
          position={Position.Right}
          id="retryOut"
          style={{
            background: "#2563eb",
            width: 10,
            height: 10,
          }}
        />
      )}

    </div>
  );
}