// https://leetcode.com/problems/minimum-size-subarray-sum/description/
// Difficulty: Medium
// tags: sliding window variable

// Solution

// O(n) time and O(1) space. Create two pointers at the beginning, and iterate until our right pointer goes past the array. As we iterate, we store a prefix for the sum of the array. As soon as we reach a number for the first time, we add it to our prefix, and this is the only time we will add it. If our prefix is not big enough after that addition, we need to keep incrementing. If our prefix is big enough, we can decrement the left pointer. If we just decrement it once, we will end up adding nums[r] again in the next iteration of the while loop. Instead, we should decrement the left pointer until we are under the target, and then we know we need to increment the right pointer once again. We could choose to use a more confusing solution, where as soon as our sum is too big we increment the left pointer once, and then on the next iteration of the while loop we check if we just incremented the left pointer, because we would not want to add nums[r] in that case. However, that would basically be the same thing, we would just be flattening out the logic of our nested while loop into a single while loop with extra if statements.

// This won't work if there can be negative numbers in the array, because we aren't sure if incrementing r will increase the sum, and decrementing l will decrease it. For instance: [-10, 8, 4] target = 7. We start pointing at -10, and the sum is too small, so we point r at 8 now. The sum (2) is still too small, so we point r at 4. The sum is still too small, but if we increment r we close the while loop. We actually want to decrement l to get [8] but we cannot.

// We can't use a strategy where we check if the left number is negative, and if so increase the sum by removing that, consider: [2, -50, 100] target = 52. When we are pointing l->2 r->10000, we don't know if we can remove 2. It momentarily reduces our sum below the target, but in theory it would be good because then we could also remove -50.

const minSubArrayLen = function (target, nums) {
  let l = 0;
  let r = 0;
  let minLength = Number.POSITIVE_INFINITY;
  let prefixSum = 0;

  while (r < nums.length) {
    prefixSum += nums[r];
    while (prefixSum >= target) {
      minLength = Math.min(minLength, r - l + 1);
      prefixSum -= nums[l];
      l++;
    }
    r++;
  }
  return minLength === Number.POSITIVE_INFINITY ? 0 : minLength;
};

// If we are trying to solve the same problem except we are looking for subarrays that specifically equal k (not >=), and our numbers are all positive, we can still do O(n) time and O(1) space.

// The differences are that now when we see our subarray is >= the target, we then check if it precisely equals the target. If so we increment l as usual. However, if l ever passes r, such as [0,0,0], we break out of the loop. We also cannot just check (prefixSum === target) in the first while loop, consider: [1, 5, 2] and target is 7, we need to decrement 1 but we can't since our sum doesn't equal 7, it equals 8.

const minSubArrayLen2 = function (target, nums) {
  let l = 0;
  let r = 0;
  let minLength = Number.POSITIVE_INFINITY;
  let prefixSum = 0;

  while (r < nums.length) {
    prefixSum += nums[r];
    while (prefixSum >= target) {
      if (prefixSum === target) {
        minLength = Math.min(minLength, r - l + 1);
      }

      prefixSum -= nums[l];
      l++;
      if (l >= r) break;
    }
    r++;
  }
  return minLength === Number.POSITIVE_INFINITY ? 0 : minLength;
};
