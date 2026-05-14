// https://leetcode.com/problems/count-unreachable-pairs-of-nodes-in-an-undirected-graph/description/
// Difficulty: Medium
// Tags: Graphs, union findl, undirected, unconnected

// Problem
/*
You are given an integer n. There is an undirected graph with n nodes, numbered from 0 to n - 1. You are given a 2D integer array edges where edges[i] = [ai, bi] denotes that there exists an undirected edge connecting nodes ai and bi.

Return the number of pairs of different nodes that are unreachable from each other.
*/

// Solution, O(V+E) time and O(V+E) space
/*
First, create an edge mapping in a hashtable, which takes O(E) time and O(E) space.

Then, find the sizes of all components, by creating a DFS function that explores out, also marking seen nodes to prevent overlap. We run the loop on each cell as if it were a parent, and for each cell we iterate over all edges. This takes V+E time and V space to store the seen cells. I also could've just not entered seen cells to prevent looping on their neighbors unnecessarily.

Then, iterate over the component sizes, calculating pairs with all future component sizes.
*/

var countPairs = function (n, edges) {
  const edgeMapping = {};
  for (const [a, b] of edges) {
    if (!(a in edgeMapping)) {
      edgeMapping[a] = [b];
    } else {
      edgeMapping[a].push(b);
    }

    if (!(b in edgeMapping)) {
      edgeMapping[b] = [a];
    } else {
      edgeMapping[b].push(a);
    }
  }

  const seen = new Set();

  function dfs(node) {
    seen.add(node);
    const adjacentEdges = edgeMapping[node];
    // a node with no edges
    if (adjacentEdges === undefined) {
      return;
    }

    for (const neighbor of adjacentEdges) {
      if (!seen.has(neighbor)) {
        dfs(neighbor);
      }
    }
  }

  const componentSizes = [];
  let prevTotalSeenNodes = 0;
  for (let node = 0; node <= n - 1; node++) {
    dfs(node);
    const totalSeenNodes = seen.size;
    // if we didn't get a new component, move on
    if (totalSeenNodes === prevTotalSeenNodes) {
      continue;
    }
    componentSizes.push(totalSeenNodes - prevTotalSeenNodes);
    prevTotalSeenNodes = totalSeenNodes;
  }

  let result = 0;
  let totalComponentSizesToRight = componentSizes.reduce(
    (acc, val) => acc + val,
    0
  );

  // iterate over the component sizes, forming pairs with all components to the right (right only to avoid duplicate pairs)
  for (let i = 0; i < componentSizes.length; i++) {
    totalComponentSizesToRight -= componentSizes[i];
    result += componentSizes[i] * totalComponentSizesToRight;
  }

  return result;
};
