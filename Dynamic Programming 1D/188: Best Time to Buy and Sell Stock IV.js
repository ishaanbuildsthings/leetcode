// https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/description/
// Difficulty: hard
// tags: state machine, dynamic programming 1d

// Problem
/*
Simplified:

We have a chart of stock prices over time. We can make at most k buy+sell pair transactions, but can only ever old one stock at a time, what is our max profit?

Detailed:
You are given an integer array prices where prices[i] is the price of a given stock on the ith day, and an integer k.

Find the maximum profit you can achieve. You may complete at most k transactions: i.e. you may buy at most k times and sell at most k times.

Note: You may not engage in multiple transactions simultaneously (i.e., you must sell the stock before you buy again).
*/

// Solution 1, O(n*k) time and O(k) space

/*
We use a state machine. For instance, we track the most profit we have if we are looking to buy our very first stock (this is always defaulted to 0). We track our max profit if we are holding our first stock, max profit if we are looking to buy our second stock, etc.

All of this info can be updated on prior info. For instance when we see a new price, we can update the max profit we have if we are holding our first stock- if the new price we see is the cheapest one, we would update it. We could also update our max profit if we have sold our first stock, by looking at the previous max, and comparing it with our max profit from previously holding a stock and selling it today.

I think the simulation technically also will buy and sell stocks on the same day, but that never is optimally profitable, so it doens't matter that those are computed.
*/

var maxProfit = function (k, prices) {
  /*
    maps numbers from 1 through k to arrays containing maxes of this data:

    1 : [looking to buy first stock, holding first stock],
    2 : [looking to buy second stock, holding second stock],
    3 : [looking to buy third stock, holding third stock],
    etc

    So when we encounter a new element, we can start updating things.

    Say we have [3] as our first price.

    This means looking to buy first stock is 0 (it always is). And holding first stock is -3.

    Our next price is a 1. Looking to buy first stock is a 0. Holding first stock is now the max of either what it was before, or looking to buy first stock - prices[i].

    Looking to buy secondStock is also the max of what it was before (initially -Infinity), and the previous holding first stock + prices[i].
    */

  const mapping = {};

  // iterating to k+1, say k is 2. then we need to consider "looking to buy 3rd stock" because that is if we sold the 2nd stock.

  for (let i = 1; i <= k + 1; i++) {
    mapping[i] = [-Infinity, -Infinity]; // by default, every value except for the first is -Infinity. After all, why should we have profit of even 0 for something like lookingToBuy3rdStock, if we haven't sold anything yet? If we set these to 0, the solution may work, but things like lookingToBuy3rdStock might also simulate only buying 1 or 2 stocks, this is more explicitly clear.
  }

  mapping[1][0] = 0; // looking to buy our first stock max profit is always 0

  for (let i = 0; i < prices.length; i++) {
    for (const transactionCount in mapping) {
      const tuple = mapping[transactionCount];
      // console.log(`looking to buy ${transactionCount}rd stock: ${tuple[0]} holding that stock: ${tuple[1]}`)

      if (transactionCount === "1") {
        // the max money we have for if we are holding one stock is always the maximum of when we were already holding it, and if we purchased it now. we use this if condition as we never update the maximum profit for if we are looking to buy our first stock, it is always 0.
        tuple[1] = Math.max(tuple[1], 0 - prices[i]);
      } else {
        const priorKey = Number(transactionCount) - 1;
        const priorTuple = mapping[priorKey];
        tuple[0] = Math.max(tuple[0], priorTuple[1] + prices[i]);
        tuple[1] = Math.max(tuple[1], tuple[0] - prices[i]);
      }
    }
  }

  let result = 0;
  for (const key in mapping) {
    const tuple = mapping[key];
    result = Math.max(result, tuple[0], tuple[1]);
  }

  return result;
};
