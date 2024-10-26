// https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/description/
// Difficulty: Medium

// Problem
/*
Simplified:

Input: prices = [7,1,5,3,6,4]
Output: 7
Explanation: Buy on day 2 (price = 1) and sell on day 3 (price = 5), profit = 5-1 = 4.
Then buy on day 4 (price = 3) and sell on day 5 (price = 6), profit = 6-3 = 3.
Total profit is 4 + 3 = 7.

Detailed:

You are given an integer array prices where prices[i] is the price of a given stock on the ith day.

On each day, you may decide to buy and/or sell the stock. You can only hold at most one share of the stock at any time. However, you can buy it then immediately sell it on the same day.

Find and return the maximum profit you can achieve.
*/

// Solution, O(n) time and O(1) space, simulation.
// * Solution 2 is more concise and elegant
/*
Just simulate buying and selling the stock. Find the initial entry point. If we own a stock, sell it if the next price is lower, hold if higher. If we don't own a stock, buy one if the next day's price is higher.
*/

var maxProfit = function (prices) {
  // find the cheapest starting entry point
  let i;
  for (i = 0; i < prices.length - 1; i++) {
    // if the next price is greater, we should buy at i, and that is our entry point
    if (prices[i + 1] > prices[i]) {
      break;
    }
  }

  // if there is no entry point, return 0
  if (i === prices.length - 1) {
    return 0;
  }

  // we start with negative money since we initially buy the stock
  let currentProfit = -1 * prices[i];

  let ownStock = true;

  while (i < prices.length) {
    // edge case, we are at the last price, if we own a stock we can sell it. edge case since we have no future price to compare to
    if (i === prices.length - 1 && ownStock) {
      currentProfit += prices[i];
      break;
    }

    // if we own a stock, and the next price is >= current price, do nothing, since we will hold the stock
    if (ownStock && prices[i + 1] >= prices[i]) {
    }

    // if we own a stock, and the next price is lower, we sell the stock and gain the current price
    else if (ownStock && prices[i + 1] < prices[i]) {
      currentProfit += prices[i];
      ownStock = false;
    }

    // if we don't own a stock, and the next price is <= current price, we don't do anything
    else if (!ownStock && prices[i + 1] <= prices[i]) {
    }

    // if we don't own a stock, but the next price is higher, we will buy it so we can profit
    else if (!ownStock && prices[i + 1] > prices[i]) {
      currentProfit -= prices[i];
      ownStock = true;
    }

    i++;
  }

  return currentProfit;
};

// Solution 2, O(n) time and O(1) space. Since we can maximally extract all the profit, we can just add all the positive differences. So if the prices are 5, 10, 3, 8, our profit comes from 10-5 and 8-3. So any time the next days price is higher, we add the difference to our profit.

var maxProfit = function (prices) {
  let profit = 0;
  for (let i = 0; i < prices.length - 1; i++) {
    if (prices[i + 1] > prices[i]) {
      profit += prices[i + 1] - prices[i];
    }
  }

  return profit;
};
