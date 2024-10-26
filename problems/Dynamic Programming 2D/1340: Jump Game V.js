// https://leetcode.com/problems/jump-game-v/description/
// Difficulty: Hard
// Tags: Dynamic Programming 2d

// Problem
/*
Given an array of integers arr and an integer d. In one step you can jump from index i to index:

i + x where: i + x < arr.length and  0 < x <= d.
i - x where: i - x >= 0 and  0 < x <= d.
In addition, you can only jump from index i to index j if arr[i] > arr[j] and arr[i] > arr[k] for all indices k between i and j (More formally min(i, j) < k < max(i, j)).

You can choose any index of the array and start jumping. Return the maximum number of indices you can visit.

Notice that you can not jump outside of the array at any time.
*/

// Solution, O(n^2) time, O(n) space
/*
Since we can only jump to strictly decreasing spots, there's no back and forth jumping. Pretty straightforward dp, for each spot we try all possible jumps. At most we compute n values, each value checks n jumps. Since we don't have a defined starting location, we also loop through each one, but since the values are memoized this doesn't add to time complexity.
*/

var maxJumps = function (arr, d) {
  // memo[i] contains the answer to the problem as if we started at that index
  const memo = new Array(arr.length).fill(-1);

  function dp(i) {
    if (memo[i] !== -1) {
      return memo[i];
    }

    let resultForThis = 1; // worst case we can only visit our own index

    // try jumping left
    for (let jumps = 1; jumps <= d; jumps++) {
      const indexToJumpTo = i - jumps;
      if (indexToJumpTo < 0) {
        break;
      }

      // as soon as we find a step too big, we cannot go left of that
      if (arr[indexToJumpTo] >= arr[i]) {
        break;
      }
      const ifJumpHere = 1 + dp(indexToJumpTo);
      resultForThis = Math.max(resultForThis, ifJumpHere);
    }

    // try jumping right
    for (let jumps = 1; jumps <= d; jumps++) {
      const indexToJumpTo = i + jumps;

      if (indexToJumpTo >= arr.length) {
        break;
      }

      // as soon as we find a step too big, we cannot go left of that
      if (arr[indexToJumpTo] >= arr[i]) {
        break;
      }
      const ifJumpHere = 1 + dp(indexToJumpTo);
      resultForThis = Math.max(resultForThis, ifJumpHere);
    }

    memo[i] = resultForThis;
    return resultForThis;
  }

  let result = 1;
  for (let i = 0; i < arr.length; i++) {
    const ifStartHere = dp(i);
    result = Math.max(result, ifStartHere);
  }

  return result;
};
