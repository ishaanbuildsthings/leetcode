// https://leetcode.com/problems/graph-valid-tree/description/
// Difficulty: Medium
// Tags: graph, unconnected, undirected

// Problem
/*
You have a graph of n nodes labeled from 0 to n - 1. You are given an integer n and a list of edges where edges[i] = [ai, bi] indicates that there is an undirected edge between nodes ai and bi in the graph.

Return true if the edges of the given graph make up a valid tree, and false otherwise.
*/

// Solution, O(V+E) time and O(V+E) space
/*
A graph is a valid tree if: 1) there are no cycles, 2) the graph is connected.

First, we populate an adjacency list, which takes O(E) time. Not O(V+E) since we might have nodes but no edges. Then, we will dfs out from the first node, checking if there is a path. The DFS function dfs's out to the "leaves" first, and returns false if it finds a path collision. It also has the side effect of populating all nodes seen.

If from the first node, we found a collision, we are not a tree. If we didn't find a collision, we are a tree if we saw every node.

For the dfs, we go to each node once, and for each node, we try all edges. I think this is technically a more complicated problem due to the pathing but we shouldn't ever take more than V+E time as an upper bound. The recursive stack depth is V if we see every node, so V+E space.
*/

var validTree = function (n, edges) {
  const adjList = {}; // maps a node to a list of adjacent nodes

  for (const [a, b] of edges) {
    if (!(a in adjList)) {
      adjList[a] = [b];
    } else {
      adjList[a].push(b);
    }

    if (!(b in adjList)) {
      adjList[b] = [a];
    } else {
      adjList[b].push(a);
    }
  }

  const seen = new Set();

  // this dfs's out, determining if from the root node, we form a tree. it works by detecting if there is any path. we need the prev paramter to not dfs back to the root that called us. it also marks every node as seen, so that we can tell if we have an unconnected graph (and therefore not a tree) later.
  function dfs(node, prev) {
    seen.add(node);

    const neighbors = adjList[node];

    // edge case if we have no edges for a node
    if (neighbors === undefined) {
      return true;
    }

    for (const neighbor of neighbors) {
      // don't go back to the node we just came from
      if (neighbor === prev) {
        continue;
      }
      if (seen.has(neighbor)) {
        return false;
      }
      if (!dfs(neighbor, node)) {
        return false;
      }
    }

    return true;
  }

  // if we don't have a tree from 0, return false
  if (!dfs(0, -1)) {
    return false;
  }

  if (Array.from(seen).length === n) {
    return true;
  }

  return false;
};
