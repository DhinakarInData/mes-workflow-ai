import { useEffect, useState } from "react";

import ReactFlow from "reactflow";

import "reactflow/dist/style.css";
import ConnectorNode from "./nodes/ConnectorNode";
import SystemActivityNode from "./nodes/SystemActivityNode";
import DecisionNode from "./nodes/DecisionNode";
import ErrorNode from "./nodes/ErrorNode";
import ManualActivityNode from "./nodes/ManualActivityNode";
import SwimlaneBackground from "./components/SwimlaneBackground";

function App() {

  const [nodes, setNodes] = useState([]);

  const [edges, setEdges] = useState([]);
  const nodeTypes = {

  connector: ConnectorNode,

  decision: DecisionNode,

  error: ErrorNode,

  manual_activity: ManualActivityNode,

  system_activity: SystemActivityNode
}

  useEffect(() => {

    fetch("http://127.0.0.1:8000/workflow")

      .then((response) => response.json())

      .then((data) => {

        setNodes(data.nodes);

        setEdges(data.edges);
      });

  }, []);


  return (

    <div
      style={{
        width: "100vw",
        height: "100vh",
        position: "relative"
      }}
    >
   

      <ReactFlow
  nodes={nodes}
  edges={edges}
  nodeTypes={nodeTypes}
  defaultViewport={{
    x: 100,
    y: 50,
    zoom: 1
  }}
>

  <SwimlaneBackground />

</ReactFlow>

    </div>
  );
}


export default App;