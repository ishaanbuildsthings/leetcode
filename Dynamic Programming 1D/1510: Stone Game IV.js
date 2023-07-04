// https://leetcode.com/problems/stone-game-iv/description/
// Difficulty: Hard
// tags: dynamic programming 1d

// Problem
/*
Example:
Input: n = 2
Output: false
Explanation: Alice can only remove 1 stone, after that Bob removes the last one winning the game (2 -> 1 -> 0).

Detailed:
Alice and Bob take turns playing a game, with Alice starting first.

Initially, there are n stones in a pile. On each player's turn, that player makes a move consisting of removing any non-zero square number of stones in the pile.

Also, if a player cannot make a move, he/she loses the game.

Given a positive integer n, return true if and only if Alice wins the game otherwise return false, assuming both players play optimally.
*/

// Solution, O(n*root n) time, O(n) space for the dp array. We also spend O(10**5) (max n) time initializing a squares array of root n space. We put the memo outside the function since it the memo doesn't depend on the input, it is just a universal function of the game (optimization, not needed for time complexity). We could also remove the inner dp function I just left it in as a fragment of my initial implementation.

/*
First, compute all squares we might need, so we know possible moves. Maintain a dp array that checks whether a player moving first can win if they draw some amount of stones. For alice, try drawing all possible squares, and we win if one of the draws wins. We calculate that we win if after drawing that many stones, it is not possible to win from the remaining stone count.
*/

const allSquares = [];
for (let i = 1; i <= Math.floor(Math.sqrt(10 ** 5)); i++) {
  const squared = i * i;
  allSquares.push(squared);
}

// represents if the problem can be won for n for a given person's turn, or -1 if no solution has yet been found
const memo = new Array(10 ** 5 + 1).fill(-1);
// all of the squares are true
for (let i = 0; i < allSquares.length; i++) {
  const square = allSquares[i];
  // if (square > n) {
  //     break;
  // }
  memo[square] = true;
}

var winnerSquareGame = function (n) {
  function dp(stones) {
    if (stones === 0) {
      return true;
    }

    // if we have already determined a result for alice for this amount, return that
    if (memo[stones] !== -1) {
      return memo[stones];
    }

    let canWin = false;

    // try every possible stone removal, if any force a win, alice can win
    for (let i = 0; i < allSquares.length; i++) {
      // stop once the stone removal becomes bigger than the amount of stones we have left
      if (allSquares[i] > stones) {
        break;
      }

      const couldWinWithThisRemoval = !dp(stones - allSquares[i]); // if we remove some square amount, and the resulting dp is false, it means that bob couldn't win with that many stones left, so alice could win

      canWin = canWin || couldWinWithThisRemoval;

      // optimization, early prune
      if (canWin) {
        break;
      }
    }

    memo[stones] = canWin;
    return canWin;
  }

  return dp(n);
};
