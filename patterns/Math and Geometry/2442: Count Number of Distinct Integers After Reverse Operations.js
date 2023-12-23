// https://leetcode.com/problems/count-number-of-distinct-integers-after-reverse-operations/description/
// Difficulty: Medium

// Problem
/*
You are given an array nums consisting of positive integers.

You have to take each integer in the array, reverse its digits, and add it to the end of the array. You should apply this operation to the original integers in nums.

Return the number of distinct integers in the final array.
*/

// Solution, O(n) time, O(n) space, just reverse the numbers and add to a set

var countDistinctIntegers = function (nums) {
  const resultSet = new Set();
  for (const num of nums) {
    resultSet.add(num);
  }

  function reverseNum(num) {
    let result = 0;
    let current = num;
    while (current > 0) {
      const lastDigit = current % 10;
      result *= 10;
      result += lastDigit;
      current = Math.floor(current / 10);
    }
    return result;
  }

  for (let i = 0; i < nums.length; i++) {
    const num = nums[i];
    const reversedNum = reverseNum(num);
    resultSet.add(reversedNum);
  }

  return resultSet.size;
};
