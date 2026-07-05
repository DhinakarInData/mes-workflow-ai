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
import ConnectorNode from "./nodes/ConnectorNode";

const nodeTypes = {
  start: StartNode,
  end: EndNode,
  decision: DecisionNode,
  system_check: SystemCheckNode,
  manual_activity: ManualActivityNode,
  system_activity: SystemActivityNode,
  response: ResponseNode,
  merge: MergeNode,
  connector: ConnectorNode
};

const edgeTypes = {
  semantic: (props) => {
    return <CustomOrthogonalEdge {...props} />;
  }
};
export default function App() {
  const nodesById = new Map(
    workflow.nodes.map((node) => [
      node.id,
      node
    ])
  );

  const errorActivityTargets = new Set(
    workflow.edges
      .filter((edge) => {
        if (edge?.data?.routing_role !== "ERROR") {
          return false;
        }

        const sourceNode = nodesById.get(edge.source);
        const targetNode = nodesById.get(edge.target);

        if (
          !sourceNode
          || !targetNode
          || targetNode.type !== "system_activity"
        ) {
          return false;
        }

        return (
          targetNode?.data?.group === "ERROR_HANDLING"
          || targetNode.position.x > sourceNode.position.x + 80
        );
      })
      .map((edge) => edge.target)
  );

  const nodes = workflow.nodes.map((node) => {
    if (node.type !== "system_activity") {
      return node;
    }

    return {
      ...node,
      data: {
        ...node.data,
        is_error_activity: (
          node.data?.is_error_activity
          ||
          node.data?.group === "ERROR_HANDLING"
          || errorActivityTargets.has(node.id)
        )
      }
    };
  });
  
  return (
    <div style={{ width: "100vw", height: "100vh" }}>
      
      <ReactFlow

        nodes={nodes}
        edges={workflow.edges}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{
          padding: 0.16
        }}
        minZoom={0.12}
        maxZoom={1.35}
        nodeOrigin={[0.5, 0.5]}
      />
    </div>
  );
}
