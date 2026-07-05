import React from "react";

import {
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
  useStore
} from "reactflow";

const GLOBAL_RETURN_BUS_X = 2060;


export default function CustomOrthogonalEdge(props) {

  const {
    id,
    source,
    target,
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
    style = {},
    markerEnd,
    label,
    labelStyle,
    data
  } = props;

  const flowNodes = useStore(
    state => {
      const internalNodes = state.nodeInternals?.values
        ? Array.from(
            state.nodeInternals.values()
          )
        : [];

      return internalNodes.length
        ? internalNodes
        : state.nodes || [];
    }
  );

  const flowEdges = useStore(
    state => state.edges || []
  );

  const laneOffset = Number(data?.lane_offset || 0);

  const normalizedLabel =
    String(label || "")
      .trim()
      .replace(/_/g, " ")
      .toUpperCase();

  const isRestartLabel = [
    "YES",
    "CONTINUE",
    "CONTINUE WITH NEXT EQUIPMENT",
    "CONFIRM NEXT EQUIPMENT",
    "NEXT EQUIPMENT",
    "REQUIRED",
    "REQURIED",
    "APPROVE REWEIGHING",
    "APPROVES REWEIGHING",
    "REWEIGH",
    "REWEIGHING"
  ].includes(normalizedLabel);

  const routingType =
    data?.routing_type === "OUTER_LOOP"
    && data?.source_type === "RESPONSE"
    && isRestartLabel
      ? "RESTART_FLOW"
      : data?.routing_type;

  const labelText =
    String(label || "").replace(/_/g, " ");

  const labelLength =
    labelText.length;

  const shouldWrapOutcomeLabel =
    /\b(NOT|DOES NOT|DOESN'T)\b/.test(
      normalizedLabel
    )
    && labelLength > 8;

  const shouldWrapLabel =
    labelLength > 22
    || shouldWrapOutcomeLabel;

  const labelLineCount =
    Math.max(
      1,
      Math.ceil(labelText.length / 18)
    );

  const labelGap =
    labelText
      ? Math.min(
          Math.max(
            Math.min(labelText.length, 18) * 6 + 22,
            44
          ),
          96
        )
      : 0;

  const branchInlineGap =
    labelText
      ? Math.min(
          Math.max(
            Math.min(labelLength, 22) * 5.4 + 20,
            48
          ),
          136
        )
      : 0;

  const verticalLabelGap =
    labelText
      ? Math.min(
          Math.max(
            labelLineCount * 12 + 8,
            24
          ),
          48
        )
      : 0;

  const estimateBranchLabelWidth = () => {
    if (!labelText) {
      return 0;
    }

    if (shouldWrapLabel) {
      return 132;
    }

    return Math.min(
      Math.max(
        labelText.length * 5.8 + 12,
        42
      ),
      132
    );
  };

  const estimateLabelBox = () => {
    const width = Math.max(
      estimateBranchLabelWidth(),
      Math.min(
        Math.max(
          labelText.length * 5.8 + 12,
          42
        ),
        shouldWrapLabel ? 132 : 160
      )
    );

    const height = Math.max(
      labelLineCount * 12 + 6,
      16
    );

    return {
      width,
      height
    };
  };

  const getNodeMetrics = nodeId => {
    const node = flowNodes.find(
      candidate => candidate.id === nodeId
    );

    if (!node) {
      return null;
    }

    const position =
      node.positionAbsolute ||
      node.__rf?.position ||
      node.internals?.positionAbsolute ||
      node.position ||
      {};

    const width =
      node.measured?.width ||
      node.__rf?.width ||
      node.width ||
      node.data?.width ||
      160;

    const height =
      node.measured?.height ||
      node.__rf?.height ||
      node.height ||
      node.data?.height ||
      80;

    return {
      x: position.x,
      y: position.y,
      width,
      height
    };
  };

  const nodeBounds = flowNodes
    .filter(node => node.id !== source && node.id !== target)
    .map(node => {
      const position =
        node.positionAbsolute ||
        node.__rf?.position ||
        node.internals?.positionAbsolute ||
        node.position ||
        {};

      const width =
        node.measured?.width ||
        node.__rf?.width ||
        node.width ||
        node.data?.width ||
        160;

      const height =
        node.measured?.height ||
        node.__rf?.height ||
        node.height ||
        node.data?.height ||
        80;

      return {
        left: position.x - (width / 2) - 16,
        right: position.x + (width / 2) + 16,
        top: position.y - (height / 2) - 12,
        bottom: position.y + (height / 2) + 12
      };
    });

  const overlapArea = (first, second) => {
    const overlapWidth = Math.max(
      0,
      Math.min(first.right, second.right) - Math.max(first.left, second.left)
    );

    const overlapHeight = Math.max(
      0,
      Math.min(first.bottom, second.bottom) - Math.max(first.top, second.top)
    );

    return overlapWidth * overlapHeight;
  };

  const stabilizeLabelPosition = (baseX, baseY, options = {}) => {
    if (!labelText || !nodeBounds.length) {
      return {
        x: baseX,
        y: baseY
      };
    }

    const labelBox = estimateLabelBox();

    const candidateOffsets =
      options.offsets || [
        [0, 0],
        [0, -22],
        [0, 22],
        [28, 0],
        [-28, 0],
        [28, -18],
        [-28, -18],
        [28, 18],
        [-28, 18]
      ];

    const candidates = candidateOffsets.map(([offsetX, offsetY], index) => {
      const box = {
        left: baseX + offsetX - (labelBox.width / 2),
        right: baseX + offsetX + (labelBox.width / 2),
        top: baseY + offsetY - (labelBox.height / 2),
        bottom: baseY + offsetY + (labelBox.height / 2)
      };

      const collisionScore = nodeBounds.reduce(
        (score, bounds) => score + overlapArea(box, bounds),
        0
      );

      const movementPenalty =
        (Math.abs(offsetX) + Math.abs(offsetY)) * 0.08;

      return {
        x: baseX + offsetX,
        y: baseY + offsetY,
        score: collisionScore + movementPenalty,
        index
      };
    });

    const bestCandidate = candidates.sort(
      (first, second) =>
        first.score - second.score ||
        first.index - second.index
    )[0];

    return {
      x: bestCandidate.x,
      y: bestCandidate.y
    };
  };

  const clearVerticalLaneX = (
    baseLaneX,
    direction,
    startY,
    endY,
    limitX
  ) => {
    const laneTop = Math.min(
      startY,
      endY
    );

    const laneBottom = Math.max(
      startY,
      endY
    );

    const clearance =
      28;

    let laneX =
      baseLaneX;

    nodeBounds.forEach(bounds => {
      const verticalOverlap =
        !(laneBottom < bounds.top || laneTop > bounds.bottom);

      if (!verticalOverlap) {
        return;
      }

      const crossesBounds =
        laneX >= bounds.left && laneX <= bounds.right;

      if (!crossesBounds) {
        return;
      }

      laneX = direction > 0
        ? bounds.right + clearance
        : bounds.left - clearance;
    });

    if (direction > 0) {
      return Math.min(
        laneX,
        limitX - 24
      );
    }

    return Math.max(
      laneX,
      limitX + 24
    );
  };

  const verticalLaneCollisionCount = (
    laneX,
    startY,
    endY
  ) => {
    const laneTop = Math.min(
      startY,
      endY
    );

    const laneBottom = Math.max(
      startY,
      endY
    );

    return nodeBounds.filter(bounds => {
      const crossesX =
        laneX >= bounds.left && laneX <= bounds.right;

      const overlapsY =
        !(laneBottom < bounds.top || laneTop > bounds.bottom);

      return crossesX && overlapsY;
    }).length;
  };

  const segmentIntersectsBounds = (
    startX,
    startY,
    endX,
    endY,
    bounds
  ) => {
    if (Math.abs(startX - endX) < 1) {
      const x = startX;

      if (x < bounds.left || x > bounds.right) {
        return false;
      }

      const segmentTop = Math.min(startY, endY);
      const segmentBottom = Math.max(startY, endY);

      return !(
        segmentBottom < bounds.top ||
        segmentTop > bounds.bottom
      );
    }

    if (Math.abs(startY - endY) < 1) {
      const y = startY;

      if (y < bounds.top || y > bounds.bottom) {
        return false;
      }

      const segmentLeft = Math.min(startX, endX);
      const segmentRight = Math.max(startX, endX);

      return !(
        segmentRight < bounds.left ||
        segmentLeft > bounds.right
      );
    }

    return false;
  };

  const orthogonalRouteCollisionScore = (
    laneX,
    routeSourceX,
    routeSourceY,
    routeTargetX,
    routeTargetY
  ) => {
    const segments = [
      [
        routeSourceX,
        routeSourceY,
        laneX,
        routeSourceY
      ],
      [
        laneX,
        routeSourceY,
        laneX,
        routeTargetY
      ],
      [
        laneX,
        routeTargetY,
        routeTargetX,
        routeTargetY
      ]
    ];

    return nodeBounds.reduce((score, bounds) => {
      const hits = segments.filter(segment =>
        segmentIntersectsBounds(
          segment[0],
          segment[1],
          segment[2],
          segment[3],
          bounds
        )
      ).length;

      return score + (hits * 1_000);
    }, 0);
  };

  const clearRestartLaneX = (
    baseLaneX,
    direction,
    startY,
    endY,
    options = {}
  ) => {
    const laneStep =
      92;

    let bestLaneX =
      baseLaneX;

    let bestCollisionCount =
      Number.POSITIVE_INFINITY;

    let bestScore =
      Number.POSITIVE_INFINITY;

    const sideLimitX =
      options.sideLimitX;

    const routeSourceX =
      options.sourceX ?? sourceX;

    const routeTargetX =
      options.targetX ?? targetX;

    const routeSourceY =
      options.sourceY ?? startY;

    const routeTargetY =
      options.targetY ?? endY;

    const isAllowedForSide = candidateX => {
      if (!Number.isFinite(sideLimitX)) {
        return true;
      }

      return direction > 0
        ? candidateX >= sideLimitX + 72
        : candidateX <= sideLimitX - 72;
    };

    const candidateOffsets = [
      0
    ];

    for (let attempt = 1; attempt <= 8; attempt += 1) {
      candidateOffsets.push(
        direction * laneStep * attempt,
        -direction * laneStep * attempt
      );
    }

    candidateOffsets.forEach(offset => {
      const candidateX =
        baseLaneX + offset;

      if (!isAllowedForSide(candidateX)) {
        return;
      }

      const collisionCount =
        verticalLaneCollisionCount(
          candidateX,
          startY,
          endY
        );

      const routeCollisionScore =
        orthogonalRouteCollisionScore(
          candidateX,
          routeSourceX,
          routeSourceY,
          routeTargetX,
          routeTargetY
        );

      const distancePenalty =
        Math.abs(candidateX - baseLaneX);

      const widthPenalty =
        Math.abs(candidateX - routeSourceX) * 0.35;

      const score =
        (collisionCount * 10_000)
        + routeCollisionScore
        + distancePenalty
        + widthPenalty;

      if (
        score < bestScore
        || (
          score === bestScore
          && collisionCount < bestCollisionCount
        )
      ) {
        bestCollisionCount = collisionCount;
        bestLaneX = candidateX;
        bestScore = score;
      }
    });

    return bestLaneX;
  };

  let edgePath;
  let labelX;
  let labelY;
  let suppressMarkerEnd = false;

  if (routingType === "CONNECTOR_STUB") {

    const connectorBranchIndex =
      Number(data?.connector_branch_index || 0);

    const connectorBranchCount =
      Number(data?.connector_branch_count || 0);

    const groupedConnector =
      connectorBranchIndex > 0
      && connectorBranchCount > 1
      && data?.connector_segment === "to_reference";

    const branchSpread =
      18;

    const branchYOffset =
      groupedConnector
        ? (
            connectorBranchIndex
            - ((connectorBranchCount + 1) / 2)
          ) * branchSpread
        : 0;

    const branchStartY =
      sourceY + branchYOffset;

    const branchMidX =
      sourceX + Math.max(
        42,
        Math.abs(targetX - sourceX) * 0.34
      );

    const isMostlyHorizontal =
      Math.abs(branchStartY - targetY) < 8;

    const elbowX =
      sourceX + ((targetX - sourceX) * 0.55);

    edgePath = groupedConnector
      ? `
        M ${sourceX} ${sourceY}
        L ${branchMidX} ${sourceY}
        L ${branchMidX} ${branchStartY}
        L ${targetX} ${branchStartY}
        L ${targetX} ${targetY}
      `
      : isMostlyHorizontal
      ? `
        M ${sourceX} ${branchStartY}
        L ${targetX} ${targetY}
      `
      : `
        M ${sourceX} ${branchStartY}
        L ${elbowX} ${branchStartY}
        L ${elbowX} ${targetY}
        L ${targetX} ${targetY}
      `;

    labelX = groupedConnector
      ? branchMidX + ((targetX - branchMidX) * 0.45)
      : sourceX + ((targetX - sourceX) * 0.5);

    labelY = groupedConnector
      ? branchStartY - 11
      : sourceY + ((targetY - sourceY) * 0.5) - 14;

  } else if (routingType === "BUSINESS_BRANCH") {

    const direction =
      targetX >= sourceX ? 1 : -1;

    const targetEntryX =
      targetX - (direction * 18);

    const isLongBypassBranch =
      Math.abs(targetY - sourceY) > 320;

    const preferredBranchLaneX =
      isLongBypassBranch
        ? targetX - (direction * 90)
        : sourceX + (
          direction * Math.min(
            170,
            Math.max(
              104,
              Math.abs(targetEntryX - sourceX) * 0.34
            )
          )
        );

    const branchLaneX =
      isLongBypassBranch
        ? clearRestartLaneX(
          preferredBranchLaneX,
          direction,
          sourceY,
          targetY,
          {
            sideLimitX: sourceX,
            sourceX,
            sourceY,
            targetX,
            targetY
          }
        )
        : clearVerticalLaneX(
          preferredBranchLaneX,
          direction,
          sourceY,
          targetY,
          targetEntryX
        );

    const branchLabelPadding =
      14;

    labelX = isLongBypassBranch
      ? sourceX + ((branchLaneX - sourceX) * 0.48)
      : sourceX + ((branchLaneX - sourceX) * 0.78);

    labelY = isLongBypassBranch
      ? sourceY - 14
      : sourceY + ((targetY - sourceY) * 0.42);

    const verticalGapStartY =
      labelY - (verticalLabelGap / 2) - branchLabelPadding;

    const verticalGapEndY =
      labelY + (verticalLabelGap / 2) + branchLabelPadding;

    const canBreakVerticalLane =
      !isLongBypassBranch
      && Math.abs(targetY - sourceY) > verticalLabelGap + 42;

    const usesTopTargetEntry =
      targetPosition === "top";

    const targetMetrics =
      getNodeMetrics(target);

    const targetNodeWidth =
      Number(data?.target_width || targetMetrics?.width || 160);

    const targetNodeHeight =
      Number(targetMetrics?.height || 80);

    const sideTargetX =
      targetX - (direction * (targetNodeWidth / 2));

    const sideTargetY =
      usesTopTargetEntry
        ? targetY + (targetNodeHeight / 2)
        : targetY;

    const sideApproachLaneX =
      sideTargetX - (direction * 54);

    const desiredSideTargetHandle =
      direction > 0
        ? "loopback"
        : "return";

    const targetSideAlreadyOccupied =
      usesTopTargetEntry
      && flowEdges.some(edge =>
        edge.id !== id
        && edge.target === target
        && edge.targetHandle === desiredSideTargetHandle
      );

    const sideEntryCollisionScore =
      usesTopTargetEntry
        ? orthogonalRouteCollisionScore(
            sideApproachLaneX,
            sourceX,
            sourceY,
            sideTargetX,
            sideTargetY
          )
        : Number.POSITIVE_INFINITY;

    const canUseDirectSideEntry =
      usesTopTargetEntry
      && !targetSideAlreadyOccupied
      && Math.abs(targetX - sourceX) > 80
      && sideEntryCollisionScore === 0;

    const directTopDropCollisionScore =
      usesTopTargetEntry
        ? orthogonalRouteCollisionScore(
            targetX,
            sourceX,
            sourceY,
            targetX,
            targetY
          )
        : Number.POSITIVE_INFINITY;

    const canUseDirectTopDrop =
      usesTopTargetEntry
      && !canUseDirectSideEntry
      && Math.abs(targetX - sourceX) > 80
      && directTopDropCollisionScore === 0;

    const routeLaneX =
      canUseDirectSideEntry
        ? sideApproachLaneX
        : canUseDirectTopDrop
        ? targetX
        : branchLaneX;

    if (canUseDirectSideEntry) {

      labelX = sourceX + ((routeLaneX - sourceX) * 0.78);
      labelY = sourceY + ((sideTargetY - sourceY) * 0.42);
    }

    const topTargetApproachY =
      targetY - 18;

    const targetEntrySegment = canUseDirectSideEntry
      ? `
        L ${routeLaneX} ${sideTargetY}
        L ${sideTargetX} ${sideTargetY}
      `
      : canUseDirectTopDrop
      ? `
        L ${targetX} ${targetY}
      `
      : usesTopTargetEntry
      ? `
        L ${routeLaneX} ${topTargetApproachY}
        L ${targetX} ${topTargetApproachY}
        L ${targetX} ${targetY}
      `
      : `
        L ${routeLaneX} ${targetY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

    edgePath = label && canBreakVerticalLane
      ? `
        M ${sourceX} ${sourceY}
        L ${routeLaneX} ${sourceY}
        L ${routeLaneX} ${verticalGapStartY}
        M ${routeLaneX} ${verticalGapEndY}
        ${targetEntrySegment}
      `
      : `
        M ${sourceX} ${sourceY}
        L ${routeLaneX} ${sourceY}
        ${targetEntrySegment}
      `;

    if (isLongBypassBranch && label) {

      const stableLabel = stabilizeLabelPosition(
        labelX,
        labelY,
        {
          offsets: [
            [0, 0],
            [0, -18],
            [0, 18],
            [24, 0],
            [-24, 0],
            [24, -16],
            [-24, -16]
          ]
        }
      );

      labelX = stableLabel.x;
      labelY = stableLabel.y;
    }

    if (!canBreakVerticalLane) {

      if (!isLongBypassBranch) {

        labelX = sourceX + ((targetEntryX - sourceX) * 0.5);
        labelY = targetY - 12;
      }
    }

  } else if (routingType === "RIGHT_EXTERNAL") {

    const sourceBranchCountValue =
      routingType === "BUSINESS_BRANCH"
        ? data?.source_business_branch_count
        : data?.source_error_branch_count;

    const branchGroupLayout =
      routingType === "BUSINESS_BRANCH"
        ? data?.source_business_branch_layout || "single"
        : data?.source_error_branch_layout || "single";

    const sourceBranchMaxY =
      routingType === "BUSINESS_BRANCH"
        ? data?.source_business_branch_max_y
        : data?.source_error_branch_max_y;

    const hasSourceErrorBranchCount =
      sourceBranchCountValue !== undefined
      && sourceBranchCountValue !== null;

    const sourceErrorBranchCount =
      Math.max(
        Number(sourceBranchCountValue || laneOffset || 1),
        laneOffset,
        1
      );

    const usesSharedBranchSpine =
      sourceErrorBranchCount > 1
      && branchGroupLayout !== "horizontal";

    const usesHorizontalBranchBus =
      sourceErrorBranchCount > 1
      && branchGroupLayout === "horizontal";

    const usesSingleDirectBranch =
      routingType === "RIGHT_EXTERNAL"
      && sourceErrorBranchCount <= 1;

    const targetEntryX =
      targetX - 42;

    const branchExitX =
      usesSharedBranchSpine || usesHorizontalBranchBus
        ? sourceX + 52
        : sourceX;

    const finalSpineY =
      Number.isFinite(Number(sourceBranchMaxY))
        ? Number(sourceBranchMaxY)
        : sourceY
          + 90
          + ((sourceErrorBranchCount - 1) * 125);

    const spinePath =
      usesSharedBranchSpine
      && hasSourceErrorBranchCount
      && laneOffset === 1
        ? `
          M ${sourceX} ${sourceY}
          L ${branchExitX} ${sourceY}
          L ${branchExitX} ${finalSpineY}
        `
        : !hasSourceErrorBranchCount
        ? `
          M ${sourceX} ${sourceY}
          L ${branchExitX} ${sourceY}
          L ${branchExitX} ${targetY}
        `
        : usesHorizontalBranchBus
        && laneOffset === 1
        ? `
          M ${sourceX} ${sourceY}
          L ${branchExitX} ${sourceY}
          L ${branchExitX} ${targetY}
        `
        : "";

    const branchWidth =
      targetEntryX - branchExitX;

    const labelWidth =
      estimateBranchLabelWidth();

    const labelLeadIn =
      routingType === "BUSINESS_BRANCH"
        ? 76
        : 66;

    const preferredLabelX =
      branchExitX
      + Math.min(
          Math.max(
            branchWidth * 0.34,
            labelLeadIn + (labelWidth / 2)
          ),
          branchWidth * 0.56
        );

    const maxLabelX =
      targetEntryX - (labelWidth / 2) - 34;

    labelX = Math.max(
      branchExitX + labelLeadIn,
      Math.min(
        preferredLabelX,
        maxLabelX
      )
    );

    labelY = targetY;

    const labelLanePadding =
      10;

    const singleBranchLabelGapStartX =
      labelX - (labelWidth / 2) - labelLanePadding;

    const singleBranchLabelGapEndX =
      labelX + (labelWidth / 2) + labelLanePadding;

    if (usesSingleDirectBranch) {

      const isSameRow =
        Math.abs(sourceY - targetY) < 8;

      const directEntryX =
        targetX - 18;

      labelY = isSameRow
        ? sourceY
        : targetY;

      edgePath = label
        ? isSameRow
          ? `
            M ${sourceX} ${sourceY}
            L ${singleBranchLabelGapStartX} ${sourceY}
            M ${singleBranchLabelGapEndX} ${sourceY}
            L ${directEntryX} ${targetY}
            L ${targetX} ${targetY}
          `
          : `
            M ${sourceX} ${sourceY}
            L ${singleBranchLabelGapStartX} ${sourceY}
            M ${singleBranchLabelGapEndX} ${sourceY}
            L ${directEntryX} ${targetY}
            L ${targetX} ${targetY}
          `
        : `
          M ${sourceX} ${sourceY}
          L ${directEntryX} ${targetY}
          L ${targetX} ${targetY}
        `;

    } else {

    const labelGapStartX =
      Math.max(
        branchExitX + 38,
        labelX - (labelWidth / 2) - labelLanePadding
      );

    const labelGapEndX =
      Math.min(
        targetEntryX - 30,
        labelX + (labelWidth / 2) + labelLanePadding
      );

    const branchStartPath =
      usesSharedBranchSpine || usesHorizontalBranchBus
        ? `
          M ${branchExitX} ${targetY}
          L ${labelGapStartX} ${targetY}
          M ${labelGapEndX} ${targetY}
          L ${targetEntryX} ${targetY}
        `
        : `
          M ${sourceX} ${sourceY}
          L ${labelGapStartX} ${targetY}
          M ${labelGapEndX} ${targetY}
          L ${targetEntryX} ${targetY}
        `;

    edgePath = `
      ${spinePath}
      ${branchStartPath}
      L ${targetX} ${targetY}
    `;

    }

  } else if (routingType === "TERMINAL_BRANCH") {

    const exitsFromBottom =
      sourcePosition === "bottom"
      || data?.source_handle === "success";

    const sameRow =
      Math.abs(sourceY - targetY) < 8;

    const direction =
      targetX >= sourceX ? 1 : -1;

    const targetEntryX =
      targetX - (direction * 18);

    const labelWidth =
      estimateBranchLabelWidth();

    const branchWidth =
      Math.abs(targetEntryX - sourceX);

    labelX = sourceX + ((targetEntryX - sourceX) * 0.46);

    labelY = sameRow
      ? sourceY - 12
      : sourceY + ((targetY - sourceY) * 0.45) - 12;

    if (exitsFromBottom) {

      const isAlignedVertical =
        Math.abs(sourceX - targetX) < 8;

      if (isAlignedVertical) {

        labelX = sourceX;
        labelY = sourceY + ((targetY - sourceY) * 0.48);

        const labelGapStartY =
          labelY - (verticalLabelGap / 2);

        const labelGapEndY =
          labelY + (verticalLabelGap / 2);

        edgePath = label
          ? `
            M ${sourceX} ${sourceY}
            L ${sourceX} ${labelGapStartY}
            M ${sourceX} ${labelGapEndY}
            L ${targetX} ${targetY}
          `
          : `
            M ${sourceX} ${sourceY}
            L ${targetX} ${targetY}
          `;

      } else {

      const verticalDropY =
        sourceY + Math.max(
          28,
          Math.min(
            72,
            Math.abs(targetY - sourceY) * 0.45
          )
        );

      labelX = sourceX + ((targetEntryX - sourceX) * 0.52);
      labelY = verticalDropY - 12;

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${sourceX} ${verticalDropY}
        L ${targetEntryX} ${verticalDropY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

      }

    } else if (label && sameRow && branchWidth > labelWidth + 42) {

      const labelLanePadding =
        10;

      const labelGapStartX =
        labelX - (direction * ((labelWidth / 2) + labelLanePadding));

      const labelGapEndX =
        labelX + (direction * ((labelWidth / 2) + labelLanePadding));

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${labelGapStartX} ${sourceY}
        M ${labelGapEndX} ${sourceY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

    } else if (sameRow) {

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

    } else {

      const elbowX =
        sourceX + ((targetEntryX - sourceX) * 0.55);

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${elbowX} ${sourceY}
        L ${elbowX} ${targetY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

    }

  } else if (routingType === "SUCCESS_REJOIN") {

    const direction =
      targetX >= sourceX ? 1 : -1;

    const targetEntryX =
      targetX - (direction * 10);

    const labelWidth =
      estimateBranchLabelWidth();

    const branchWidth =
      Math.abs(sourceX - targetEntryX);

    labelX = sourceX + ((targetEntryX - sourceX) * 0.48);
    labelY = sourceY;

    const hasSinglePeerErrorBranch =
      Number(data?.source_error_branch_count || 0) === 1
      && data?.source_type === "RESPONSE";

    const labelGapStartX =
      labelX - (direction * ((labelWidth / 2) + 14));

    const labelGapEndX =
      labelX + (direction * ((labelWidth / 2) + 14));

    const firstSegmentEndX =
      direction > 0
        ? Math.min(
            labelGapStartX,
            labelGapEndX
          )
        : Math.max(
            labelGapStartX,
            labelGapEndX
          );

    const secondSegmentStartX =
      direction > 0
        ? Math.max(
            labelGapStartX,
            labelGapEndX
          )
        : Math.min(
            labelGapStartX,
            labelGapEndX
          );

    const rejoinLaneStep =
      Math.min(
        Math.max(
          branchWidth * 0.18,
          24
        ),
        58
      );

    const preferredRejoinLaneX =
      direction > 0
        ? Math.min(
            targetEntryX - 28,
            secondSegmentStartX + rejoinLaneStep
          )
        : Math.max(
            targetEntryX + 28,
            secondSegmentStartX - rejoinLaneStep
          );

    const initialRejoinLaneX =
      clearRestartLaneX(
        preferredRejoinLaneX,
        direction,
        sourceY,
        targetY,
        {
          sourceX,
          sourceY,
          targetX,
          targetY
        }
      );

    const rejoinLaneX =
      direction > 0
      && initialRejoinLaneX > targetEntryX - 18
        ? targetX - 14
        : direction < 0
        && initialRejoinLaneX < targetEntryX + 18
        ? targetX + 14
        : initialRejoinLaneX;

    const rejoinSegmentStartX =
      direction > 0
        ? Math.min(
            secondSegmentStartX,
            rejoinLaneX - 10
          )
        : Math.max(
            secondSegmentStartX,
            rejoinLaneX + 10
          );

    const usesResponseDownStem =
      data?.source_type === "RESPONSE"
      && sourcePosition === "bottom"
      && targetY > sourceY + 28;

    const usesTopTargetEntry =
      targetPosition === "top"
      && !usesResponseDownStem;

    const responseStemY =
      sourceY + Math.min(
        72,
        Math.max(
          34,
          (targetY - sourceY) * 0.22
        )
      );

    const targetMetrics =
      getNodeMetrics(target);

    const responseTopTargetX =
      targetMetrics?.x ?? targetX;

    const responseTopTargetY =
      targetMetrics
        ? targetMetrics.y - ((targetMetrics.height || 80) / 2)
        : targetY;

    const canUseResponseTopEntry =
      usesResponseDownStem
      && Math.abs(responseTopTargetX - sourceX) > 80
      && responseTopTargetY > sourceY + 24
      && orthogonalRouteCollisionScore(
          responseTopTargetX,
          sourceX,
          sourceY,
          responseTopTargetX,
          responseTopTargetY
        ) === 0;

    if (
      Math.abs(sourceY - targetY) < 4
      && branchWidth > labelWidth + 42
    ) {

      if (hasSinglePeerErrorBranch) {

        labelY = sourceY + 36;
      }

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${firstSegmentEndX} ${sourceY}
        M ${secondSegmentStartX} ${sourceY}
        L ${targetEntryX} ${targetY}
        L ${targetX} ${targetY}
      `;

    } else {

      labelY = hasSinglePeerErrorBranch
        ? sourceY + 36
        : sourceY;

      if (usesTopTargetEntry) {

        edgePath = `
          M ${sourceX} ${sourceY}
          L ${firstSegmentEndX} ${sourceY}
          M ${rejoinSegmentStartX} ${sourceY}
          L ${targetX} ${sourceY}
          L ${targetX} ${targetY}
        `;

      } else if (canUseResponseTopEntry) {

        labelY = responseStemY;

        edgePath = `
          M ${sourceX} ${sourceY}
          L ${sourceX} ${responseStemY}
          L ${firstSegmentEndX} ${responseStemY}
          M ${rejoinSegmentStartX} ${responseStemY}
          L ${responseTopTargetX} ${responseStemY}
          L ${responseTopTargetX} ${responseTopTargetY}
        `;

      } else if (usesResponseDownStem) {

        labelY = responseStemY;

        edgePath = `
          M ${sourceX} ${sourceY}
          L ${sourceX} ${responseStemY}
          L ${firstSegmentEndX} ${responseStemY}
          M ${rejoinSegmentStartX} ${responseStemY}
          L ${rejoinLaneX} ${responseStemY}
          L ${rejoinLaneX} ${targetY}
          L ${targetEntryX} ${targetY}
          L ${targetX} ${targetY}
        `;

      } else {

        edgePath = `
          M ${sourceX} ${sourceY}
          L ${firstSegmentEndX} ${sourceY}
          M ${rejoinSegmentStartX} ${sourceY}
          L ${rejoinLaneX} ${sourceY}
          L ${rejoinLaneX} ${targetY}
          L ${targetEntryX} ${targetY}
          L ${targetX} ${targetY}
        `;
      }
    }

  } else if (routingType === "REVIEW_BRANCH") {

    const reviewBranchCount =
      Number(data?.source_review_branch_count || 1);

    const reviewLaneIndex =
      Math.max(
        Number(data?.lane_offset || 1),
        1
      );

    const targetEntryX =
      sourceX > targetX
        ? targetX + 10
        : targetX - 10;

    const reviewLaneSpread =
      reviewBranchCount > 1
        ? (reviewLaneIndex - 1) * 34
        : 0;

    const branchLaneX =
      Math.min(sourceX, targetX)
      - 70
      - reviewLaneSpread;

    const labelWidth =
      estimateBranchLabelWidth();

    const reviewBranchWidth =
      Math.abs(sourceX - targetEntryX);

    const preferredReviewLabelX =
      sourceX > targetX
        ? sourceX - Math.max(
            58,
            reviewBranchWidth * 0.42
          )
        : sourceX + Math.max(
            58,
            reviewBranchWidth * 0.42
          );

    const minReviewLabelX =
      Math.min(sourceX, targetEntryX) + (labelWidth / 2) + 18;

    const maxReviewLabelX =
      Math.max(sourceX, targetEntryX) - (labelWidth / 2) - 18;

    labelX = maxReviewLabelX > minReviewLabelX
      ? Math.min(
          Math.max(
            preferredReviewLabelX,
            minReviewLabelX
          ),
          maxReviewLabelX
        )
      : sourceX + ((targetEntryX - sourceX) * 0.5);

    const reviewBranchY =
      reviewBranchCount > 1
        ? targetY
        : sourceY;

    labelY = reviewBranchY;

    const labelGapStartX =
      labelX - (labelWidth / 2) - 14;

    const labelGapEndX =
      labelX + (labelWidth / 2) + 14;

    const usesTopTargetEntry =
      targetPosition === "top";

    const topTargetApproachY =
      targetY - 18;

    if (
      Math.abs(reviewBranchY - targetY) < 4
      && Math.abs(sourceY - reviewBranchY) < 4
    ) {

      edgePath = usesTopTargetEntry
        ? `
          M ${sourceX} ${sourceY}
          L ${labelGapEndX} ${sourceY}
          M ${labelGapStartX} ${sourceY}
          L ${targetX} ${sourceY}
          L ${targetX} ${topTargetApproachY}
          L ${targetX} ${targetY}
        `
        : `
          M ${sourceX} ${sourceY}
          L ${labelGapEndX} ${sourceY}
          M ${labelGapStartX} ${sourceY}
          L ${targetEntryX} ${targetY}
          L ${targetX} ${targetY}
        `;

    } else {

      edgePath = usesTopTargetEntry
        ? `
          M ${sourceX} ${sourceY}
          L ${sourceX} ${reviewBranchY}
          L ${labelGapEndX} ${reviewBranchY}
          M ${labelGapStartX} ${reviewBranchY}
          L ${branchLaneX} ${reviewBranchY}
          L ${branchLaneX} ${topTargetApproachY}
          L ${targetX} ${topTargetApproachY}
          L ${targetX} ${targetY}
        `
        : `
          M ${sourceX} ${sourceY}
          L ${sourceX} ${reviewBranchY}
          L ${labelGapEndX} ${reviewBranchY}
          M ${labelGapStartX} ${reviewBranchY}
          L ${branchLaneX} ${reviewBranchY}
          L ${branchLaneX} ${targetY}
          L ${targetEntryX} ${targetY}
          L ${targetX} ${targetY}
        `;
    }

  } else if (routingType === "MERGE_JOIN") {

    edgePath = `
      M ${sourceX} ${sourceY}
      L ${targetX} ${sourceY}
      L ${targetX} ${targetY}
    `;

    labelX = targetX;
    labelY = sourceY;

  } else if (routingType === "LOCAL_RETRY_LOOP") {

    const localRetrySide =
      data?.local_retry_side === "left"
        ? "left"
        : "right";

    const localRetrySpan =
      Math.abs(sourceY - targetY);

    const localRetryAnchor =
      data?.local_retry_anchor || "side";

    const isCompactLocalRetry =
      localRetrySpan <= 420;

    const localRetryLaneDistance =
      isCompactLocalRetry
        ? 56
        : localRetrySide === "left"
        ? 260
        : 420;

    const localLoopLaneX =
      localRetrySide === "left"
        ? Math.min(sourceX, targetX) - localRetryLaneDistance
        : Math.max(sourceX, targetX) + localRetryLaneDistance;

    const targetArrowX =
      localRetrySide === "left"
        ? targetX - 10
        : targetX + 10;

    if (localRetryAnchor === "top") {

      const sourceMetrics =
        getNodeMetrics(source);

      const targetMetrics =
        getNodeMetrics(target);

      const sourceSideX =
        sourceMetrics
          ? sourceMetrics.x + (
              localRetrySide === "left"
                ? -(sourceMetrics.width / 2)
                : sourceMetrics.width / 2
            )
          : sourceX;

      const sourceSideY =
        sourceMetrics?.y ?? sourceY;

      const targetSideX =
        targetMetrics
          ? targetMetrics.x + (
              localRetrySide === "left"
                ? -(targetMetrics.width / 2)
                : targetMetrics.width / 2
            )
          : targetArrowX;

      const targetSideY =
        targetMetrics?.y ?? targetY;

      const sideLaneX =
        localRetrySide === "left"
          ? Math.min(
              localLoopLaneX,
              sourceSideX - 46,
              targetSideX - 46
            )
          : Math.max(
              localLoopLaneX,
              sourceSideX + 46,
              targetSideX + 46
            );

      edgePath = `
        M ${sourceSideX} ${sourceSideY}
        L ${sideLaneX} ${sourceSideY}
        L ${sideLaneX} ${targetSideY}
        L ${targetSideX} ${targetSideY}
      `;

      labelX = localRetrySide === "left"
        ? sideLaneX - 18
        : sideLaneX + 18;

      labelY = sourceSideY + ((targetSideY - sourceSideY) * 0.5);

    } else {

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${localLoopLaneX} ${sourceY}
        L ${localLoopLaneX} ${targetY}
        L ${targetArrowX} ${targetY}
      `;

      labelX = localRetrySide === "left"
        ? localLoopLaneX - 18
        : localLoopLaneX + 18;

      labelY = sourceY + ((targetY - sourceY) * 0.5);
    }

  } else if (routingType === "OUTER_LOOP") {

    const isErrorRetryReturn =
      targetY < sourceY
      && (
        data?.source_type === "SYSTEM_ACTIVITY"
        || data?.collapsed_merge
        || data?.render_expanded_error
        || sourceX > targetX + 60
      );

    const busOffsetY =
      isErrorRetryReturn
        ? 0
        : (laneOffset - 1) * 10;

    const sourceWidth =
      Number(data?.source_width || 0);

    const sharedRetrySourceWidth =
      Number(
        data?.target_outer_loop_max_source_width
        || sourceWidth
      );

    const occupiedLeftRetryBoundary =
      Number(data?.restart_left_occupied_left_x);

    const hasOccupiedLeftRetryBoundary =
      Number.isFinite(occupiedLeftRetryBoundary);

    const occupiedRightRetryBoundary =
      Number(data?.restart_right_occupied_right_x);

    const hasOccupiedRightRetryBoundary =
      Number.isFinite(occupiedRightRetryBoundary);

    const targetOuterLoopCount =
      Number(data?.target_outer_loop_count || 0);

    const targetOuterLoopMaxSourceY =
      Number(data?.target_outer_loop_max_source_y || sourceY);

    const retryVerticalSpan =
      Math.abs(sourceY - targetY);

    const isCompactSingleRetryReturn =
      isErrorRetryReturn
      && targetOuterLoopCount <= 1
      && retryVerticalSpan <= 900;

    const compactRetryLaneDistance =
      retryVerticalSpan <= 420
        ? 76
        : 132;

    const baseReturnLaneX =
      isErrorRetryReturn
        ? isCompactSingleRetryReturn
          ? sourceX < targetX
            ? sourceX - compactRetryLaneDistance
            : sourceX + compactRetryLaneDistance
        : sourceX < targetX
          ? Math.min(
              sourceX - (
                sharedRetrySourceWidth > 0
                  ? sharedRetrySourceWidth
                  : 0
              ) - 46,
              Math.min(sourceX, targetX) - 46,
              hasOccupiedLeftRetryBoundary
                ? occupiedLeftRetryBoundary
                : Number.POSITIVE_INFINITY
            )
          : Math.max(
              Math.max(sourceX, targetX) + 46,
              hasOccupiedRightRetryBoundary
                ? occupiedRightRetryBoundary
                : Number.NEGATIVE_INFINITY
            )
        : Number(
            data?.global_return_bus_x
            || GLOBAL_RETURN_BUS_X
          );

    const outerLoopBusLaneIndex =
      Math.max(
        Number(data?.outer_loop_bus_lane_index || 1),
        1
      );

    const outerLoopBusLaneStep =
      96;

    const spacedReturnLaneX =
      isErrorRetryReturn
        ? baseReturnLaneX + (
            baseReturnLaneX > sourceX
              ? 1
              : -1
          ) * outerLoopBusLaneStep * (outerLoopBusLaneIndex - 1)
        : baseReturnLaneX;

    const returnLaneDirection =
      spacedReturnLaneX > sourceX
        ? 1
        : -1;

    const returnLaneX =
      isErrorRetryReturn
        ? clearRestartLaneX(
            spacedReturnLaneX,
            returnLaneDirection,
            sourceY,
            targetY,
            {
              sourceX,
              sourceY,
              targetX,
              targetY,
              sideLimitX: returnLaneDirection > 0
                ? Math.max(sourceX, targetX)
                : Math.min(sourceX, targetX)
            }
          )
        : spacedReturnLaneX;

    const drawsSharedRetryBus =
      !isErrorRetryReturn
      || targetOuterLoopCount <= 1
      || Math.abs(sourceY - targetOuterLoopMaxSourceY) < 24;

    suppressMarkerEnd = !drawsSharedRetryBus;

    const targetArrowX =
      returnLaneX > targetX
        ? targetX + 10
        : targetX - 10;

    edgePath = drawsSharedRetryBus
      ? `
        M ${sourceX} ${sourceY}
        L ${returnLaneX} ${sourceY + busOffsetY}
        L ${returnLaneX} ${targetY - busOffsetY}
        L ${targetArrowX} ${targetY}
      `
      : `
        M ${sourceX} ${sourceY}
        L ${returnLaneX} ${sourceY}
      `;

    const labelStackOffset =
      Math.max(
        laneOffset - 1,
        0
      ) * 56;

    labelX = sourceX + 180;
    labelY = sourceY - 110 + labelStackOffset;

  } else if (routingType === "RESTART_FLOW") {

    const restartSide =
      data?.restart_side === "right"
        ? "right"
        : "left";

    const restartLaneIndex =
      Math.max(
        Number(data?.restart_lane_index || 1),
        1
      );

    const isUserRestart =
      data?.source_type === "RESPONSE"
      && isRestartLabel;

    const isLongMainRestart =
      targetY < sourceY
      && Math.abs(sourceX - targetX) < 80
      && Math.abs(sourceY - targetY) > 520;

    const isLocalValidationRetry =
      targetY < sourceY
      && !isLongMainRestart
      && !isRestartLabel;

    const localRetrySpan =
      Math.abs(sourceY - targetY);

    const localRetryLaneDistance =
      Math.min(
        180,
        Math.max(
          88,
          82 + (localRetrySpan * 0.08)
        )
      );

    const restartLaneDistance =
      isLocalValidationRetry
        ? localRetryLaneDistance
        : isLongMainRestart
        ? Math.min(
            330,
            235 + (Math.abs(sourceY - targetY) * 0.025)
          )
        : isUserRestart
        ? 260
        : 145;

    const occupiedRestartRightX =
      Number(data?.restart_left_occupied_right_x);

    const occupiedRestartLeftX =
      Number(data?.restart_left_occupied_left_x);

    const occupiedRestartOuterRightX =
      Number(
        data?.restart_right_occupied_right_x
      );

    const hasOccupiedRestartRightX =
      Number.isFinite(occupiedRestartRightX);

    const hasOccupiedRestartLeftX =
      Number.isFinite(occupiedRestartLeftX);

    const hasOccupiedRestartOuterRightX =
      Number.isFinite(occupiedRestartOuterRightX);

    const sourceLeftClearance =
      Math.min(sourceX, targetX) - occupiedRestartRightX;

    const canUseInnerRestartLane =
      hasOccupiedRestartRightX
      && sourceLeftClearance >= 240;

    const nearestClearRestartLaneX =
      hasOccupiedRestartRightX
        ? Math.min(
            occupiedRestartRightX,
            Math.min(sourceX, targetX) - 92
          )
        : null;

    const preferredRestartLaneX =
      restartSide === "right"
        ? Math.max(
            Math.max(sourceX, targetX)
            + restartLaneDistance
            + ((restartLaneIndex - 1) * 132),
            hasOccupiedRestartOuterRightX
              ? occupiedRestartOuterRightX + 132
                + ((restartLaneIndex - 1) * 132)
              : Number.NEGATIVE_INFINITY
          )
        : Math.min(sourceX, targetX) - restartLaneDistance;

    const baseRestartLaneX =
      restartSide === "right"
        ? preferredRestartLaneX
        :
      isLongMainRestart
      && hasOccupiedRestartRightX
        ? canUseInnerRestartLane
          ? Math.max(
              preferredRestartLaneX,
              nearestClearRestartLaneX
            )
          : hasOccupiedRestartLeftX
          ? Math.min(
              preferredRestartLaneX,
              occupiedRestartLeftX - 132
            )
          : preferredRestartLaneX
        : preferredRestartLaneX;

    const restartLaneDirection =
      baseRestartLaneX > sourceX ? 1 : -1;

    let restartLaneX =
      (
        isLongMainRestart
        || routingType === "RESTART_FLOW"
      )
        ? clearRestartLaneX(
            baseRestartLaneX,
            restartLaneDirection,
            sourceY,
            targetY,
            {
              sourceX,
              sourceY,
              targetX,
              targetY,
              sideLimitX: restartSide === "left"
                && isLongMainRestart
                && !canUseInnerRestartLane
                && hasOccupiedRestartLeftX
                ? occupiedRestartLeftX
                : restartSide === "right"
                ? Math.max(sourceX, targetX)
                : Math.min(sourceX, targetX)
            }
          )
        : baseRestartLaneX;

    const isResponseReworkToSideTarget =
      data?.source_type === "RESPONSE"
      && data?.target_type === "MANUAL_ACTIVITY"
      && targetY < sourceY
      && !isRestartLabel
      && Math.abs(sourceX - targetX) > 80;

    if (
      isResponseReworkToSideTarget
      && targetPosition === "right"
    ) {

      restartLaneX = Math.max(
        restartLaneX,
        targetX + 36
      );
    }

    if (
      isResponseReworkToSideTarget
      && targetPosition === "left"
    ) {

      restartLaneX = Math.min(
        restartLaneX,
        targetX - 36
      );
    }

    if (
      targetPosition === "bottom"
      && targetY < sourceY
      && Math.abs(targetX - sourceX) > 80
      && orthogonalRouteCollisionScore(
          targetX,
          sourceX,
          sourceY,
          targetX,
          targetY
        ) === 0
    ) {

      restartLaneX = targetX;
    }

    const restartDirection =
      restartLaneX > sourceX ? 1 : -1;

    const targetHasErrorRetryBus =
      Number(data?.target_outer_loop_count || 0) > 0;

    const restartTargetY =
      isUserRestart && targetHasErrorRetryBus
        ? targetY + 26
        : targetY;

    const restartLabelDistance =
      Math.min(
        Math.max(
          labelGap * 0.9,
          54
        ),
        96
      );

    labelX = sourceX + (restartDirection * restartLabelDistance);
    labelY = sourceY;

    const labelGapStartX =
      labelX - (labelGap / 2);

    const labelGapEndX =
      labelX + (labelGap / 2);

    const firstSegmentEndX =
      restartLaneX > sourceX
        ? labelGapStartX
        : labelGapEndX;

    const secondSegmentStartX =
      restartLaneX > sourceX
        ? labelGapEndX
        : labelGapStartX;

    const targetArrowX =
      restartLaneX < targetX
        ? targetX - 10
        : targetX + 10;

    const usesTopRestartTarget =
      targetPosition === "top";

    const usesBottomRestartTarget =
      targetPosition === "bottom";

    const restartTargetApproachY =
      restartTargetY - 14;

    const restartBottomApproachY =
      restartTargetY + 14;

    const restartLaneTerminalY =
      usesBottomRestartTarget
        ? restartBottomApproachY
        : restartTargetY;

    const restartFinalSegment = usesTopRestartTarget
      ? `
        L ${targetX} ${restartTargetApproachY}
        L ${targetX} ${targetY}
      `
      : usesBottomRestartTarget
      ? `
        L ${targetX} ${restartBottomApproachY}
        L ${targetX} ${targetY}
      `
      : `
        L ${targetArrowX} ${restartTargetY}
      `;

    if (isLocalValidationRetry) {

      labelX = restartLaneX + (restartDirection * 14);
      labelY = sourceY + ((targetY - sourceY) * 0.5);

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${restartLaneX} ${sourceY}
        L ${restartLaneX} ${restartLaneTerminalY}
        ${restartFinalSegment}
      `;

    } else if (isLongMainRestart) {

      labelX = sourceX + ((restartLaneX - sourceX) * 0.56);
      labelY = sourceY;

      const longLabelGapStartX =
        labelX - (labelGap / 2);

      const longLabelGapEndX =
        labelX + (labelGap / 2);

      const longFirstSegmentEndX =
        restartLaneX > sourceX
          ? longLabelGapStartX
          : longLabelGapEndX;

      const longSecondSegmentStartX =
        restartLaneX > sourceX
          ? longLabelGapEndX
          : longLabelGapStartX;

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${longFirstSegmentEndX} ${sourceY}
        M ${longSecondSegmentStartX} ${sourceY}
        L ${restartLaneX} ${sourceY}
        L ${restartLaneX} ${restartLaneTerminalY}
        ${restartFinalSegment}
      `;

    } else {

      edgePath = `
        M ${sourceX} ${sourceY}
        L ${firstSegmentEndX} ${sourceY}
        M ${secondSegmentStartX} ${sourceY}
        L ${restartLaneX} ${sourceY}
        L ${restartLaneX} ${restartLaneTerminalY}
        ${restartFinalSegment}
      `;

    }

  } else if (routingType === "DOWN") {

    labelX = sourceX;
    labelY = sourceY + ((targetY - sourceY) * 0.35);

    const labelGapStartY =
      labelY - (verticalLabelGap / 2);

    const labelGapEndY =
      labelY + (verticalLabelGap / 2);

    edgePath = label
      ? `
        M ${sourceX} ${sourceY}
        L ${sourceX} ${labelGapStartY}
        M ${sourceX} ${labelGapEndY}
        L ${sourceX} ${targetY}
      `
      : `
        M ${sourceX} ${sourceY}
        L ${sourceX} ${targetY}
      `;

  } else if (routingType === "VERTICAL") {

    const isAlignedVertical =
      Math.abs(sourceX - targetX) < 4;

    const elbowY =
      sourceY + ((targetY - sourceY) * 0.55);

    edgePath = isAlignedVertical
      ? `
        M ${sourceX} ${sourceY}
        L ${targetX} ${targetY}
      `
      : `
        M ${sourceX} ${sourceY}
        L ${sourceX} ${elbowY}
        L ${targetX} ${elbowY}
        L ${targetX} ${targetY}
      `;

    labelX = sourceX;
    labelY = sourceY + ((targetY - sourceY) * 0.5);

  } else {

    const pathResult =
      getSmoothStepPath({

        sourceX,
        sourceY,

        targetX,
        targetY,

        sourcePosition,
        targetPosition,

        borderRadius: 16,

        offset: 30
      });

    edgePath = pathResult[0];
    labelX = pathResult[1];
    labelY = pathResult[2];
  }

  // ===================================
  // EDGE COLOR
  // ===================================

  let edgeColor = "#6B7280";

  if (routingType === "RIGHT_EXTERNAL") {

    edgeColor = "#DC2626";

  } else if (
    routingType === "OUTER_LOOP"
    || routingType === "LOCAL_RETRY_LOOP"
  ) {

    edgeColor = "#2563EB";

  } else if (routingType === "MERGE_JOIN") {

    edgeColor = "#6B7280";

  } else if (routingType === "RESTART_FLOW") {

    edgeColor = "#0F766E";

  } else if (routingType === "SUCCESS_REJOIN") {

    edgeColor = "#16A34A";

  } else if (routingType === "REVIEW_BRANCH") {

    edgeColor = "#7C3AED";

  } else if (routingType === "BUSINESS_BRANCH") {

    edgeColor = "#7C3AED";

  } else if (routingType === "TERMINAL_BRANCH") {

    edgeColor = "#7C3AED";

  } else if (routingType === "DOWN") {

    edgeColor = "#16A34A";

  } else if (routingType === "CONNECTOR_STUB") {

    edgeColor = "#111827";

  }

  const isMergeJoin =
    routingType === "MERGE_JOIN";

  const strokeWidth =
    routingType === "OUTER_LOOP"
    || routingType === "LOCAL_RETRY_LOOP"
      ? 1.6
      : 2;

  const strokeDasharray =
    isMergeJoin
      ? "4 4"
      : routingType === "OUTER_LOOP"
      || routingType === "LOCAL_RETRY_LOOP"
      ? "5 5"
      : undefined;

  const edgeOpacity =
    routingType === "OUTER_LOOP"
    || routingType === "LOCAL_RETRY_LOOP"
      ? 0.72
      : 1;

  const isErrorBranch =
    routingType === "RIGHT_EXTERNAL";

  const isBusinessBranch =
    routingType === "BUSINESS_BRANCH";

  const isTerminalBranch =
    routingType === "TERMINAL_BRANCH";

  const isDownLabel =
    routingType === "DOWN";

  const isRestartFlowLabel =
    routingType === "RESTART_FLOW";

  const isSuccessRejoinLabel =
    routingType === "SUCCESS_REJOIN";

  const isReviewBranchLabel =
    routingType === "REVIEW_BRANCH";

  const isBranchLabel = [
    "RIGHT_EXTERNAL",
    "BUSINESS_BRANCH",
    "TERMINAL_BRANCH",
    "REVIEW_BRANCH",
    "RESTART_FLOW",
    "SUCCESS_REJOIN",
    "DOWN",
    "OUTER_LOOP",
    "LOCAL_RETRY_LOOP",
    "CONNECTOR_STUB"
  ].includes(routingType);

  const labelPadding =
    isBranchLabel
      ? "2px 5px"
      : "4px 8px";

  const labelFontSize =
    isBranchLabel
      ? "10px"
      : "11px";

  const labelBackground =
    isBranchLabel
      ? "white"
      : "white";

  const labelBorder =
    isBranchLabel
      ? "none"
      : `1px solid ${edgeColor}`;

  const labelColor =
    isBranchLabel
      ? "#111827"
      : edgeColor;

  const labelTextShadow =
    isBranchLabel
      ? "0 1px 0 white, 1px 0 0 white, 0 -1px 0 white, -1px 0 0 white"
      : undefined;

  const labelMaxWidth =
    shouldWrapOutcomeLabel
      ? "58px"
      : isErrorBranch
      ? shouldWrapLabel
        ? "132px"
        : "none"
      : isBusinessBranch
      ? shouldWrapLabel
        ? "132px"
        : "none"
      : isTerminalBranch
      ? shouldWrapLabel
        ? "132px"
        : "none"
      : isReviewBranchLabel
      ? shouldWrapLabel
        ? "128px"
        : "none"
      : isRestartFlowLabel
      ? shouldWrapLabel
        ? "128px"
        : "none"
      : isSuccessRejoinLabel
      ? shouldWrapLabel
        ? "128px"
        : "none"
      : isDownLabel
      ? shouldWrapLabel
        ? "116px"
        : "none"
      : isBranchLabel
      ? "120px"
      : undefined;

  const labelWhiteSpace =
    isBranchLabel && shouldWrapLabel
      ? "normal"
      : "nowrap";

  const labelLineHeight =
    isBranchLabel
      ? "1.15"
      : undefined;

  const labelCandidateOffsets =
    isDownLabel
      ? [
          [0, 0],
          [24, 0],
          [-24, 0],
          [0, -22],
          [0, 22],
          [32, -16],
          [-32, -16],
          [32, 16],
          [-32, 16]
        ]
      : isRestartFlowLabel
      || isSuccessRejoinLabel
      || isReviewBranchLabel
      ? [
          [0, 0],
          [0, -18],
          [0, 18],
          [34, 0],
          [-34, 0],
          [34, -18],
          [-34, -18],
          [34, 18],
          [-34, 18]
        ]
      : isBranchLabel
      ? [
          [0, 0],
          [0, -20],
          [0, 20],
          [30, 0],
          [-30, 0],
          [30, -16],
          [-30, -16],
          [30, 16],
          [-30, 16]
        ]
      : [
          [0, 0],
          [0, -18],
          [0, 18],
          [24, 0],
          [-24, 0]
        ];

  const stabilizedLabelPosition = stabilizeLabelPosition(
    labelX,
    labelY,
    {
      offsets: labelCandidateOffsets
    }
  );

  labelX = stabilizedLabelPosition.x;
  labelY = stabilizedLabelPosition.y;

  const markerId =
    `fds-arrow-${id}`;

  const effectiveMarkerEnd =
    isMergeJoin
    || suppressMarkerEnd
      ? undefined
      : `url(#${markerId})`;

  return (

    <>

      <defs>
        <marker
          id={markerId}
          markerWidth="8"
          markerHeight="8"
          refX="7.5"
          refY="4"
          orient="auto"
          markerUnits="strokeWidth"
        >
          <path
            d="M 0 0 L 8 4 L 0 8 z"
            fill={edgeColor}
          />
        </marker>
      </defs>

      <BaseEdge

        id={id}

        path={edgePath}

        markerEnd={effectiveMarkerEnd}

        style={{

          stroke: edgeColor,

          strokeWidth,

          strokeDasharray,

          opacity: edgeOpacity,

          ...style
        }}
      />

      {

        label && !isMergeJoin && (

          <EdgeLabelRenderer>

            <div

              style={{

                position: "absolute",

                transform: `translate(-50%, -50%) 
                translate(${labelX}px, ${labelY}px)`,

                background: labelBackground,

                padding: labelPadding,

                borderRadius: "6px",

                fontSize: labelFontSize,

                fontWeight: 700,

                color: labelColor,

                border: labelBorder,

                textShadow: labelTextShadow,

                whiteSpace: labelWhiteSpace,

                maxWidth: labelMaxWidth,

                lineHeight: labelLineHeight,

                textAlign: "center",

                pointerEvents: "all",

                zIndex: 9999,

                ...labelStyle
              }}
            >

              {labelText}

            </div>

          </EdgeLabelRenderer>
        )
      }

    </>
  );
}
