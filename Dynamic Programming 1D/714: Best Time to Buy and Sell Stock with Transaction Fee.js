// https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/description/
// Difficulty: Medium
// tags: dynamic programming 1d, state machine, bottom up recursion

// Problem
/*
Example:
Input: prices = [1,3,2,8,4,9], fee = 2
Output: 8
Explanation: The maximum profit can be achieved by:
- Buying at prices[0] = 1
- Selling at prices[3] = 8
- Buying at prices[4] = 4
- Selling at prices[5] = 9
The total profit is ((8 - 1) - 2) + ((9 - 4) - 2) = 8.

Detailed:

You are given an array prices where prices[i] is the price of a given stock on the ith day, and an integer fee representing a transaction fee.

Find the maximum profit you can achieve. You may complete as many transactions as you like, but you need to pay the transaction fee for each transaction.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).
*/

// Solution 1, O(n) time and O(1) space, state machine
// * Solution 2 is an n^2 dp
// * We can also just dp a dp of (i, holding) and do something or do nothing

/*
We maintain two states, looking to buy a stock, and holding a stock. We can update looking to buy a stock by compare the old value of it with if we sell our previously held stock for todays price (minus the fee).

We can update holding stock if we compare it with the previous, and also consider if we were previously holding stock and bought stock today.

I think because I didn't use a temp variable, the simulation might consider things like buying and selling on the same day, which doesn't matter since those results are not optimal anyway.
*/

var maxProfit = function (prices, fee) {
  let lookingToBuyStock = 0;
  let holdingStock = -Infinity;
  for (let i = 0; i < prices.length; i++) {
    lookingToBuyStock = Math.max(
      lookingToBuyStock,
      holdingStock + prices[i] - fee
    );
    holdingStock = Math.max(holdingStock, lookingToBuyStock - prices[i]);
  }

  return lookingToBuyStock;
};

// Solution 2, O(n^2) time and O(n) space, tabulation - this probably works, but gets time limit exceeded on later test cases.

/*
for any given day, the max profit we can make is either
1) we buy the stock, then on some future day we sell, take that profit, then take the following dp

2) we do nothing, so we take the profit of the next day
*/

var maxProfit = function (prices, fee) {
  const dp = new Array(prices.length).fill(null);

  dp[dp.length - 1] = 0; // there is no profit that can be gotten from just the last day

  /*
    for any given day, the max profit we can make is either
    1) we buy the stock, then on some future day we sell, take that profit, then take the following dp

    2) we do nothing, so we take the profit of the next day
    */

  // start iterating from the 2nd to last day
  for (let day = dp.length - 2; day >= 0; day--) {
    const option1 = dp[day + 1];

    let option2 = -Infinity;

    for (let futureDay = day + 1; futureDay < dp.length; futureDay++) {
      const futurePrice = prices[futureDay];
      const currentPrice = prices[day];
      const profit = futurePrice - currentPrice - fee;
      // after selling it on some future day, we add the dp after it, if it exists
      let futureDp;
      // if we sold on the last day, there is no futuredp to add
      if (futureDay === dp.length - 1) {
        futureDp = 0;
      } else {
        futureDp = dp[futureDay + 1];
      }

      const sellOnThatDayAndTakeNextDp = profit + futureDp;

      option2 = Math.max(option2, sellOnThatDayAndTakeNextDp);
    }

    dp[day] = Math.max(option1, option2);
  }

  return dp[0];
};
