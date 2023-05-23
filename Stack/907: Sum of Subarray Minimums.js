// https://leetcode.com/problems/sum-of-subarray-minimums/description/
// Difficulty: Medium
// tags: monotonic stack

// Problem
/*
Simplified: Given an array, find the sum of the minimums of all subarrays.
*/

// Solution, O(n) time and O(n) space
/*
Find the range for which a given number is the minimum. Maintain a monotonically increasing stack. Consider these elements: 1, 4, 9. None of them are certain yet of the entire range for which they are the minimum, because they could all have more bigger numbers. But then say we add a 6:

[1, 4, 9, 6

The 6 is smaller than the 9, so we know the 9 has met its bottleneck on the right. We also know the 9 has met its bottleneck on the left, because we are monotonically increasing. We actually need to store tuples in the stack to track the indices however:

[[0,1], [1,4], [2,9], [3,6]

So here, the number 9 gets stopped at index 3, and index 1 from the left. This makes the range for which it is the minimum to be [2,2]. We can then calculate how many subarrays it is a part of, based on the index and the indices in the range. The number of subarrays is the number of left starts (from the left part of the range to the index itself, inclusive) times the number of right ends. We add this to our total sum. In the actual code below I created a mapping but it isn't needed for this. We pop from the stack and keep going. If there are leftover monotonically increasing elements in the stack, we handle those as well.
*/

var sumSubarrayMins = function (arr) {
  const MOD = 10 ** 9 + 7;
  const mapping = {}; // maps an index to the range it is in the minimum, going right can see the same number, but not left
  const stack = []; // contains tuples [index, number], we need the index so we put the index in mapping, which is needed to determine all the subarrays
  for (let i = 0; i < arr.length; i++) {
    while (stack.length > 0 && arr[i] < stack[stack.length - 1][1]) {
      const beatenTuple = stack[stack.length - 1];
      const index = beatenTuple[0];
      const untilRight = i - 1;
      let untilLeft;
      if (stack.length >= 2) {
        untilLeft = stack[stack.length - 2][0] + 1;
      } else {
        untilLeft = 0;
      }
      mapping[index] = [untilLeft, untilRight];
      stack.pop();
    }
    stack.push([i, arr[i]]);
  }

  for (let i = 0; i < stack.length; i++) {
    const tuple = stack[i];
    const index = tuple[0];
    const untilRight = arr.length - 1; // we are allowed to keep going right even if the elements are the same
    let untilLeft;
    if (i === 0) {
      untilLeft = 0;
    } else {
      untilLeft = stack[i - 1][0] + 1;
    }
    mapping[index] = [untilLeft, untilRight];
  }

  let totalSum = 0;

  for (const key in mapping) {
    const index = Number(key);
    const tuple = mapping[key];
    const left = tuple[0];
    const right = tuple[1];
    const validLefts = index - left + 1;
    const validRights = right - index + 1;
    const totalSubarrays = validLefts * validRights;
    const minContribution = arr[index] * totalSubarrays;
    totalSum += minContribution;
  }

  return totalSum % MOD;
};

// n^2
// var sumSubarrayMins = function(arr) {
//     // create an nxn table with null values, where table[i][j] represents the minimum for the subarray from i to j
//     const table = new Array(arr.length).fill().map(() => new Array(arr.length).fill(null));

//     // populate the known minimums for subarrays of length 1
//     for (let i = 0; i < arr.length; i++) {
//         table[i][i] = arr[i];
//     }

//     console.log(table);

//     // iterate over all possible subarrays
//     for (let i = 0; i < arr.length; i++) {
//         for (let j = i; j < arr.length; j++) {
//             if (i !== j) table[i][j] = Math.min(table[i][j-1], arr[j]);
//         }
//     }

//     let totalSum = 0;

//     for (let i = 0; i < arr.length; i++) {
//         for (let j = i; j < arr.length; j++) {
//             totalSum += table[i][j];
//             totalSum = totalSum % (10**9 + 7);
//         }
//     }

//     return totalSum % (Math.pow(10, 9) + 7);
// };
