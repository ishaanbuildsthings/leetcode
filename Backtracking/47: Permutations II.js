// https://leetcode.com/problems/permutations-ii/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Example:
Input: nums = [1,1,2]
Output:
[[1,1,2],
 [1,2,1],
 [2,1,1]]

Given a collection of numbers, nums, that might contain duplicates, return all possible unique permutations in any order.
*/

// Solution, O(n*n!) time and O(n) space
/*
At a given state, we can choose any number, if we haven't chosen all of that number. So we maintain a frequency mapping of how many numbers we have chosen. There are n! possible permutations and each takes n time to serialize, so n*n!. There are repeats, so we could derive a better upper bound.

For space, we have a callstack depth of n, and a mapping of n numbers, so O(n) space.
*/

var permuteUnique = function (nums) {
  const maxAllowed = {}; // maps a number to the max occurences it will have
  for (const num of nums) {
    if (num in maxAllowed) {
      maxAllowed[num]++;
    } else {
      maxAllowed[num] = 1;
    }
  }

  const uniqueNums = Array.from(new Set(nums)); // helps us backtrack to adjacent states as we don't want to add the same number to the same state multiple times, i.e. currentNums = [1, 1] and we have two more 1s we could use, we only want to consider [1, 1, 1] once

  const result = [];

  function backtrack(currentNums, currentFrequencies) {
    if (currentNums.length === nums.length) {
      result.push(JSON.parse(JSON.stringify(currentNums)));
      return;
    }

    for (const num of uniqueNums) {
      if (currentFrequencies[num] === maxAllowed[num]) {
        continue;
      }
      currentNums.push(num);
      currentFrequencies[num]++;
      backtrack(currentNums, currentFrequencies);
      currentNums.pop();
      currentFrequencies[num]--;
    }
  }

  const currentFrequencies = {};
  for (const num of nums) {
    currentFrequencies[num] = 0;
  }

  backtrack([], currentFrequencies);

  return result;
};
