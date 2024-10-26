// https://leetcode.com/problems/maximal-network-rank/description/
// Difficulty: Medium
// Tags: Graphs

// Problem
/*
There is an infrastructure of n cities with some number of roads connecting these cities. Each roads[i] = [ai, bi] indicates that there is a bidirectional road between cities ai and bi.

The network rank of two different cities is defined as the total number of directly connected roads to either city. If a road is directly connected to both cities, it is only counted once.

The maximal network rank of the infrastructure is the maximum network rank of all pairs of different cities.

Given the integer n and the array roads, return the maximal network rank of the entire infrastructure.
*/

// Solution, O(E + V^2) time, O(E) space
/*
What I did was first generate all edges in a hashmap which took O(E) time and space. Then, I tried every pair of nodes which took O(V^2) time. I thought you could just do a greedy solution with the two nodes with the most edges but maybe this does not work.
*/

/**
 * @param {number} n
 * @param {number[][]} roads
 * @return {number}
 */
var maximalNetworkRank = function (n, roads) {
  const nodes = {};
  for (let i = 0; i < roads.length; i++) {
    const [from, to] = roads[i];
    if (!(from in nodes)) {
      nodes[from] = [to];
    } else {
      nodes[from].push(to);
    }

    if (!(to in nodes)) {
      nodes[to] = [from];
    } else {
      nodes[to].push(from);
    }
  }

  let result = 0;

  for (let node = 0; node < n - 1; node++) {
    for (let secondNode = node + 1; secondNode < n; secondNode++) {
      const firstSize = nodes[node] ? nodes[node].length : 0;
      const secondSize = nodes[secondNode] ? nodes[secondNode].length : 0;
      let totalSize;
      if (nodes[node] && nodes[node].includes(secondNode)) {
        totalSize = firstSize + secondSize - 1;
      } else {
        totalSize = firstSize + secondSize;
      }
      result = Math.max(result, totalSize);
    }
  }

  return result;
};
