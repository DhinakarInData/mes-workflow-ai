import { useEffect, useState } from "react";

import ReactFlow from "reactflow";

import "reactflow/dist/style.css";
import {

  Background,

  Controls,

  MiniMap
} from "reactflow"


// ===================================
// NODES
// ===================================

import ConnectorNode from "./nodes/ConnectorNode";

import SystemActivityNode from "./nodes/SystemActivityNode";

import DecisionNode from "./nodes/DecisionNode";

import ErrorNode from "./nodes/ErrorNode";

import ManualActivityNode from "./nodes/ManualActivityNode";


// ===================================
// EDGES
// ===================================

import CustomOrthogonalEdge from "./edges/CustomOrthogonalEdge";

// ===================================
// LAYOUT
// ===================================

import {
  getLayoutedElements
} from "./layouts/dagreLayout";


// ===================================
// APP
// ===================================

function App() {

  // ===================================
  // STATE
  // ===================================

  const [nodes, setNodes] = useState([]);

  const [edges, setEdges] = useState([]);


  // ===================================
  // NODE TYPES
  // ===================================

  const nodeTypes = {

    connector: ConnectorNode,

    decision: DecisionNode,

    error: ErrorNode,

    manual_activity: ManualActivityNode,

    system_activity: SystemActivityNode
  };


  // ===================================
  // EDGE TYPES
  // ===================================

  const edgeTypes = {

    semantic: CustomOrthogonalEdge
  };


  // ===================================
  // FETCH WORKFLOW
  // ===================================

 useEffect(() => {

  fetch(
    "http://127.0.0.1:8000/workflow"
  )

    .then(
      (response) => response.json()
    )

    .then((data) => {
      console.log(
  data.nodes.map(n => ({
    id: n.id,
    x: n.position.x,
    y: n.position.y
  }))
);

      console.log(
        "NODES:",
        data.nodes
      );

      console.log(
        "EDGES:",
        data.edges
      );

      setNodes(
        data.nodes
      );

      setEdges(
        data.edges
      );
    });

}, []);


  // ===================================
  // RENDER
  // ===================================

  return (

    <div

      style={{

        width: "100vw",

        height: "100vh",

        background: "#F8FAFC"
      }}
    >

      <ReactFlow

        nodes={nodes}

        edges={edges}

        nodeTypes={nodeTypes}

        edgeTypes={edgeTypes}
        defaultEdgeOptions={{

          type: "custom"
        }}

        fitView

        minZoom={0.3}

        maxZoom={2}

        defaultViewport={{

          x: 250,

          y: 40,

          zoom: 1.0
        }}

        fitViewOptions={{

          padding: 0.2
        }}
        
      />
     
      
      

    </div>
  );
}


export default App;