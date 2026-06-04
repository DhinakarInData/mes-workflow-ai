// ===================================
// GET LAYOUTED ELEMENTS
// ===================================

export function getLayoutedElements(nodes, edges) {

  // ===================================
  // LAYOUT NODES
  // ===================================

  const layoutedNodes = nodes.map((node) => ({

    ...node,

    sourcePosition: "bottom",

    targetPosition: "top"
  }));


  // ===================================
  // LAYOUT EDGES
  // ===================================

  const layoutedEdges = edges.map((edge) => {

    // ===================================
    // DEFAULT HANDLES
    // ===================================

    let sourceHandle = "bottom";

    let targetHandle = "top";


    // ===================================
    // YES FLOW
    // ===================================

    if (
      edge.condition === "YES"
    ) {

      sourceHandle = "yes";
    }


    // ===================================
    // NO FLOW
    // ===================================

    if (
      edge.condition === "NO"
    ) {

      sourceHandle = "no";
    }


    // ===================================
    // LOOPBACK FLOW
    // ===================================

    if (
      edge.edge_type === "LOOPBACK"
    ) {

      sourceHandle = "loop";
    }


    // ===================================
    // EDGE COLORS
    // ===================================

    let strokeColor = "#6B7280";

    let animated = false;


    // ===================================
    // YES FLOW
    // ===================================

    if (
      edge.condition === "YES"
    ) {

      strokeColor = "#16A34A";
    }


    // ===================================
    // NO FLOW
    // ===================================

    if (
      edge.condition === "NO"
    ) {

      strokeColor = "#DC2626";
    }


    // ===================================
    // LOOPBACK FLOW
    // ===================================

    if (
      edge.edge_type === "LOOPBACK"
    ) {

      strokeColor = "#2563EB";

      animated = true;
    }


    // ===================================
    // ERROR FLOW
    // ===================================

    if (
      edge.edge_type === "ERROR_FLOW"
    ) {

      strokeColor = "#DC2626";

      animated = true;
    }


    // ===================================
    // RETURN EDGE
    // ===================================

    return {

      ...edge,

      type: "semantic",

      animated,

      sourceHandle,

      targetHandle,

      style: {

        stroke: strokeColor,

        strokeWidth: 2
      },

      labelStyle: {

        fill: strokeColor,

        fontWeight: 700,

        fontSize: 12
      }
    };
  });


  // ===================================
  // RETURN GRAPH
  // ===================================

  return {

    nodes: layoutedNodes,

    edges: layoutedEdges
  };
}