// https://leetcode.com/problems/longest-consecutive-sequence/description/
// Difficulty: Medium

// Solution
// O(n) time and O(n) space. Use a set to store all the numbers. Iterate over the numbers and check if the number is the start of a sequence. If it is, then iterate over the set and count the sequence.
// It's important to note that the inner while loop will not add any time complexity, because it will only run once for every number. For instance [1, 2, 3, 5, 6, 7]: 2 and 3 will only run in the while loop during their sequence, and 6 and 7 will only run during the 5 sequence.

const longestConsecutive = function (nums) {
  if (nums.length === 1) return 1;
  const set = new Set();
  for (const num of nums) {
    set.add(num);
  }
  let longestSequence = 0;
  for (let num of nums) {
    // the number is the start of a sequence
    if (!set.has(num - 1)) {
      let currentSequence = 1;
      while (set.has(num + 1)) {
        currentSequence++;
        num = num + 1;
      }
      longestSequence = Math.max(longestSequence, currentSequence);
    }
  }
  return longestSequence;
};
