function WorkflowGroup({

  title,

  x,

  y,

  width,

  height
}) {

  return (

    <div

      style={{

        position: "absolute",

        left: x,

        top: y,

        width: width,

        height: height,

        backgroundColor: "#F3F4F6",

        border: "2px solid #D1D5DB",

        borderRadius: "16px",

        padding: "20px",

        zIndex: 0
      }}
    >

      <div

        style={{

          fontSize: "18px",

          fontWeight: "bold",

          marginBottom: "12px",

          color: "#374151"
        }}
      >

        {title}

      </div>

    </div>
  );
}


export default WorkflowGroup;