// https://leetcode.com/problems/clone-graph/description/
// Difficulty: Medium
// tags: graphs, recursion, graphs with nodes, undirected graphs

// Problem
/*
Given a reference of a node in a connected undirected graph.

Return a deep copy (clone) of the graph.

Each node in the graph contains a value (int) and a list (List[Node]) of its neighbors.
*/

// Solution, O(V+E) time, O(V) space, where V is the number of nodes, and E is the number of edges.
/*
Define a recursive function, getClone, which when passed an old node, returns the new one. We also map old nodes to new nodes, so we don't duplicate nodes multiple times.

Start at the first node, build it, call build on all its neighbors and add those to our neighbor list, then return the node. This recursively works because each neighbor will in turn build itself or return the alread built version.

Originally, I had a slightly clunkier solution, but it was the exact same thing. I had defined cloneNode to either be what was already in the mapping, or a new node. At the end, I returned clone node. But in the code below, I just immediately return if it it is in the mapping, since this is a bit cleaner. Also, on neighbors, I previously checked if those neighbors were already built, and if so, used the built neighbor and pushed it into the cloneNode's neighbor list, but we can simplify add the result of every `getClone` call to the neighbor list, since getClone returns the built node if it already exists.
*/

var cloneGraph = function (firstNode) {
  const valsToNew = {}; // maps a node from the original list to the cloned list, so if we see an original node multiple times, we don't remake new nodes

  function getClone(oldNode) {
    if (oldNode.val in valsToNew) {
      return valsToNew[oldNode.val];
    }

    const cloneNode = new Node(oldNode.val);
    valsToNew[oldNode.val] = cloneNode;

    // for every neighbor, build it if it doesn't exist, or use the existing neighbor- then add them to the neighbor list
    for (const oldNeighbor of oldNode.neighbors) {
      const neighborClone = getClone(oldNeighbor);
      cloneNode.neighbors.push(neighborClone);
    }

    return cloneNode;
  }

  if (!firstNode) {
    return null;
  }

  return getClone(firstNode);
};
