// https://leetcode.com/problems/count-nice-pairs-in-an-array/description/
// difficulty: Medium
// tags: math

// Problem
/*
You are given an array nums that consists of non-negative integers. Let us define rev(x) as the reverse of the non-negative integer x. For example, rev(123) = 321, and rev(120) = 21. A pair of indices (i, j) is nice if it satisfies all of the following conditions:

0 <= i < j < nums.length
nums[i] + rev(nums[j]) == nums[j] + rev(nums[i])
Return the number of nice pairs of indices. Since that number can be too large, return it modulo 109 + 7.
*/

// Solution, O(n) time and O(n) space
/*
For a pair to be nice, a-reverse(a) has to equal b-reverse(b). So, creating a mapping of a reverse diff to the # of times it occurs. Iterate through, adding to the result based on the amount of numbers that have that same reversal on the right, and delete from the mapping our seen number's reverse diff first too.
*/

function reverseNum(num) {
  let original = num;
  let reversed = 0;
  while (original > 0) {
    const lastDigit = original % 10;
    original = Math.floor(original / 10);
    reversed *= 10;
    reversed += lastDigit;
  }

  return reversed;
}

var countNicePairs = function (nums) {
  const reversalDiffs = {}; // maps reversal diff : count, for all elements

  // populate the diffs
  for (const num of nums) {
    const reversed = reverseNum(num);
    const diff = num - reversed;
    if (!(diff in reversalDiffs)) {
      reversalDiffs[diff] = 1;
    } else {
      reversalDiffs[diff]++;
    }
  }

  let result = 0;

  for (let i = 0; i < nums.length; i++) {
    const reversedNum = reverseNum(nums[i]);
    const diff = nums[i] - reversedNum;
    reversalDiffs[diff]--; // lose the diff for the current number
    result += reversalDiffs[diff];
  }

  return result % (10 ** 9 + 7);
};
