import ReactFlow from "reactflow";
import "reactflow/dist/style.css";

import workflow from "./data/test_graph.json";

import StartNode from "./nodes/StartNode";
import EndNode from "./nodes/EndNode";
import DecisionNode from "./nodes/DecisionNode";
import SystemCheckNode from "./nodes/SystemCheckNode";
import ManualActivityNode from "./nodes/ManualActivityNode";
import SystemActivityNode from "./nodes/SystemActivityNode";
import CustomOrthogonalEdge from "./edges/CustomOrthogonalEdge";
import ResponseNode from "./nodes/ResponseNode";
import MergeNode from "./nodes/MergeNode";

const nodeTypes = {
  start: StartNode,
  end: EndNode,
  decision: DecisionNode,
  system_check: SystemCheckNode,
  manual_activity: ManualActivityNode,
  system_activity: SystemActivityNode,
  response: ResponseNode,
  merge: MergeNode
};

const edgeTypes = {
  semantic: (props) => {
    console.log("CUSTOM EDGE WORKING", props);
    return <CustomOrthogonalEdge {...props} />;
  }
};
export default function App() {
  console.log("APP LOADED");

  console.log("TOTAL EDGES =", workflow.edges.length);

  console.log("ALL EDGES =", workflow.edges);
  
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      
      <ReactFlow

        nodes={workflow.nodes}
        edges={workflow.edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        nodeOrigin={[0.5, 0.5]}
      />
    </div>
  );
}