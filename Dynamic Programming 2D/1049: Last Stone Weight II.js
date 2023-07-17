// https://leetcode.com/problems/last-stone-weight-ii/description/
// Difficulty: Medium
// Tags: dynamic programming 2d

// Problem
/*
You are given an array of integers stones where stones[i] is the weight of the ith stone.

We are playing a game with the stones. On each turn, we choose any two stones and smash them together. Suppose the stones have weights x and y with x <= y. The result of this smash is:

If x == y, both stones are destroyed, and
If x != y, the stone of weight x is destroyed, and the stone of weight y has new weight y - x.
At the end of the game, there is at most one stone left.

Return the smallest possible weight of the left stone. If there are no stones left, return 0.
*/

// Solution, O(n*sum) time, O(n*sum) space
/*
This problem boils down to 0/1 knapsack, but is really hard to see. To minimize the remaining stone weight, we clearly want the difference of our last two stones to be minimized.

To minimize the last two stones, we want to split our stones into two piles, whose sums roughly equal each other. For instance if stones are 1, 2, 4, we can partition into 1,2 | 4. And every stone from the left is smashed with the right. You can keep repeating, the order doesn't matter (just think about how this works). So basically we try to get as close to half as possible.

We can do this by choosing half, and seeing how close we can get to filling it up. The memo is [i][remaining storage], and it stores the minimal amount of extra storage we have.

There are n*sum states, each takes constant time.
*/

var lastStoneWeightII = function (stones) {
  const totalWeight = stones.reduce((acc, val) => acc + val, 0);

  const HALF_WEIGHT = Math.floor(totalWeight / 2); // we want to get as close to halfWeight as possible, without exceeding it

  // memo[i][remaining weight] stores the result, which is the excess amount of remaining weight over the weight we can fit in, with [i:] elements left
  const memo = new Array(stones.length)
    .fill()
    .map(() => new Array(HALF_WEIGHT + 1).fill(-1));

  function dp(i, remainingStorage) {
    // if we have no stones left to get, we cannot fill up any more of the remaining storage
    if (i === stones.length) {
      return remainingStorage;
    }

    if (memo[i][remainingStorage] !== -1) {
      return memo[i][remainingStorage];
    }

    // we can either put a stone in our left portion (adding it), or in the right portion (not including it)

    const newStorageIfKeep = remainingStorage - stones[i];

    let ifKeep;
    if (newStorageIfKeep < 0) {
      ifKeep = Infinity;
    } else {
      ifKeep = dp(i + 1, newStorageIfKeep);
    }

    const ifSkip = dp(i + 1, remainingStorage);

    const resultForThis = Math.min(ifKeep, ifSkip);

    memo[i][remainingStorage] = resultForThis;
    return resultForThis;
  }

  const dpResult = dp(0, HALF_WEIGHT);

  if (totalWeight % 2 === 0) {
    return 2 * dpResult;
  } else {
    return 2 * dpResult + 1;
  }
};
