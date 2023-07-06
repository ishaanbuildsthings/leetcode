// https://leetcode.com/problems/maximize-score-after-n-operations/description/
// Difficulty: Hard
// tags: dynamic programming 2d, bit manipulation, bit mask

// Problem
/*
Example:

Input: nums = [3,4,6,8]
Output: 11
Explanation: The optimal choice of operations is:
(1 * gcd(3, 6)) + (2 * gcd(4, 8)) = 3 + 8 = 11

Detailed:
You are given nums, an array of positive integers of size 2 * n. You must perform n operations on this array.

In the ith operation (1-indexed), you will:

Choose two elements, x and y.
Receive a score of i * gcd(x, y).
Remove x and y from nums.
Return the maximum score you can receive after performing n operations.

The function gcd(x, y) is the greatest common divisor of x and y.
*/

// Solution 1, dp bitmask, O(2^n * n^3 * log A) time, O(2^n * n) space, to store 2^n bitmasks, here I consider a single int of size n because we need the number of bits in the number to be bigger than the length of the array
// * Solution 2, slower version that is the exact same but uses string serialization
/*
Given the array is size <= 14, I expected an exponential solution. The best seemed to be 2^n states, where we memoize states based on what has occured. We have 2^n states because elements can either appear or not appear. For a given state, we iterate through n^2 pairs, and create a new state based on what we remove. Creating the new state takes n time, either to update the bitmask, or to create a new array with the stringified array solution. The bitmask has a 0 if an element hasn't been picked, and a 1 if it has. For each pair, we also find the GCD which is log(10**6) (max size for any number) time. So we get 2^n * n^3 * log A, where n is the length of the array.
*/

function gcd(a, b) {
  while (b !== 0) {
    const temp = a;
    a = b;
    b = temp % b;
  }
  return a;
}

var maxScore = function (nums) {
  const memo = {}; // maps a bitmask, which represents which numbers have been picked or not, 0=not picked, 1=picked, to the solution for that dp problem

  const TOTAL_REMOVALS_TO_MAKE = nums.length / 2;

  function dp(mask, removalsMade) {
    if (mask in memo) {
      return memo[mask];
    }

    // base case, we removed everything
    if (removalsMade === TOTAL_REMOVALS_TO_MAKE) {
      return 0;
    }

    let scoreForThisDp = 0;

    // iterate across all pairs of valid numbers to remove, as per the mask
    for (let i = 0; i < nums.length - 1; i++) {
      // check if we already used the ith (0-index) number, by seeing if the ith bit is a 1
      if ((mask >> i) & (1 === 1)) {
        continue;
      }
      for (let j = i + 1; j < nums.length; j++) {
        if ((mask >> j) & (1 === 1)) {
          continue;
        }
        /* here, both numbers are unpicked as per the mask */

        // pick those numbers by setting the mask
        const maskWithFirstIndex = mask | (1 << i);
        const maskWithSecondIndex = maskWithFirstIndex | (1 << j);
        const scoreForRemovingTheseNumbers =
          (removalsMade + 1) * gcd(nums[i], nums[j]);
        scoreForThisDp = Math.max(
          scoreForThisDp,
          scoreForRemovingTheseNumbers +
            dp(maskWithSecondIndex, removalsMade + 1)
        );
      }
    }

    memo[mask] = scoreForThisDp;
    return scoreForThisDp;
  }

  return dp(0, 0);
};

// Solution 2, same thing but with string serialization, same complexities

var maxScore = function (nums) {
  function gcd(a, b) {
    while (b !== 0) {
      const temp = a;
      a = b;
      b = temp % b;
    }
    return a;
  }

  const memo = {}; // maps a serialized array to the optimal solution in that

  const INITIAL_LENGTH = nums.length;

  // whenever a dp call creates a new dp call, we pass a copy of an array
  function dp(currentArr) {
    const removalsMade = (INITIAL_LENGTH - currentArr.length) / 2;
    const removalNumber = removalsMade + 1;

    const serializedArray = JSON.stringify(currentArr);
    if (memo[serializedArray] !== undefined) {
      return memo[serializedArray];
    }

    // base case, if we have only two elements left
    if (currentArr.length === 2) {
      const [a, b] = currentArr;
      return removalNumber * gcd(a, b);
    }

    let maxScore = 0;

    // get the highest score based on removing any two numbers
    for (let i = 0; i < currentArr.length - 1; i++) {
      for (let j = i + 1; j < currentArr.length; j++) {
        const scoreFromRemovingThoseTwoNumbers =
          removalNumber * gcd(currentArr[i], currentArr[j]);
        const newArr = [...currentArr];
        newArr.splice(j, 1);
        newArr.splice(i, 1);
        maxScore = Math.max(
          maxScore,
          scoreFromRemovingThoseTwoNumbers + dp(newArr)
        );
      }
    }

    memo[serializedArray] = maxScore;
    return maxScore;
  }

  return dp(nums);
};
