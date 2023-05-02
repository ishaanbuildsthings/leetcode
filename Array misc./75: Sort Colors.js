// https://leetcode.com/problems/sort-colors/
// Difficulty: Medium
// tags: bucket sort

// Solution
// bucket sort
// O(n) time and O(n) space. Iterate over the elements and maintain a count for the buckets. Iterate over the array again and rewrite the elements in order.

const sortColors = function (nums) {
  const buckets = {
    0: 0,
    1: 0,
    2: 0,
  };
  for (let num of nums) {
    buckets[num]++;
  }
  console.log(buckets);

  for (let i = 0; i < nums.length; i++) {
    if (buckets[0] > 0) {
      nums[i] = 0;
      buckets[0]--;
    } else if (buckets[1] > 0) {
      nums[i] = 1;
      buckets[1]--;
    } else {
      nums[i] = 2;
      buckets[2]--;
    }
  }

  return nums;
};
