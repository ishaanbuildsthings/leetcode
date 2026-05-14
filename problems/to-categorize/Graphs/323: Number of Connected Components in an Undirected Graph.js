// https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/description/
// Difficulty: Medium
// Tags: graphs, undirected, unconnected

// Problem
/*
You have a graph of n nodes. You are given an integer n and an array edges where edges[i] = [ai, bi] indicates that there is an edge between ai and bi in the graph.

Return the number of connected components in the graph.
*/

// Solution, O(V+E) time and O(V+E) space
/*
First, built an adjacency list for the nodes. Then, iterate through each node, doing a dfs and marking adjacent nodes as seen. When we do a root call on a node, if it was seen before it was part of an old component, otherwise we increment the component count.

We iterate through every edge, assembling the adjacency list. We iterate through every node to solve the problem. We also store up to E edges in the adjacency list and V nodes in the seen set.
*/

var countComponents = function (n, edges) {
  const seen = new Set();

  const neighbors = {}; // maps a node to a list of its edges

  for (const [a, b] of edges) {
    if (!(a in neighbors)) {
      neighbors[a] = [b];
    } else {
      neighbors[a].push(b);
    }

    if (!(b in neighbors)) {
      neighbors[b] = [a];
    } else {
      neighbors[b].push(a);
    }
  }

  function markSeenDfs(node) {
    seen.add(node);

    const neighborsForNode = neighbors[node];

    // it's possible some nodes were never includes in the edges list, so they won't have neighbors
    if (neighborsForNode === undefined) {
      return;
    }

    for (const neighbor of neighborsForNode) {
      if (!seen.has(neighbor)) {
        markSeenDfs(neighbor);
      }
    }
  }

  let result = 0;

  for (let node = 0; node < n; node++) {
    if (seen.has(node)) {
      continue;
    }
    result++;
    markSeenDfs(node);
  }

  return result;
};
