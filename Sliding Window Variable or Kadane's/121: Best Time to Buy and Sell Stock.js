// https://leetcode.com/problems/best-time-to-buy-and-sell-stock/
// Difficulty: Easy
// tags: sliding window variable

// Solution
// O(n) time and O(1) space. Assigns two pointers at index 0 and 1. Checks the current profit based on the pointers. If we can profit, compare it to the current max profit. Slide the right pointer over to check a new sell price. If we cannot profit, move the left pointer over to the cheaper price, increment right pointer.
// * Solution 2: just to maintain the current smallest price we have seen, iterate over, check potential profit, and update a result.

const maxProfit = function (prices) {
  // edge case
  if (prices.length === 1) return 0;

  let l = 0;
  let r = 1;
  let maxProfit = 0;
  while (r < prices.length) {
    const currentProfit = prices[r] - prices[l];
    // if we can't profit from the current transaction, we should update our buy to prices[r], since it is cheaper. We can jump `l` straight to `r` because if there were a lower price in-between, our `l` would have been updated to that already.
    if (currentProfit <= 0) {
      l = r;
      r++;
      continue;
    }
    // if we can profit, see if it's the most money we can make, and try the next price
    maxProfit = Math.max(maxProfit, currentProfit);
    r++;
  }
  return maxProfit;
};
