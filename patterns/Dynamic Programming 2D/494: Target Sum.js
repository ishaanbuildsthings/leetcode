// https://leetcode.com/problems/target-sum/description/
// Difficulty: Medium
// tags: dynamic programming 2d, bottom up recursion

// Problem
/*
Example:

Input: nums = [1,1,1,1,1], target = 3
Output: 5
Explanation: There are 5 ways to assign symbols to make the sum of nums be target 3.
-1 + 1 + 1 + 1 + 1 = 3
+1 - 1 + 1 + 1 + 1 = 3
+1 + 1 - 1 + 1 + 1 = 3
+1 + 1 + 1 - 1 + 1 = 3
+1 + 1 + 1 + 1 - 1 = 3

Detailed:

You are given an integer array nums and an integer target.

You want to build an expression out of nums by adding one of the symbols '+' and '-' before each integer in nums and then concatenate all the integers.

For example, if nums = [2, 1], you can add a '+' before 2 and a '-' before 1 and concatenate them to build the expression "+2-1".
Return the number of different expressions that you can build, which evaluates to target.
*/

// Solution, bottom up tabulation, O(n * unique sum combinations) time and O(n * unique sum combinations) space, I think. I don't see how to define these unique sum combinations.

/*
To solve the amount of ways we can reach the target with some array, start with the sub problem of just one index. Consider only the last 1. We cannot reach a target of 3 in any way, but we do know we can make a sum of 1 in one way, and a sum of -1 in one way. Now, consider the prior 1. We can make a sum of 2 in one way, a sum of 0 in two ways, and a sum of -2 in one way. We just repeat this process, then see how many ways we can make the target from the beginning of the solution.

The point of the dp is we do get to memoize a lot of data, instead of pure backtracking which is 2^n. For instance +1 -1 +1 -1 could memoize the last 2 cells as there are two ways to make 0. -1 +1 +1 -1 could also use this for instance.

We store a dp of length n, and for each dp, we store a hashmap of size (unique sum combinations). I have no idea what that is lol.
*/

var findTargetSumWays = function (nums, target) {
  /*
    1, 1, 1, 1, 1

    at the last 1, we are at index 4
    our possible sums are 1, and -1, neither of which reach the target

    at the second to last 1, we are at index 3
    we can add +1 to all sums on the right, and -1 to all sums on the right
    so we can make a 2 in one way, a 0 in two ways, and a -2 in one way

    */

  /*
    the dp stores a mapping for each index, which maps a sum you can make at that index to how many ways you can make it
    */
  const dp = new Array(nums.length).fill().map(() => ({}));

  // seed the dp with the last value, we also need to handle the edge case if it is a 0
  const lastMapping = dp[dp.length - 1];
  const lastValue = nums[nums.length - 1];
  if (lastValue === 0) {
    lastMapping[lastValue] = 2;
  } else {
    lastMapping[lastValue] = 1;
    lastMapping[-1 * lastValue] = 1;
  }

  // iterate backwards, starting at the second to last value
  for (let i = dp.length - 2; i >= 0; i--) {
    const val = nums[i];
    const negVal = -1 * val;
    const mapping = dp[i];

    const nextMapping = dp[i + 1];
    for (const sumType in nextMapping) {
      const occurencesOfThatSumType = nextMapping[sumType];
      const valueWithAdd = val + Number(sumType);
      const valueWithSubtract = negVal + Number(sumType);
      if (valueWithAdd in mapping) {
        mapping[valueWithAdd] += occurencesOfThatSumType;
      } else {
        mapping[valueWithAdd] = occurencesOfThatSumType;
      }

      if (valueWithSubtract in mapping) {
        mapping[valueWithSubtract] += occurencesOfThatSumType;
      } else {
        mapping[valueWithSubtract] = occurencesOfThatSumType;
      }
    }
  }

  return dp[0][target] === undefined ? 0 : dp[0][target];
};
