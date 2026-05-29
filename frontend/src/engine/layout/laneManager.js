export function assignLanes(workflowTree) {

  const laneMap = {};



  traverseTree(

    workflowTree,

    "MAIN",

    laneMap
  );



  return laneMap;
}



// ======================================
// RECURSIVE LANE TRAVERSAL
// ======================================

function traverseTree(

  node,

  lane,

  laneMap
) {

  if (!node) {

    return;
  }



  // ====================================
  // ASSIGN CURRENT NODE
  // ====================================

  laneMap[node.id] = lane;



  // ====================================
  // DECISION NODE
  // ====================================

  if (

    node.workflow_type ===
    "DECISION"

  ) {

    // ================================
    // YES BRANCH
    // ================================

    node.yesBranch?.forEach(

      (child) => {

        traverseTree(

          child,

          "LEFT",

          laneMap
        );
      }
    );



    // ================================
    // NO / RETRY BRANCH
    // ================================

    node.noBranch?.forEach(

      (child) => {

        const isRetry =

          child.label
            ?.toLowerCase()
            .includes("retry");



        traverseTree(

          child,

          isRetry

            ? "RIGHT"

            : "LEFT",

          laneMap
        );
      }
    );



    return;
  }



  // ====================================
  // NORMAL FLOW
  // ====================================

  node.children?.forEach(

  (child) => {

    const nextLane =

      node.workflow_type ===
      "DECISION"

        ? "MAIN"

        : lane;



    traverseTree(

      child,

      nextLane,

      laneMap
    );
  }
);
}