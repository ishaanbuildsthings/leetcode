// https://leetcode.com/problems/reachable-nodes-with-restrictions/description/
// difficulty: medium
// tags: undirected, tree, graphs

// Problem
/*
There is an undirected tree with n nodes labeled from 0 to n - 1 and n - 1 edges.

You are given a 2D integer array edges of length n - 1 where edges[i] = [ai, bi] indicates that there is an edge between nodes ai and bi in the tree. You are also given an integer array restricted which represents restricted nodes.

Return the maximum number of nodes you can reach from node 0 without visiting a restricted node.

Note that node 0 will not be a restricted node.
*/

// Solution, O(V+E) time and O(V+E) space
/*
First, create an edge mapping which is V+E space. Then, iterate through all nodes starting from 0, marking ones we have seen to not duplicte nodes. This takes V+E time. Stop at seen or restricted nodes.
*/

var reachableNodes = function (n, edges, restricted) {
  const edgeMap = {}; // maps a node to a list of edges it can reach
  for (const [a, b] of edges) {
    if (!(a in edgeMap)) {
      edgeMap[a] = [b];
    } else {
      edgeMap[a].push(b);
    }

    if (!(b in edgeMap)) {
      edgeMap[b] = [a];
    } else {
      edgeMap[b].push(a);
    }
  }

  const restrictedSet = new Set();
  for (const restrictedNode of restricted) {
    restrictedSet.add(restrictedNode);
  }

  const seen = new Set();

  function dfs(node) {
    seen.add(node);
    const neighbors = edgeMap[node];

    if (neighbors) {
      for (const neighbor of neighbors) {
        if (!seen.has(neighbor) && !restrictedSet.has(neighbor)) {
          dfs(neighbor);
        }
      }
    }
  }

  dfs(0);

  return seen.size;
};
