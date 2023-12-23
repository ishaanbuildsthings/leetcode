// https://leetcode.com/problems/count-number-of-bad-pairs/description/
// Difficulty: Medium

// Problem
/*
Example:
Input: nums = [4,1,3,3]
Output: 5
Explanation: The pair (0, 1) is a bad pair since 1 - 0 != 1 - 4.
The pair (0, 2) is a bad pair since 2 - 0 != 3 - 4, 2 != -1.
The pair (0, 3) is a bad pair since 3 - 0 != 3 - 4, 3 != -1.
The pair (1, 2) is a bad pair since 2 - 1 != 3 - 1, 1 != 2.
The pair (2, 3) is a bad pair since 3 - 2 != 3 - 3, 1 != 0.
There are a total of 5 bad pairs, so we return 5.

Detailed:
You are given a 0-indexed integer array nums. A pair of indices (i, j) is a bad pair if i < j and j - i != nums[j] - nums[i].

Return the total number of bad pairs in nums.
*/

// Solution, O(n) time and O(n) space

/*
Map the occurences of diffs to how many times they occur. A diff is the surplus of a number to its index. Iterate through numbers, finding good pairs, meaning pairs which have the same diff. a good pair is one where the difference in indices equals the difference in numbers. so imagine we had a 105 at index 100. we would need for instance a 155 at index 150. this also means that a good pair is one where the difference between a value and index is the same for each number. so we look through numbers, find their diff, and see how many of that diff remain, adding good pairs. Then we subtract good pairs from total pairs to get bad pairs.

This could be done in one pass too, where we see how many of a certain diff we already had.
*/
var countBadPairs = function (nums) {
  const diffs = {}; // maps a diff (the surplus of a number to its index), to how many times it occurs.
  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    const diff = num - i;
    if (diff in diffs) {
      diffs[diff]++;
    } else {
      diffs[diff] = 1;
    }
  }

  let goodPairs = 0;
  // iterate through numbers, finding good pairs, meaning pairs which have the same diff. a good pair is one where the difference in indices equals the difference in numbers. so imagine we had a 105 at index 100. we would need for instance a 155 at index 150. this also means that a good pair is one where the difference between a value and index is the same for each number. so we look through numbers, find their diff, and see how many of that diff remain, adding good pairs.
  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    const diff = num - i;
    diffs[diff]--; // remove the current diff
    const sameDiffsRemaining = diffs[diff];
    goodPairs += sameDiffsRemaining;
  }

  const totalPairs = (nums.length * (nums.length - 1)) / 2;
  return totalPairs - goodPairs; // return bad pairs
};
