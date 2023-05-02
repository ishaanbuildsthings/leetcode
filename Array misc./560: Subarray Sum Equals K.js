// Solution ONLY if all numbers are positive: O(n) time and O(1) space. Uses a sliding window, we increment the window to the right when the sum is too small, and decrement it from the left when the sum is too big. This finds all solutions even if the numbers are not sorted.
// The sliding window works because we are only checking contiguous arrays. If the sum is too small, clearly  we need to add another number. But if it's too big, why can we just remove the left number? Consider this array: [1, 2, 3] and say we are pointing at 1 and 3, and our array is too big. We could reset both pointers to 2 like how we do in the n^2 and n^3 solutions, but it would be redundant to check that. How could the array [2] possibly be correct? If it were, [1, 2] would have been too big, and we would have decremented 1 already. The array also doesn't need to be sorted, say [2, 1, 3] and we are pointing at 2 and 3. [1] could not possibly be a solution, or we would have decremeneted from [2, 1] already.
const subarraySum = function (nums, k) {
  let l = 0;
  let r = 0;
  let dpSum = 0;
  let totalSolutions = 0;
  while (l < nums.length) {
    if (dpSum < k) {
      r++;
      dpSum += nums[r];
    } else if (dpSum > k) {
      l++;
      dpSum -= nums[l];
    } else if (dpSum === k) {
      totalSolutions++;
      l++;
      dpSum -= nums[l];
    }
  }
  return totalSolutions;
};

// Solution 2: O(n^2) time and O(1) space. For LEARNING PURPOSES only. This solution is the same as solution 3, but caches the prior sum in a variable instead of computing it each time.
const subarraySum2 = function (nums, k) {
  let totalArrays = 0;
  let dpSum; // tracks the sum
  for (let start = 0; start < nums.length; start++) {
    dpSum = 0; // every time our starting pointer moves over, reset the sum
    for (let end = start; end < nums.length; end++) {
      dpSum += nums[end]; // whenever the ending pointer moves, incremenet the dp sum by the new value
      if (dpSum === k) {
        totalArrays++;
      }
    }
  }
  return totalArrays;
};

// Solution 3: O(n^3) time and O(1) space. For LEARNING PURPOSES only. This solution checks every subarray using a left and right pointer (n^2 subarrays) and sums them (n operation), for n^3 time.
const subarraySum3 = function (nums, k) {
  let totalArrays = 0;
  for (let start = 0; start < nums.length; start++) {
    for (let end = start; end < nums.length; end++) {
      let sum = 0;
      for (let i = start; i <= end; i++) {
        sum += nums[i];
      }
      if (sum === k) {
        totalArrays++;
      }
    }
  }
  return totalArrays;
};
