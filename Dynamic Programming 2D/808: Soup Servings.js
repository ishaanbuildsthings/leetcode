// https://leetcode.com/problems/soup-servings/description/
// Difficulty: Medium
// Tags: dynamic programming 2d, backtracking

// Problem
/*
There are two types of soup: type A and type B. Initially, we have n ml of each type of soup. There are four kinds of operations:

Serve 100 ml of soup A and 0 ml of soup B,
Serve 75 ml of soup A and 25 ml of soup B,
Serve 50 ml of soup A and 50 ml of soup B, and
Serve 25 ml of soup A and 75 ml of soup B.
When we serve some soup, we give it to someone, and we no longer have it. Each turn, we will choose from the four operations with an equal probability 0.25. If the remaining volume of soup is not enough to complete the operation, we will serve as much as possible. We stop once we no longer have some quantity of both types of soup.

Note that we do not have an operation where all 100 ml's of soup B are used first.

Return the probability that soup A will be empty first, plus half the probability that A and B become empty at the same time. Answers within 10-5 of the actual answer will be accepted.
*/

// Solution O(n^2) time and space, where n is the number of buckets (soup/25)
/*
We can basically simulate 4 options for each turn, and store the amount of soup for each in a dp array. I just used string keys since I didn't feel like dividing by 25 for the dp array. Given the large constraint of n, we add a stopping condition, that if n is big enough, we return 1. This is because with big enough n, the chance of finsihing soup B first becomes so low, and our answer fits within the rounding error.
*/
var soupServings = function (n) {
  if (n < 5000) return 1;

  const memo = {}; // memo['100,50'] stores the answer to the subproblem of if we have 100 of soup A and 50 of soup B

  function dp(soupA, soupB) {
    if (soupA === 0 && soupB === 0) {
      return 0.5;
    }

    if (soupA === 0) {
      return 1;
    }

    if (soupB === 0) {
      return 0;
    }

    const key = `${soupA},${soupB}`;

    if (key in memo) {
      return memo[key];
    }

    let oddsForThis = 0;

    const servings = [
      [100, 0],
      [75, 25],
      [50, 50],
      [25, 75],
    ];

    for (const [soupAServing, soupBServing] of servings) {
      const leftoverASoup = Math.max(0, soupA - soupAServing);
      const leftoverBSoup = Math.max(0, soupB - soupBServing);
      const oddsWithThisServingSet = dp(leftoverASoup, leftoverBSoup);
      oddsForThis += oddsWithThisServingSet;
    }

    oddsForThis /= 4; // divide odds of sum of children since we have 4 children

    memo[key] = oddsForThis;
    return oddsForThis;
  }

  return dp(n, n);
};
