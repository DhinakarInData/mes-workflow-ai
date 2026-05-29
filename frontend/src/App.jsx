import { useEffect, useState } from "react";

import ReactFlow, {
  Background,
  Controls,
  
} from "reactflow";
import StartNode from "./nodes/StartNode";
import EndNode from "./nodes/EndNode";
import ManualActivityNode from "./nodes/ManualActivityNode";
import DecisionNode from "./nodes/DecisionNode";
import ErrorNode from "./nodes/ErrorNode";
import "reactflow/dist/style.css";

const nodeTypes = {

  start: StartNode,
  error: ErrorNode,

  end: EndNode,

  manual_activity: ManualActivityNode,
  decision: DecisionNode
};

function App() {

  const [nodes, setNodes] = useState([]);

  const [edges, setEdges] = useState([]);



  useEffect(() => {

    fetch("/graph.json")

      .then((response) => response.json())

      .then((data) => {

        console.log(data);

        setNodes(data.nodes);

        setEdges(data.edges);
      });

  }, []);



  return (

    <div
      style={{
        width: "100vw",
        height: "100vh"
      }}
    >

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
      >

        <Background />

        <Controls />

      </ReactFlow>

    </div>
  );
}

export default App;