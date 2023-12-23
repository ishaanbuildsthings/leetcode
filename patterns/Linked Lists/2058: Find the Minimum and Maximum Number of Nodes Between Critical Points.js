// https://leetcode.com/problems/find-the-minimum-and-maximum-number-of-nodes-between-critical-points/description/
// difficulty: Medium
// tags: linked list

// Problem
/*
A critical point in a linked list is defined as either a local maxima or a local minima.

A node is a local maxima if the current node has a value strictly greater than the previous node and the next node.

A node is a local minima if the current node has a value strictly smaller than the previous node and the next node.

Note that a node can only be a local maxima/minima if there exists both a previous node and a next node.

Given a linked list head, return an array of length 2 containing [minDistance, maxDistance] where minDistance is the minimum distance between any two distinct critical points and maxDistance is the maximum distance between any two distinct critical points. If there are fewer than two critical points, return [-1, -1].
*/

// Solution, O(n) time and O(n) space
// * Solution 2 - Currently we use n space for both the callstack and the critical points. The callstack could be constant space by iteratively looping and storing a prevValue pointer. We also don't need to store all critical points. We can just cache the very first critical point (for max distance), and the previous critical point (to compare adjacent pairs), resulting in O(1) space.
/*
We iterate through each node, seeing if it is a minimum or maximum point. To find the max distance, we check the distance between the first and last critical points. To find the smallest distance, we compare each adjacent pair.
*/

var nodesBetweenCriticalPoints = function (head) {
  const criticalPoints = [];

  function recurse(node, prevVal, i) {
    // if we are an ending node, we cannot be a critical point
    if (!node.next) {
      return;
    }

    // if we are bigger than both, or smaller than both, add to the critical points
    if (
      (node.val > prevVal && node.val > node.next.val) ||
      (node.val < prevVal && node.val < node.next.val)
    ) {
      criticalPoints.push(i);
    }

    recurse(node.next, node.val, i + 1);
  }

  recurse(head, NaN, 0); // prev val is NaN so the comparisons always fail for the firsst node

  if (criticalPoints.length < 2) {
    return [-1, -1];
  }

  const maxDistance =
    criticalPoints[criticalPoints.length - 1] - criticalPoints[0];
  let minDistance = Infinity;
  for (let i = 0; i < criticalPoints.length - 1; i++) {
    minDistance = Math.min(
      minDistance,
      criticalPoints[i + 1] - criticalPoints[i]
    );
  }

  return [minDistance, maxDistance];
};
