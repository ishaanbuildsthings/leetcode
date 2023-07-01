// https://leetcode.com/problems/fair-distribution-of-cookies/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
You are given an integer array cookies, where cookies[i] denotes the number of cookies in the ith bag. You are also given an integer k that denotes the number of children to distribute all the bags of cookies to. All the cookies in the same bag must go to the same child and cannot be split up.

The unfairness of a distribution is defined as the maximum total cookies obtained by a single child in the distribution.

Return the minimum unfairness of all distributions.
*/

// Solution, O(k^n) time and O(n + k) space. Backtracking, I didn't have an intuition for it, I just saw the low constraints.
/*
Create k boxes for each child. Backtrack across n cookies, so the max callstack depth is n. For each cookie, try adding it to a different child. We could also maintain sums for each children's cookie count, but I just recomputed the sums at the end which is still O(n) time anyway. An optimization could be to terminate early if we don't have at least 1 cookie for every child, as this is always more optimal than not, since k <= n.
*/

var distributeCookies = function (cookies, k) {
  // there are k children and each receives various cookies
  const children = new Array(k).fill().map(() => []);

  let smallestUnfairness = Infinity;

  function backtrack(i) {
    // stop when we have considered all cookies
    if (i === cookies.length) {
      let largestMaxInThisArrangement = -Infinity;
      for (const child of children) {
        const sum = child.reduce((acc, val) => acc + val, 0);
        largestMaxInThisArrangement = Math.max(
          largestMaxInThisArrangement,
          sum
        );
      }
      smallestUnfairness = Math.min(
        smallestUnfairness,
        largestMaxInThisArrangement
      );
      return;
    }

    for (const child of children) {
      child.push(cookies[i]);
      backtrack(i + 1);
      child.pop();
    }
  }

  backtrack(0);

  return smallestUnfairness;
};
