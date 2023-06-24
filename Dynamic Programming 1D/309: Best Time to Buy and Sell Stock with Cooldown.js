// https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/description/
// Difficulty: Medium
// tags: dynamic programming 1d, state machine, bottom up recursion

// Problem
/*
You are given an array prices where prices[i] is the price of a given stock on the ith day.

Find the maximum profit you can achieve. You may complete as many transactions as you like (i.e., buy one and sell one share of the stock multiple times) with the following restrictions:

After you sell your stock, you cannot buy stock on the next day (i.e., cooldown one day).
Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).
*/

// Solution, O(n^2) time and O(n) space, tabulation
// * Solution 2, O(n) time and O(1) space using a state machine

/*
Consider the problem for trying to figure out how much we can profit from some given price array, say [1, 2, 3, 0, 2].

We can reduce the problem to subproblems:

1) We buy the stock now, and sell it at one of n possible future prices. When we sell it, we make some profit. We add that profit to the dp space 2 over. For instance if we buy at 1, and sell at 2, our profit is 1. We add that to the result of the subproblem starting at number 0, which is when we are off cooldown.

2) We do nothing with the stock now, and defer action to the next day. We take the dp from the next day, which is 1 space over.

So, to solve the dp of our given cell, we take the max of those.

Since for each cell, we have to consider up to n cells on the right, the time is n^2. And the space is O(n) to store the dp.

*/

var maxProfit = function (prices) {
  /*
    in the dp, we store the answers to the initial problem, as if we starting at some index. for instance if dp is length 4, dp[2] (the third number) would store the problem to the original question if we had the subarrary from indicies [2, 3]. Then, we can use a formula to solve what the previous value is. The previous value would have to check every subsequent value, buy and sell if needed, and take a value after the cooldown as the max profit. (see editorial solution if this doesn't make sense, they had the same idea)
    */
  const dp = new Array(prices.length).fill(null);
  dp[prices.length - 1] = 0; // profiting from the very last option stock price only is impossible

  // iterate backwards, filling out the tabulation, starting from the second to last element
  for (let i = prices.length - 2; i >= 0; i--) {
    // case 1, we do nothing with the stock, so the amount we can profit from this cell is just the amount we profit from the cell on the right. for instance in [7, 5], we know at the 5 our max profit is 0. at the 7, our case 1 is we do nothing, and therefore our case 1 profit is just what our profit is at the 5, since we defer action.
    const case1 = dp[i + 1];

    // case 2, we buy the stock at the given cell, the amount we can profit is therefore as follows: we iterate through all future cells, and see what happens if we sell the stock, then take the profit from 2 spaces over, after the cooldown has ended. for instance in [1, 7, 2, 3, 8]. Say we are solving for the 1. If we buy at 1, try all values to the right. For instance when we try value 7, that means we sell at 7. So far profit is 6. Then, we add that 6 to the dp at 3, since that is the next time we could buy a stock.

    const currentPrice = prices[i];
    let maxProfitCase2 = 0;

    // scan all future prices, we can buy at our current price, sell at that future price, then take the result for the dp 2 spaces over
    for (let j = i + 1; j < prices.length; j++) {
      const sellPrice = prices[j];
      let currentProfit = sellPrice - currentPrice; // can be negative

      // if we have a future dp to consider, as in we could maybe buy something again (wouldn't apply if we are too close to the end of the array), then add that
      if (j + 2 < prices.length) {
        currentProfit += dp[j + 2];
      }

      maxProfitCase2 = Math.max(maxProfitCase2, currentProfit);
    }

    dp[i] = Math.max(case1, maxProfitCase2);
  }

  return dp[0];
};
