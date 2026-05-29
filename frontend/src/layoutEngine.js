import {

  buildWorkflowTree

} from "./engine/graph/workflowTree";



import {

  assignLanes

} from "./engine/layout/laneManager";



import {

  assignLayers

} from "./engine/layout/layerAssigner";



import {

  generateGraphLayout

} from "./engine/layout/graphLayout";



// ======================================
// GENERATE LAYOUT
// ======================================

export function generateLayout(data) {

  // ====================================
  // BUILD TREE
  // ====================================

  const workflowTree =

    buildWorkflowTree(data);



  if (!workflowTree) {

    return {};
  }



  console.log(

    "WORKFLOW TREE:",

    workflowTree
  );



  // ====================================
  // ASSIGN LANES
  // ====================================

  const laneMap =

    assignLanes(workflowTree);



  console.log(

    "LANE MAP:",

    laneMap
  );



  // ====================================
  // ASSIGN LAYERS
  // ====================================

  const layerMap =

    assignLayers(workflowTree);



  console.log(

    "LAYER MAP:",

    layerMap
  );



  // ====================================
  // GENERATE COORDINATES
  // ====================================

  const positions =

    generateGraphLayout(

      workflowTree,

      laneMap,

      layerMap
    );



  console.log(

    "FINAL POSITIONS:",

    positions
  );



  return positions;
}