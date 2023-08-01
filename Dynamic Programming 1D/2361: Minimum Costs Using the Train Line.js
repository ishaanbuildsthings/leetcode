// https://leetcode.com/problems/minimum-costs-using-the-train-line/description/
// Difficulty: Hard
// Tags: state machine

// Problem
/*
Note: Seeing the picture helps a lot.

A train line going through a city has two routes, the regular route and the express route. Both routes go through the same n + 1 stops labeled from 0 to n. Initially, you start on the regular route at stop 0.

You are given two 1-indexed integer arrays regular and express, both of length n. regular[i] describes the cost it takes to go from stop i - 1 to stop i using the regular route, and express[i] describes the cost it takes to go from stop i - 1 to stop i using the express route.

You are also given an integer expressCost which represents the cost to transfer from the regular route to the express route.

Note that:

There is no cost to transfer from the express route back to the regular route.
You pay expressCost every time you transfer from the regular route to the express route.
There is no extra cost to stay on the express route.
Return a 1-indexed array costs of length n, where costs[i] is the minimum cost to reach stop i from stop 0.

Note that a stop can be counted as reached from either route.
*/

// Solution O(n) time O(1) space
/*
At first, I wrote a DP solution, but then I kind of realized I misread the question, and we needed an array of costs, not just a minimum cost. The dp I wrote made it hard to solve this but I realized that we can just use a state machine to solve this. Pretty straightforward... I hope Citadel asks me this :)
*/

var minimumCosts = function (regular, express, expressCost) {
  let minToReachReg = 0;
  let minToReachExpress = expressCost;

  const result = [];

  for (let i = 0; i < regular.length; i++) {
    // the minimum to reach the regular is either the previous minimum express, plus the new express cost (where we then transfer to regular for free), or the previous minimum regular, plus the regular cost
    const newMinToReachReg = Math.min(
      minToReachExpress + express[i],
      minToReachReg + regular[i]
    );
    // the min to reach express is either the previous min to reach reg, plus the regular cost, plus the transfer cost, or the previous express plus the express cost
    const newMinToReachExpress = Math.min(
      minToReachReg + regular[i] + expressCost,
      minToReachExpress + express[i]
    );

    minToReachReg = newMinToReachReg;
    minToReachExpress = newMinToReachExpress;
    result.push(Math.min(minToReachReg, minToReachExpress));
  }

  return result;
};
