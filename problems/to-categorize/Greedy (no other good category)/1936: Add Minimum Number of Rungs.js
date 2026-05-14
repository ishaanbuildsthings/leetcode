// https://leetcode.com/problems/add-minimum-number-of-rungs/description/
// Difficulty: Medium
// tags: greedy

// Problem
/*
Example:

Input: rungs = [1,3,5,10], dist = 2
Output: 2
Explanation:
You currently cannot reach the last rung.
Add rungs at heights 7 and 8 to climb this ladder.
The ladder will now have rungs at [1,3,5,7,8,10].

Detailed:

You are given a strictly increasing integer array rungs that represents the height of rungs on a ladder. You are currently on the floor at height 0, and you want to reach the last rung.

You are also given an integer dist. You can only climb to the next highest rung if the distance between where you are currently at (the floor or on a rung) and the next rung is at most dist. You are able to insert rungs at any positive integer height if a rung is not already there.

Return the minimum number of rungs that must be added to the ladder in order for you to climb to the last rung.
*/

// Solution, O(n) time, O(1) space, just greedily add rungs as needed

var addRungs = function (rungs, dist) {
  rungs[-1] = 0; // helps with the loop

  let currentIndexPos = -1;
  let result = 0;
  while (currentIndexPos !== rungs.length - 1) {
    // if we can reach the next step, do so
    if (rungs[currentIndexPos + 1] - rungs[currentIndexPos] <= dist) {
      currentIndexPos++;
    }

    // if we cannot reach the next step, greedily add rungs until we can
    else {
      const rungsNeeded = Math.floor(
        (rungs[currentIndexPos + 1] - 1 - rungs[currentIndexPos]) / dist
      );
      result += rungsNeeded;
      currentIndexPos++;
    }
  }

  return result;
};
