// https://leetcode.com/problems/coin-path/description/
// Difficulty: Hard
// Tags: dynamic programming 1d

// Problem
/*
You are given an integer array coins (1-indexed) of length n and an integer maxJump. You can jump to any index i of the array coins if coins[i] != -1 and you have to pay coins[i] when you visit index i. In addition to that, if you are currently at index i, you can only jump to any index i + k where i + k <= n and k is a value in the range [1, maxJump].

You are initially positioned at index 1 (coins[1] is not -1). You want to find the path that reaches index n with the minimum cost.

Return an integer array of the indices that you will visit in order so that you can reach index n with the minimum cost. If there are multiple paths with the same cost, return the lexicographically smallest such path. If it is not possible to reach index n, return an empty array.

A path p1 = [Pa1, Pa2, ..., Pax] of length x is lexicographically smaller than p2 = [Pb1, Pb2, ..., Pbx] of length y, if and only if at the first j where Paj and Pbj differ, Paj < Pbj; when no such j exists, then x < y.
*/

// Solution, O(n*jumps) time, O(n) space
/*
Notably in this problem, we need the path not just the cost. Because of this, in the memo, we both store the cost (to determine when a path is good), but also a path of the subproblem. I also start at max jumps first, to handle the case that if paths have the same cost we want the lexicographically smallest path.

For each [l:] subproblem, we do up to k jumps. We also then reprocess the array which is at most length k.

I also converted the indices to 1-indexing at the end and handled some edge cases which is why the return statement looks weird.
*/

var cheapestJump = function (coins, maxJump) {
  // memo[l] tells us the answer to the subproblem [l:], which is [smallest path, cost for that path]
  const memo = new Array(coins.length).fill(-1);

  function dp(l) {
    if (l >= coins.length - 1) {
      return [[], 0];
    }

    if (memo[l] !== -1) {
      return memo[l];
    }

    let smallestPriceFromHere = Infinity;
    let pathAnswer = [];

    // for every jump up to max jump away, try that, see what is the minimum
    for (let jump = maxJump; jump >= 1; jump--) {
      const cell = coins[l + jump];
      let minPriceIfThisSpot = Infinity;

      if (cell !== -1) {
        minPriceIfThisSpot = cell + dp(l + jump)[1];
      }
      if (
        minPriceIfThisSpot <= smallestPriceFromHere &&
        minPriceIfThisSpot !== Infinity
      ) {
        pathAnswer = [l + jump, ...dp(l + jump)[0]];
        smallestPriceFromHere = minPriceIfThisSpot;
      }
    }

    memo[l] = [pathAnswer, smallestPriceFromHere];
    return [pathAnswer, smallestPriceFromHere];
  }

  const result = [1, ...dp(0)[0].map((e) => e + 1)];
  if (result.length === 1 && coins.length !== 1) {
    return [];
  }
  return result;
};
