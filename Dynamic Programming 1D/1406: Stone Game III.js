// https://leetcode.com/problems/stone-game-iii/description/
// Difficulty: Hard
// tags: dynamic programming 1d

// Problem
/*
Example:
Input: stoneValue = [1,2,3,7]
Output: "Bob"
Explanation: Alice will always lose. Her best move will be to take three piles and the score become 6. Now the score of Bob is 7 and Bob wins.

Alice and Bob continue their games with piles of stones. There are several stones arranged in a row, and each stone has an associated value which is an integer given in the array stoneValue.

Alice and Bob take turns, with Alice starting first. On each player's turn, that player can take 1, 2, or 3 stones from the first remaining stones in the row.

The score of each player is the sum of the values of the stones taken. The score of each player is 0 initially.

The objective of the game is to end with the highest score, and the winner is the player with the highest score and there could be a tie. The game continues until all the stones have been taken.

Assume Alice and Bob play optimally.

Return "Alice" if Alice will win, "Bob" if Bob will win, or "Tie" if they will end the game with the same score.
*/

// Solution, O(n) time and O(n) space
/*
For each state, which is defined by the current starting index, we can choose one of three options, so there are n states which are solved in constant time. Typical DP. We could probably do bottom up as well if we started from the right. I used a range query to help compute the amount we win in constant time, though there are probably other ways to avoid this such as maybe a turn order (maximizer / minimizer)
*/

var stoneGameIII = function (stones) {
  // memo[l] stores the amount of stones you can in from [l, stoneValue.length - 1]
  const memo = new Array(stones.length);

  // helps us do O(1) range query
  let prefixSums = [];
  let runningSum = 0;
  for (let i = 0; i < stones.length; i++) {
    runningSum += stones[i];
    prefixSums[i] = runningSum;
  }
  prefixSums[-1] = 0; // if we try to range query from [0, x]

  function dp(l) {
    // base case
    if (l === stones.length - 1) {
      return stones[stones.length - 1];
    }

    // edge case, for if we finish all piles
    if (l >= stones.length) {
      return 0;
    }

    if (memo[l]) {
      return memo[l];
    }

    // total stones we can win from a given section is either: we take all stones minus the amount opponent wins from dp(l + 1), dp(l + 2), or dp(l + 3)
    const totalStones = prefixSums[prefixSums.length - 1] - prefixSums[l - 1];
    const stonesWeGetIfWeTakeOnePile = totalStones - dp(l + 1);
    const stonesWeGetIfWeTakeTwoPiles = totalStones - dp(l + 2);
    const stonesWeGetIfWeTakeThreePiles = totalStones - dp(l + 3);
    const maxStones = Math.max(
      stonesWeGetIfWeTakeOnePile,
      stonesWeGetIfWeTakeTwoPiles,
      stonesWeGetIfWeTakeThreePiles
    );

    memo[l] = maxStones;
    return maxStones;
  }

  const totalStones = prefixSums[prefixSums.length - 1];
  const stonesAliceWins = dp(0);
  if (stonesAliceWins > totalStones / 2) {
    return "Alice";
  } else if (stonesAliceWins === totalStones / 2) {
    return "Tie";
  } else {
    return "Bob";
  }
};
