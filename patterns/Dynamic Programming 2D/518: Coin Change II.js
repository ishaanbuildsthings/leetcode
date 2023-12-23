// https://leetcode.com/problems/coin-change-ii/description/
// Difficulty: Medium
// Tags: dynamic programming 2d

// Problem
/*
You are given an integer array coins representing coins of different denominations and an integer amount representing a total amount of money.

Return the number of combinations that make up that amount. If that amount of money cannot be made up by any combination of the coins, return 0.

You may assume that you have an infinite number of each kind of coin.

The answer is guaranteed to fit into a signed 32-bit integer.
*/

// Solution, O(amount * num coins) time and space
/*
For a given amount, we can take any of the coins. Importantly, we can take the same coin over and over, but if we skip it, we can never take it again. Maintain a pointer, `i`, that tracks which coins left we are allowed to take from. It is similar to a lot of backtracking with duplicate problems I did. Also maintain the amount remaining. So memo[i][amount] tells us how many ways there are to make a given amount with [i:] coins left. There are coin types * amount options.
*/

var change = function (amount, coins) {
  //memo[i][amount] returns the number of ways we can make amount, using only coins from [i:]
  const memo = new Array(coins.length)
    .fill()
    .map(() => new Array(amount + 1).fill(-1));

  // returns the number of ways for the subproblem
  function dp(i, amountRemaining) {
    // if we have no amount left, we find a way
    if (amountRemaining === 0) {
      return 1;
    }

    // if taking the ith coin put us under the amount, we cannot make the exact amount. we could also choose to never enter this recursive call instead
    if (amountRemaining < 0) {
      return 0;
    }

    // if there are no coin types left
    if (i === coins.length) {
      return 0;
    }

    if (memo[i][amountRemaining] !== -1) {
      return memo[i][amountRemaining];
    }

    // we can either take the ith coin, or we can skip it, the number of ways at our current position is the sum of both
    const ifTake = dp(i, amountRemaining - coins[i]);

    const ifSkip = dp(i + 1, amountRemaining);

    const resultForThis = ifTake + ifSkip;

    memo[i][amountRemaining] = resultForThis;

    return resultForThis;
  }

  return dp(0, amount);
};
