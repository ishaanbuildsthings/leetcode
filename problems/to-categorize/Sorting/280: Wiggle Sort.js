// https://leetcode.com/problems/wiggle-sort/description/
// Difficulty: Medium
// tags: bubble sort

// Solution
// O(n) time and O(1) space. Iterate over the list and swap numbers if they are not in the correct order. The wiggle is toggled after each swap. Only one swap at most is needed, because we are just toggling the parity between two numbers, so bubble sort is actually linear time!

const wiggleSort = function (nums) {
  let wiggleUp = true; // our next number needs to be higher

  for (let i = 0; i < nums.length; i++) {
    // bigger number but the wiggle is down
    if (nums[i + 1] > nums[i] && !wiggleUp) {
      const temp = nums[i];
      nums[i] = nums[i + 1];
      nums[i + 1] = temp;
    }
    // smaller number but the wiggle is up
    else if (nums[i + 1] < nums[i] && wiggleUp) {
      const temp = nums[i];
      nums[i] = nums[i + 1];
      nums[i + 1] = temp;
    }

    // toggle the wiggle
    wiggleUp = !wiggleUp;
  }
  return nums;
};
