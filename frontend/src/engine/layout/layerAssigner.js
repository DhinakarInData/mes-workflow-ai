export function assignLayers(workflowTree) {

  const layerMap = {};



  traverseLayers(

    workflowTree,

    0,

    layerMap
  );



  return layerMap;
}



// ======================================
// RECURSIVE LAYER TRAVERSAL
// ======================================

function traverseLayers(

  node,

  level,

  layerMap
) {

  if (!node) {

    return level;
  }



  // ====================================
  // PREVENT REASSIGNMENT
  // ====================================

  if (

    layerMap[node.id] !== undefined

  ) {

    return level;
  }



  // ====================================
  // ASSIGN CURRENT LEVEL
  // ====================================

  layerMap[node.id] = level;



  let nextLevel =
    level + 1;



  // ====================================
  // DECISION NODE
  // ====================================

  if (

    node.workflow_type ===
    "DECISION"

  ) {

    let maxBranchDepth =
      nextLevel;



    // ================================
    // YES BRANCH
    // ================================

    node.yesBranch?.forEach(

      (child) => {

        const depth =
          traverseLayers(

            child,

            nextLevel,

            layerMap
          );



        maxBranchDepth =
          Math.max(

            maxBranchDepth,

            depth
          );
      }
    );



    // ================================
    // NO BRANCH
    // ================================

    node.noBranch?.forEach(

      (child) => {

        const depth =
          traverseLayers(

            child,

            nextLevel,

            layerMap
          );



        maxBranchDepth =
          Math.max(

            maxBranchDepth,

            depth
          );
      }
    );



    // ================================
    // CONTINUE FLOW
    // ================================

    node.children?.forEach(

      (child) => {

        traverseLayers(

          child,

          maxBranchDepth + 1,

          layerMap
        );
      }
    );



    return maxBranchDepth + 1;
  }



  // ====================================
  // NORMAL FLOW
  // ====================================

  let deepest =
    nextLevel;



  node.children?.forEach(

    (child) => {

      const depth =
        traverseLayers(

          child,

          nextLevel,

          layerMap
        );



      deepest = Math.max(

        deepest,

        depth
      );
    }
  );



  return deepest;
}