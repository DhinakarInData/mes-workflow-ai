export default function SwimlaneBackground() {

  const lanes = [

    {
      label: "OPERATOR",
      left: 0,
      width: 300,
      background: "#F9FAFB"
    },

    {
      label: "MES",
      left: 300,
      width: 300,
      background: "#ECFEFF"
    },

    {
      label: "SYSTEM",
      left: 600,
      width: 300,
      background: "#F0FDF4"
    },

    {
      label: "SUPERVISOR",
      left: 900,
      width: 300,
      background: "#FEFCE8"
    },

    {
      label: "QA",
      left: 1200,
      width: 300,
      background: "#FEF2F2"
    }
  ];


  return (

    <div
      style={{
        position: "absolute",
        width: "100%",
        height: "100%",
        top: 0,
        left: 0,
        zIndex: 0,
        pointerEvents: "none"
      }}
    >

      {lanes.map((lane) => (

        <div
          key={lane.label}
          style={{
            position: "absolute",
            left: lane.left,
            top: 0,
            width: lane.width,
            height: "100%",
            background: lane.background,
            borderRight: "1px solid #D1D5DB"
          }}
        >

          <div
            style={{
              position: "sticky",
              top: 0,
              background: "#111827",
              color: "white",
              textAlign: "center",
              padding: "12px",
              fontWeight: "bold",
              fontSize: "14px",
              letterSpacing: "1px"
            }}
          >
            {lane.label}
          </div>

        </div>

      ))}

    </div>
  );
}