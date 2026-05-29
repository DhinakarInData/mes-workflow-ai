export default function SystemActionNode({ data }) {

  return (

    <div
      style={{
        width: "220px",
        background: "#2563EB",
        color: "white",
        borderRadius: "18px",
        border: "2px solid #1D4ED8",
        overflow: "hidden"
      }}
    >

      <div
        style={{
          padding: "6px",
          fontSize: "12px",
          background: "#1D4ED8",
          textAlign: "center",
          fontWeight: "bold"
        }}
      >
        {data.step_number}
      </div>

      <div
        style={{
          padding: "8px",
          textAlign: "center",
          fontSize: "11px"
        }}
      >
        SYSTEM ACTION
      </div>

      <div
        style={{
          padding: "12px",
          textAlign: "center",
          fontWeight: "bold",
          fontSize: "13px"
        }}
      >
        {data.label}
      </div>

    </div>
  );
}