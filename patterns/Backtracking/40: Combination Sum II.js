// https://leetcode.com/problems/combination-sum-ii/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Simplified:
Input: candidates = [10,1,2,7,6,1,5], target = 8
Output:
[
[1,1,6],
[1,2,5],
[1,7],
[2,6]
]

Detailed:
Given a collection of candidate numbers (candidates) and a target number (target), find all unique combinations in candidates where the candidate numbers sum to target.

Each number in candidates may only be used once in the combination.

Note: The solution set must not contain duplicate combinations.
*/

// Solution, O(2 * 2^n) time, O(n) space.
/*
We first sort all candidates, which takes n log n time. We do this to avoid duplicate solutions like [1, 2, 5] and [2, 1, 5], if we have multiples. What we need to do is, if we skip a number, skip all instances of that number.

Now, when we backtrack, we either skip the current number or use it. We backtrack on both. If we skip it, find the first different number. Our base cases are if we exceed the sum (terminate), if we equal the sum (result found + terminate), or if we considered all numbers (terminate).

If there are n candidates, and we can either keep or skip each one, we have 2^n possible solutions. Each one will also take n time to serialize, so n*2^n time.

We will also potentially use up to n space to hold an invalid solution in currentNums. The callstack can also be depth n.
*/

var combinationSum2 = function (candidates, target) {
  /*
    we have to sort the candidates, otherwise we might get duplicates solutions like [1, 2, 5] and [2, 1, 5], if we have multiples. what we need to do is, if we skip a number, skip all instances of that number
    */
  candidates.sort((a, b) => a - b);

  const result = [];

  // index is the index of the number we are considering, we can either use or skip it
  function backtrack(currentNums, currentSum, index) {
    // if our sum is ever too big, we cannot go down anymore, since all candidates are positive
    if (currentSum > target) {
      return;
    }

    // if we have the exact sum, we have a solution, and since 0 is not allowed as a candidate, we can terminate
    if (currentSum === target) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }

    // if we have gone too far, we can terminate (after we checked if we got a solution)
    if (index === candidates.length) {
      return;
    }

    // use the current number
    currentNums.push(candidates[index]);
    backtrack(currentNums, currentSum + candidates[index], index + 1);
    currentNums.pop();

    // skip the current number

    // j will iterate to find the next candidate that is a different number
    let j;
    for (j = index; j < candidates.length; j++) {
      if (candidates[j] !== candidates[index]) {
        break; // j is the first time we have a different candidate
      }
    }

    backtrack(currentNums, currentSum, j);
  }

  backtrack([], 0, 0);

  return result;
};
