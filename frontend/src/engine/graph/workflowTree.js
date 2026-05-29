export function buildWorkflowTree(data) {

  const nodeMap = {};

  const outgoing = {};



  // =====================================
  // NODE MAP
  // =====================================

  data.nodes.forEach((node) => {

    nodeMap[node.id] = {

      ...node,

      children: [],
    };
  });



  // =====================================
  // OUTGOING EDGE MAP
  // =====================================

  data.edges.forEach((edge) => {

    if (!outgoing[edge.source]) {

      outgoing[edge.source] = [];
    }



    outgoing[edge.source].push(edge);
  });



  // =====================================
  // FIND START NODE
  // =====================================

  const startNode = data.nodes.find(

    (n) => n.workflow_type === "START"
  );



  if (!startNode) {

    return null;
  }



  // =====================================
  // BUILD TREE
  // =====================================

  return buildNodeTree(

    startNode.id,

    nodeMap,

    outgoing,

    new Set()
  );
}



// =======================================
// RECURSIVE TREE BUILDER
// =======================================

function buildNodeTree(

  nodeId,

  nodeMap,

  outgoing,

  visited
) {

  // =====================================
  // STOP LOOPS
  // =====================================

  if (visited.has(nodeId)) {

    return null;
  }



  visited.add(nodeId);



  const node = nodeMap[nodeId];



  if (!node) {

    return null;
  }



  const currentNode = {

    ...node,

    children: [],
  };



  const edges = outgoing[nodeId] || [];



  // =====================================
  // DECISION NODE
  // =====================================

  if (

    node.workflow_type === "DECISION"

  ) {

    currentNode.yesBranch = [];

    currentNode.noBranch = [];



    edges.forEach((edge) => {

      // =================================
      // YES BRANCH
      // =================================

      if (

        edge.condition === "YES"

      ) {

        const childTree = buildNodeTree(

          edge.target,

          nodeMap,

          outgoing,

          new Set(visited)
        );



        if (childTree) {

          currentNode.yesBranch.push(
            childTree
          );
        }
      }



      // =================================
      // NO BRANCH
      // =================================

      if (

        edge.condition === "NO"

      ) {

        const childTree = buildNodeTree(

          edge.target,

          nodeMap,

          outgoing,

          new Set(visited)
        );



        if (childTree) {

          currentNode.noBranch.push(
            childTree
          );
        }
      }
    });



    return currentNode;
  }



  // =====================================
  // NORMAL FLOW
  // =====================================

  edges.forEach((edge) => {

    // ===================================
    // SKIP RETRY LOOP
    // ===================================

    if (

      edge.condition === "RETRY"

    ) {

      return;
    }



    const childTree = buildNodeTree(

      edge.target,

      nodeMap,

      outgoing,

      new Set(visited)
    );



    if (childTree) {

      currentNode.children.push(
        childTree
      );
    }
  });



  return currentNode;
}