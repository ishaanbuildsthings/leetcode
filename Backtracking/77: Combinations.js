// https://leetcode.com/problems/combinations/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Example:
Input: n = 4, k = 2
Output: [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
Explanation: There are 4 choose 2 = 6 total combinations.
Note that combinations are unordered, i.e., [1,2] and [2,1] are considered to be the same combination.

Detailed:
Given two integers n and k, return all possible combinations of k numbers chosen from the range [1, n].

You may return the answer in any order.
*/

// Solution, O(n!) high upper bound for time, O(k) space for the call stack. O(n!/(k!(n-k)!)) tighter upper bound.
/*
For any state, we can add all numbers bigger than the biggest one we have added, to avoid duplicates. Technically this is like doing n choose k operations hence the tighter upper bound.
*/

var combine = function (n, k) {
  const result = [];

  function backtrack(currentNums) {
    // if we reached the right amount of numbers, we add that as a combination
    if (currentNums.length === k) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }

    let biggestNumber;
    // if we have no numbers, we can add any number to the array to start
    if (currentNums.length === 0) {
      biggestNumber = 0;
    } else {
      biggestNumber = currentNums[currentNums.length - 1];
    }

    // try adding all possible other numbers
    for (let newNum = biggestNumber + 1; newNum <= n; newNum++) {
      currentNums.push(newNum);
      backtrack(currentNums);
      currentNums.pop();
    }
  }

  backtrack([]);

  return result;
};
