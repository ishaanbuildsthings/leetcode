// https://leetcode.com/problems/arithmetic-subarrays/description/
// Difficulty: Medium
// tags: math

// Problem
/*
Simplified:
We have an array of numbers, and queries, where a query represents some subarray of the numbers. A query wants to know if, given some subarray, can we rearrange those numbers to form an arithmetic sequence.
Detailed:
A sequence of numbers is called arithmetic if it consists of at least two elements, and the difference between every two consecutive elements is the same. More formally, a sequence s is arithmetic if and only if s[i+1] - s[i] == s[1] - s[0] for all valid i.

For example, these are arithmetic sequences:
*/

// Solution, O(query length * query length range) time, O(query length range) space for the set
/*
I'm not sure if there is something better than brute force, I thought DP at first but low constraints led me to brute force.

For a given range, add all the numbers to a set, tracking the min and max. Based on the min, max, and length of that region, we can determine what the difference should be. Using that difference, check the presence of all numbers in the set, updating the result as needed.
*/

var checkArithmeticSubarrays = function (nums, l, r) {
  const result = [];

  for (let i = 0; i < l.length; i++) {
    // subarray ranges from [l[i], r[i]]
    const numSet = new Set();
    let min = Infinity;
    let max = -Infinity;
    for (let j = l[i]; j <= r[i]; j++) {
      const num = nums[j];
      min = Math.min(min, num);
      max = Math.max(max, num);
      numSet.add(num);
    }

    // edge case, if all the numbers are the same the difference is 0, and we would never exit the loop
    if (min === max) {
      result.push(true);
      continue;
    }

    // based on the min, max, and number of elements, we can calculate the expected difference between elements
    const length = r[i] - l[i] + 1;
    const difference = max - min;
    const spaces = length - 1;
    const differenceBetweenNumbers = difference / spaces;

    let badSequenceFound = false;
    for (let num = min; num <= max; num += differenceBetweenNumbers) {
      if (!numSet.has(num)) {
        badSequenceFound = true;
        result.push(false);
        break;
      }
    }

    if (!badSequenceFound) {
      result.push(true);
    }
  }

  return result;
};
