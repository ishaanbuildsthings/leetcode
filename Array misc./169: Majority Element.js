// https://leetcode.com/problems/majority-element/description/
// Difficulty: Easy
// tags: none

// Solution
// O(n) time and O(1) space
// Track the current majority number and a count of how much "surplus" that number has. When that number comes up, increase the surplus, when a different number comes up, decrease it. If the surplus is lost, whatever new element we have gets set to the majority. This works because we know there is a majority element, and even if every other number tried to decrease its surplus, it would still come out as the final number.

const majorityElement = function (nums) {
  let count = 0;
  let currentNum = nums[0];
  for (let num of nums) {
    if (num === currentNum) {
      count++;
    } else {
      count--;
      if (count < 0) {
        currentNum = num;
        count = 0;
      }
    }
  }
  return currentNum;
};
