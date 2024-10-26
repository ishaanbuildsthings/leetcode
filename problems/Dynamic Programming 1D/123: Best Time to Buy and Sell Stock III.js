// https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/description/
// Difficulty: Hard
// tags: state machine

// Problem
/*
Simplified:

Input: prices = [3,3,5,0,0,3,1,4]
Output: 6
Explanation: Buy on day 4 (price = 0) and sell on day 6 (price = 3), profit = 3-0 = 3.
Then buy on day 7 (price = 1) and sell on day 8 (price = 4), profit = 4-1 = 3.

Detailed:

You are given an array prices where prices[i] is the price of a given stock on the ith day.

Find the maximum profit you can achieve. You may complete at most two transactions.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).
*/

// Solution 1, O(n) time and O(1) space, state machine.
// * Solution 2. We can presolve all subproblems that use one transaction, for both starting from 0 to some ending index, and starting from some ending ending at the end. For instance in [1, 5, 2, 3] we could solve the one transaction problem for [1], [1, 5], etc. And for [1, 5, 2, 3], [5, 2, 3], etc. Now we iterate through n, and we check the max profit on the left and right portions.

// * There is another O(n) time and O(1) solution in the edtorial using a t1 cost, t1 profit, t2 cost, and t2 profit solution, but IMO this is more confusing.
/*
Maintain a state for each possible situation. We could be looking to buy the first stock, holding the first stock, sold the first stock and looking to buy the second, holding the second stock, or we have sold the second stock. Each iteration of prices, we can update all of this information based on the prior information. For instance, to update holdingStockOne, we basically want to find the cheapest price we have seen thus far. So we take the max of the previous holdingStockOne (which will be negative, as we paid money for a stock), and the current one.

We update all these states, and return the max of 0, if we made one complete transaction, or if we made two, since we are allowed up to at most two transactions.

Technically, we don't need to return lookingToBuySecondStock in the Math.max at the end. We would think we need the case where we only sold one stock, but soldSecondStock can actually have sold just one stock, since we initialize lookingToBuySecondStock to 0.
*/

var maxProfit = function (prices) {
  // state machine, tracks the optimal amount of money we have for each state
  let holdingStockOne = -Infinity; // we cannot set this to 0, that implies we got a stock for free and can sell it
  let lookingToBuySecondStock = -Infinity; // technically not needed, if we set it to 0, it would basically also simulate the cases of buying just one stock, but by setting it to -Infinity it is explicitly clear that we must first sell a stock
  let holdingStockTwo = -Infinity; // we cannot set this to zero, it implies we bought stock 2 for free and can sell it
  let soldSecondStock = -Infinity; // same reasoning as setting `lookingToBuySecondStock` to -Infinity

  for (let i = 0; i < prices.length; i++) {
    // if we are holding stock one, we can either take the best of the previous time we were holding it, or if we were to buy it just now
    holdingStockOne = Math.max(holdingStockOne, 0 - prices[i]);
    // if we sell the first stock, we can either take the max of the previous time we sold the first stock, or take the state where we are holding stock one and sell it now
    lookingToBuySecondStock = Math.max(
      lookingToBuySecondStock,
      holdingStockOne + prices[i]
    );
    holdingStockTwo = Math.max(
      holdingStockTwo,
      lookingToBuySecondStock - prices[i]
    );
    soldSecondStock = Math.max(soldSecondStock, holdingStockTwo + prices[i]);
  }

  return Math.max(0, lookingToBuySecondStock, soldSecondStock);
};
