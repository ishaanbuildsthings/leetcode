// https://leetcode.com/problems/3sum-closest/description/
// Difficulty: Medium
// tags: two pointers
// helper: helped by 167: Two Sum II - Input Array Is Sorted, and closely related to 15: 3Sum

// Solution
// O(n^2) time and O(1) space. First sort the array, which allows us to use a 2-pointer 2sum solution as we need to be able to decrement and increment things. Iterate over the array, and establish a twoSumTa\rget. For each of those targets, do a 2-sum, and update the closestNumber.

const threeSumClosest = function (nums, target) {
  nums.sort((a, b) => a - b);

  let closestNumber = Number.POSITIVE_INFINITY;

  // iterate over numbers, O(n)
  for (let i = 0; i < nums.length; i++) {
    // optimization
    if (i > 0 && nums[i] === nums[i - 1]) {
      continue;
    }
    // do a 2 sum
    const twoSumTarget = target - nums[i];
    let l = i + 1;
    let r = nums.length - 1;
    while (l < r) {
      const twoSum = nums[l] + nums[r];
      const threeSum = nums[i] + twoSum;
      if (twoSum === twoSumTarget) {
        return target;
      } else if (twoSum < twoSumTarget) {
        l++;
        // optimization
        while (nums[l] === nums[l - 1]) {
          l++;
        }
      } else if (twoSum > twoSumTarget) {
        r--;
      }
      if (Math.abs(target - threeSum) < Math.abs(target - closestNumber)) {
        closestNumber = threeSum;
      }
    }
  }
  return closestNumber;
};
