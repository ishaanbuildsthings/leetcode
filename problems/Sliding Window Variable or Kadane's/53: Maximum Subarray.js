// https://leetcode.com/problems/maximum-subarray/
// Difficulty: Medium
// tags: kadane's

// NOTES
// If we used a two pointer sliding window variant of kadane's, we simply incrementing l++ when our subarray becomes negative would be inefficient, consider: [1, 5, 2, -9]
// when we reach -9, our overall sum is -1, so why do we reset the left pointer all the way to the number after -9, as opposed to just incrementing it once? Say we did do l++, dropping a 1. Obviously we do not want to drop a 1, that's bad, but it might be favorable if we dropped a negative number instead. However, if that number were negative, we would have already dropped it at [1] if the 1 were negative. What about [6, 1, 5]? (pretend the 1 is negative) Then we would be including the 6 in our current array as well, and not want to drop that. Or more simply put, the first number of our sliding window can never be negative, otherwise why would we include it? So just incrementing once would always decrease our sum, but then what if the next number were negative (and bigger than the first positive number), say our window starts with [1, -6]. Then we wouldn't have included this prefix either! So just incrementing the left by one or some other amount that isn't a full reset, will never be useful because we're implying our prefix at that point was negative. We can't have a negative prefix since we would have reset the pointers if we did.

// Solution 1
// O(n) time and O(1) space
// Iterate over the array. As soon as we reach a number, add it to the dp sum. Now check if the new sum is our biggest yet. Reset the dpSum if it is too small. dpSum effectively is acting as the prefix until we reach the current number.

const maxSubArray = function (nums) {
  let maxSum = Number.NEGATIVE_INFINITY;
  let dpSum = 0;
  for (const num of nums) {
    dpSum += num;
    maxSum = Math.max(maxSum, dpSum);
    if (dpSum < 0) {
      dpSum = 0;
    }
  }
  return maxSum;
};
