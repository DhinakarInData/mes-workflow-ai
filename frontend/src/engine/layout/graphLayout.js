import { SPACING } from "./spacingRules";



// ======================================
// LANE POSITIONS
// ======================================

const laneX = {

  MAIN:
    SPACING.MAIN_LANE_X,

  LEFT:
    SPACING.LEFT_LANE_X,

  RIGHT:
    SPACING.RIGHT_LANE_X,
};



// ======================================
// GENERATE GRAPH LAYOUT
// ======================================

export function generateGraphLayout(

  workflowTree,

  laneMap,

  layerMap
) {

  const positions = {};



  traverseGraph(

    workflowTree,

    positions,

    laneMap,

    layerMap
  );



  return positions;
}



// ======================================
// RECURSIVE GRAPH TRAVERSAL
// ======================================

function traverseGraph(

  node,

  positions,

  laneMap,

  layerMap
) {

  if (!node) {

    return;
  }



  // ====================================
  // SKIP EXISTING
  // ====================================

  if (positions[node.id]) {

    return;
  }



  // ====================================
  // GET NODE LANE
  // ====================================

  const lane =
    laneMap[node.id] || "MAIN";



  // ====================================
  // GET NODE LEVEL
  // ====================================

  const level =
    layerMap[node.id] || 0;



  // ====================================
  // CALCULATE X POSITION
  // ====================================

  let xPos =
    laneX[lane];



  // ====================================
  // FORCE MAIN EXECUTION SPINE
  // ====================================

  if (

    lane === "MAIN"

  ) {

    xPos =
      SPACING.MAIN_LANE_X;
  }



  // ====================================
  // LEFT BRANCH OFFSET
  // ====================================

  if (

    lane === "LEFT"

  ) {

    xPos =
      SPACING.LEFT_LANE_X;
  }



  // ====================================
  // RIGHT / RETRY OFFSET
  // ====================================

  if (

    lane === "RIGHT"

  ) {

    // ================================
    // MULTI-RETRY SEPARATION
    // ================================

    const retryOffset =

      level > 12

        ? 320

        : 240;



    xPos =
      SPACING.RIGHT_LANE_X +
      retryOffset;
  }



  // ====================================
  // CALCULATE Y POSITION
  // ====================================

  let yPos =
    120 +
    level *
      SPACING.Y_SPACING;



  // ====================================
  // DECISION NODE EXTRA SPACING
  // ====================================

  if (

    node.workflow_type ===
    "DECISION"

  ) {

    yPos += 20;
  }



  // ====================================
  // RETRY NODE BALANCING
  // ====================================

  const isRetryNode =

    node.label
      ?.toLowerCase()
      .includes("retry");



  if (isRetryNode) {

    yPos += 30;
  }



  // ====================================
  // POSITION NODE
  // ====================================

  positions[node.id] = {

    x: xPos,

    y: yPos,
  };



  // ====================================
  // YES BRANCH
  // ====================================

  node.yesBranch?.forEach(

    (child) => {

      traverseGraph(

        child,

        positions,

        laneMap,

        layerMap
      );
    }
  );



  // ====================================
  // NO BRANCH
  // ====================================

  node.noBranch?.forEach(

    (child) => {

      traverseGraph(

        child,

        positions,

        laneMap,

        layerMap
      );
    }
  );



  // ====================================
  // NORMAL CHILDREN
  // ====================================

  node.children?.forEach(

    (child) => {

      traverseGraph(

        child,

        positions,

        laneMap,

        layerMap
      );
    }
  );
}