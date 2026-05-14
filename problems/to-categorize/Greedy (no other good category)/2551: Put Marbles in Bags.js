// https://leetcode.com/problems/put-marbles-in-bags/description/
// Difficulty: Hard
// Tags: greedy

// Problem
/*
Example:
Input: weights = [1,3,5,1], k = 2
Output: 4
Explanation:
The distribution [1],[3,5,1] results in the minimal score of (1+1) + (3+1) = 6.
The distribution [1,3],[5,1], results in the maximal score of (1+3) + (5+1) = 10.
Thus, we return their difference 10 - 6 = 4.

Detailed:
You have k bags. You are given a 0-indexed integer array weights where weights[i] is the weight of the ith marble. You are also given the integer k.

Divide the marbles into the k bags according to the following rules:

No bag is empty.
If the ith marble and jth marble are in a bag, then all marbles with an index between the ith and jth indices should also be in that same bag.
If a bag consists of all the marbles with an index from i to j inclusively, then the cost of the bag is weights[i] + weights[j].
The score after distributing the marbles is the sum of the costs of all the k bags.

Return the difference between the maximum and minimum scores among marble distributions.
*/

// Solution, O(n log n) time, O(n) space
/*
Clearly only endpoints count as part of the score, so we want to minimize and maximize the endpoints. At any given point, we can make a split, meaning we get a score of the left and right. Enumerate all splits, and choose the largest and smallest k splits.

Initially I had the right idea, but was stuck on the notion that [1], [3, 5, 1] doesn't need to be handled differently, the 1 just gets counted from a left (if there are numbers on the left) and a right boundary.
*/

var putMarbles = function (weights, k) {
  const boundaries = []; // holds sums of boundaries
  for (let i = 0; i < weights.length - 1; i++) {
    const boundary = weights[i] + weights[i + 1];
    boundaries.push(boundary);
  }

  boundaries.sort((a, b) => a - b);

  if (boundaries.length === 0) return 0;

  // we have to use k-1 smaller boundaries
  let smallBoundarySum = 0;
  for (let i = 0; i < k - 1; i++) {
    smallBoundarySum += boundaries[i];
  }

  let largeBoundarySum = 0;
  const lastIndex = boundaries.length - (k - 1);
  for (let i = boundaries.length - 1; i >= lastIndex; i--) {
    largeBoundarySum += boundaries[i];
  }

  return largeBoundarySum - smallBoundarySum;
};
