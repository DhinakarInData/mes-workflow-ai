import { useMemo, useState } from "react";
import ReactFlow from "reactflow";
import { Background, BackgroundVariant, Controls } from "reactflow";
import "reactflow/dist/style.css";
import "./WorkflowStudio.css";

import sampleWorkflow from "./data/test_graph.json";

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

const MAX_WORKFLOW_TEXT_LENGTH = 20000;
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || ""
).replace(/\/$/, "");

export default function App() {
  const [workflow, setWorkflow] = useState(sampleWorkflow);
  const [workflowText, setWorkflowText] = useState("");
  const [workflowTitle, setWorkflowTitle] = useState("Sample workflow");
  const [isGenerating, setIsGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [statusMessage, setStatusMessage] = useState(
    "An example diagram is loaded. Describe a process to generate your own."
  );
  const [graphRevision, setGraphRevision] = useState(0);

  const errorActivityTargets = useMemo(() => {
    const nodesById = new Map(
      workflow.nodes.map((node) => [node.id, node])
    );

    return new Set(
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
  }, [workflow]);

  const nodes = useMemo(
    () => workflow.nodes.map((node) => {
      if (node.type !== "system_activity") {
        return node;
      }

      return {
        ...node,
        data: {
          ...node.data,
          is_error_activity: (
            node.data?.is_error_activity
            || node.data?.group === "ERROR_HANDLING"
            || errorActivityTargets.has(node.id)
          )
        }
      };
    }),
    [errorActivityTargets, workflow]
  );

  async function handleGenerate(event) {
    event.preventDefault();
    const submittedText = workflowText.trim();

    if (!submittedText) {
      setErrorMessage("Describe the workflow before generating a diagram.");
      setStatusMessage("");
      return;
    }

    setIsGenerating(true);
    setErrorMessage("");
    setStatusMessage("");

    try {
      const response = await fetch(
        `${API_BASE_URL}/workflow/generate`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            workflow_text: submittedText
          })
        }
      );
      const result = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          typeof result?.detail === "string"
            ? result.detail
            : `Generation failed with status ${response.status}.`
        );
      }

      if (
        !Array.isArray(result?.nodes)
        || !Array.isArray(result?.edges)
      ) {
        throw new Error("The workflow API returned an invalid diagram.");
      }

      setWorkflow(result);
      setWorkflowTitle("Generated workflow");
      setGraphRevision((revision) => revision + 1);
      setStatusMessage("Your workflow diagram is ready.");
    } catch (requestError) {
      setErrorMessage(
        requestError instanceof TypeError
          ? "Could not reach the workflow API. Check that the backend is running."
          : requestError.message || "Workflow generation failed."
      );
    } finally {
      setIsGenerating(false);
    }
  }

  function handleRestoreSample() {
    setWorkflow(sampleWorkflow);
    setWorkflowText("");
    setWorkflowTitle("Sample workflow");
    setErrorMessage("");
    setStatusMessage("The example diagram has been restored.");
    setGraphRevision((revision) => revision + 1);
  }

  return (
    <main className="workflow-app">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">M</div>
          <div>
            <p className="brand-kicker">MES · FDS</p>
            <h1>Workflow Studio</h1>
          </div>
        </div>
        <div className="topbar-note">
          <span className="topbar-indicator" aria-hidden="true" />
          Natural language to workflow diagram
        </div>
      </header>

      <div className="workspace">
        <aside className="composer-panel" aria-label="Workflow generator">
          <div className="panel-intro">
            <span className="section-kicker">DESCRIBE</span>
            <h2>Build a workflow</h2>
            <p>
              Write the process in plain language. Include checks, outcomes,
              and any retry steps.
            </p>
          </div>

          <form className="workflow-form" onSubmit={handleGenerate}>
            <label htmlFor="workflow-description">
              Process description
            </label>
            <textarea
              id="workflow-description"
              value={workflowText}
              onChange={(event) => setWorkflowText(event.target.value)}
              placeholder={"Example:\nScan the equipment.\nIf valid, continue to line clearance.\nIf invalid, show an error and return to scanning."}
              maxLength={MAX_WORKFLOW_TEXT_LENGTH}
              rows={10}
              disabled={isGenerating}
            />
            <div className="field-meta">
              <span>One step per line works well.</span>
              <span>{workflowText.length.toLocaleString()} / 20,000</span>
            </div>

            <button
              className="primary-button"
              type="submit"
              disabled={!workflowText.trim() || isGenerating}
            >
              {isGenerating ? (
                <>
                  <span className="button-spinner" aria-hidden="true" />
                  Generating diagram…
                </>
              ) : (
                <>
                  <span className="button-spark" aria-hidden="true">✦</span>
                  Generate diagram
                </>
              )}
            </button>
            <button
              className="secondary-button"
              type="button"
              onClick={handleRestoreSample}
              disabled={isGenerating}
            >
              Restore sample diagram
            </button>
          </form>

          <div className="message-stack" aria-live="polite">
            {errorMessage && (
              <div className="message-card error-message" role="alert">
                <strong>Couldn’t generate the diagram</strong>
                <span>{errorMessage}</span>
              </div>
            )}
            {statusMessage && (
              <div className="message-card status-message" role="status">
                <span className="status-check" aria-hidden="true">✓</span>
                <span>{statusMessage}</span>
              </div>
            )}
          </div>

          <div className="description-tips">
            <span className="section-kicker">GOOD DESCRIPTIONS INCLUDE</span>
            <ul>
              <li>Operator and system activities</li>
              <li>Decision outcomes such as valid or invalid</li>
              <li>Error, retry, and return paths</li>
            </ul>
          </div>
        </aside>

        <section className="canvas-panel" aria-label="Workflow diagram">
          <div className="canvas-toolbar">
            <div>
              <span className="section-kicker">WORKFLOW CANVAS</span>
              <h2>{workflowTitle}</h2>
            </div>
            <div className="canvas-summary">
              <span className="canvas-status">
                <span className="canvas-status-dot" aria-hidden="true" />
                {workflowTitle === "Sample workflow" ? "Example" : "Generated"}
              </span>
              <span>{workflow.nodes.length} nodes</span>
              <span className="summary-divider" aria-hidden="true" />
              <span>{workflow.edges.length} flows</span>
            </div>
          </div>

          <div className="canvas-body">
            <ReactFlow
              key={graphRevision}
              nodes={nodes}
              edges={workflow.edges}
              nodeTypes={nodeTypes}
              edgeTypes={edgeTypes}
              fitView
              fitViewOptions={{ padding: 0.16 }}
              minZoom={0.12}
              maxZoom={1.35}
              nodeOrigin={[0.5, 0.5]}
            >
              <Background
                variant={BackgroundVariant.Dots}
                gap={22}
                size={1}
                color="#cad5d8"
              />
              <Controls position="bottom-left" />
            </ReactFlow>
          </div>

          <div className="canvas-footer">
            <span>Drag to pan · Scroll to zoom</span>
            <span>React Flow canvas</span>
          </div>
        </section>
      </div>
    </main>
  );
}
