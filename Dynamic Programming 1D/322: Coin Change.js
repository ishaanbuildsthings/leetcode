// https://leetcode.com/problems/coin-change/description/
// difficulty: medium
// tags: dynamic programming 1d

// Problem
/*
Example:
Input: coins = [1,2,5], amount = 11
Output: 3
Explanation: 11 = 5 + 5 + 1

Detailed:

You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.

Return the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return -1.

You may assume that you have an infinite number of each kind of coin.
*/

// Solution 1, tabulation, O(amount*coin types) time and O(amount) space for the dp.
/*
To solve the the problem of the minimum amount of coins needed for amount 11, with coins of 1, 2, and 5, clearly the answer is either 1 coin + min needed for amount 10, 1 coin + min needed for amount 9, and 1 + min needed for amount of 6. We can use recursion + memoization until we get to a base case (an amount is doable in 1 coin, or no coins / is impossible). We can also use tabulation, first solving for amount 1, then 2, etc.

Notably, we cannot do something like store a dp min needed for a certain amount, then iterate and use cached values. For instance to solve amount 11, say we descend down the tree, using a 1 coin each time. Now, to solve amount 6, we currently have 6 coins needed as our minimum. Then if we try using a 5 coin and get to 6, we would say we need the single 5 coin + 6 from before. Only later would we try a more efficient solution to solve amount 6 (a 5 + a 1), but it wouldn't have registered yet for the first time we tried using a 5 coin for amount 11. This is why we need to solve for the problems of amount 1 first, then 2, etc.
*/

var coinChange = function (coins, amount) {
  // the dp tracks the least amount of coins needed to reach a certain amount, null if it is not possible
  const dp = [];
  // if we ever reach a prior of 0 coins left, we can reach that in 0 coins
  dp[0] = 0;

  for (
    let amountWeAreTrying = 1;
    amountWeAreTrying <= amount;
    amountWeAreTrying++
  ) {
    for (const coinType of coins) {
      // say we are solving for reaching the amount 6, and we have a coin of 2, that means we should check the dp[4], which is priorDp, and see how many it took to reach 4 in the best case. Then, one way to reach 6 is 1 + dp[4]. We minimize this by trying all coin types.
      const priorDp = dp[amountWeAreTrying - coinType];
      // if there was no way to reach that prior state, we cannot solve the current state using a coin to reach that prior state
      if (priorDp === undefined) {
        continue;
      }

      if (dp[amountWeAreTrying] === undefined) {
        dp[amountWeAreTrying] = 1 + priorDp;
      } else {
        dp[amountWeAreTrying] = Math.min(dp[amountWeAreTrying], 1 + priorDp);
      }
    }
  }

  return dp[amount] === undefined ? -1 : dp[amount];
};
