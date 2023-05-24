// https://leetcode.com/problems/minimum-size-subarray-sum/description/
// Difficulty: Medium
// tags: sliding window variable

// Problem: find the minimum length subarray that has a sum >= target. The array only has positive numbers.

// Solution

// O(n) time and O(1) space. Variable sliding window.As we iterate, we store a dpSum. As soon as we reach a number for the first time, we add it to our sum, and this is the only time we will add it. If our sum is not big enough after that addition, we need to keep incrementing. If our sum is big enough, we can decrement the left pointer. If we just decrement it once, we will end up adding nums[r] again in the next iteration of the while loop. Instead, we should decrement the from left pointer until we are under the target, and then we know we need to increment the right pointer once again. We could also just not increment r each time, and that way if our sum is too big we increment l only.

// This won't work if there can be negative numbers in the array, because we aren't sure if incrementing r will increase the sum, and decrementing l will decrease it. For instance: [-10, 8, 4] target = 7. We start pointing at -10, and the sum is too small, so we point r at 8 now. The sum (-2) is still too small, so we point r at 4. The sum is still too small, but if we increment r we close the while loop. We actually want to decrement l to get [8] but we cannot.

// We can't use a strategy where we check if the left number is negative, and if so increase the sum by removing that, consider: [2, -50, 100] target = 52. When our window is [2, -50, 100] sum=52, we don't know if we can remove 2. It momentarily reduces our sum below the target, but in theory it would be good because then we could also remove -50. Yes if our left number is negative we can remove it, but to do so we would need to remove positive numbers first anyway. Even for: [80, -40, 30, 30, 30, 100] target=170 sum = 230, and we are at the full window, we know we have to drop the 80 since we did reach our target. And after we drop the 80 we are below the target, and yes we can immediately check that we could also drop the -40, but we can't really use that strategy. Consider [15, 15, 30, 30 -40, 50, 40] target=100. Once we get to the [15, 15, 30, 30 -40, 50] and we get a length of 6, we could technically drop 2 15s, and add and get [30, 30, -50, 50, 40] which is length 5. But how would we even know to drop those 2 15s, we can't because we haven't seen the next numbers yet. If we iterated first to the next number and then started decrementing, something like [1, 1, 1, 100, 1] target=100 might fail when we are at [1, 1, 1, 100] because if we include the next 1 in the array, we skip the subarray [100] which is the smallest.

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
