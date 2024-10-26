// https://leetcode.com/problems/optimal-account-balancing/description/
// Difficulty: Hard
// tags: dynamic programming 1d, top down recursion, bit mask

// Problem
/*
Example:
Input: transactions = [[0,1,10],[2,0,5]]
Output: 2
Explanation:
Person #0 gave person #1 $10.
Person #2 gave person #0 $5.
Two transactions are needed. One way to settle the debt is person #1 pays person #0 and #2 $5 each.

Detailed:
You are given an array of transactions transactions where transactions[i] = [fromi, toi, amounti] indicates that the person with ID = fromi gave amounti $ to the person with ID = toi.

Return the minimum number of transactions required to settle the debt.
*/

// Solution, O(# people)^2 space. As our callstack depth is O(# people), and each one stores a serialized mapping. Technically we have inbetween calls if the person doesn't exist, this can be easily fixed though. Time is more complex, since it isn't quite n*2^n, as my serializations map to more than 2^n states.
/*
My solution was quite bad, and is the bottom 5% of time and space solutions. There were better, more complex solutions that had better recurrence relationships. I left this in though since it passed and I've only just started doing hards.

For each person, try to settle their debt with every other person who has unsettled debt. Memoize the state of debts.
*/

var minTransfers = function (transactions) {
  // positive if you are owed money, negative if you owe money
  const surplus = {};

  for (const [from, to, amount] of transactions) {
    if (from in surplus) {
      surplus[from] += amount;
    } else {
      surplus[from] = amount;
    }

    if (to in surplus) {
      surplus[to] -= amount;
    } else {
      surplus[to] = -1 * amount;
    }
  }

  const maxPersonNumber = Object.keys(surplus).reduce(
    (acc, val) => (acc = Math.max(acc, val)),
    0
  );

  const memo = {}; // maps serialized surpluses to the minimum amount of transactions needed to settle the debt

  // i tracks whose turn it is to settle debt
  function dp(surplus, i) {
    const serialized = JSON.stringify(surplus);
    if (serialized in memo) {
      return memo[serialized];
    }

    // base case, no one left to settle debt
    if (i === maxPersonNumber) {
      return 0;
    }

    // edge case, there can be missing people
    if (!(i in surplus)) {
      return dp(surplus, i + 1);
    }

    // if our debt was already settled for this person, try settling the next persons debt
    if (surplus[i] === 0) {
      return dp(surplus, i + 1);
    }

    let minimumTransactions = Infinity;

    // j is the person we settle our balance with
    for (let j = i + 1; j <= maxPersonNumber; j++) {
      // edge case, there can be missing people so we don't consider them
      if (!(j in surplus)) {
        continue;
      }

      // pruning, don't settle balance with people who are already settled
      if (surplus[j] === 0) {
        continue;
      }

      const ourSurplus = surplus[i];
      // we need to lose our surplus, and person j needs to gain it
      surplus[i] -= ourSurplus;
      surplus[j] += ourSurplus;

      const resultIfWeSettleWithThisPerson = 1 + dp(surplus, i + 1);

      minimumTransactions = Math.min(
        minimumTransactions,
        resultIfWeSettleWithThisPerson
      );

      // undo the surplus for the next iteration
      surplus[i] += ourSurplus;
      surplus[j] -= ourSurplus;
    }

    memo[serialized] = minimumTransactions;
    return minimumTransactions;
  }

  return dp(surplus, 0);
};
