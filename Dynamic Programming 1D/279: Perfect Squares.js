// https://leetcode.com/problems/perfect-squares/description/
// difficulty: medium
// tags: dynamic programming 1d, top down recursion

// only needs to be calculated once
const squares = [];
for (let i = 1; i <= Math.floor(Math.sqrt(10 ** 4)); i++) {
  squares.push(i * i);
}

// memo[x] corresponds to the least number of perfect squares needed to sum to x
const memo = new Array(10 ** 4 + 1).fill(-1);

var numSquares = function (n) {
  // returns how many squares are needed for some remaining amount
  function dp(remaining) {
    if (remaining === 0) {
      return 0;
    }

    if (memo[remaining] !== -1) {
      return memo[remaining];
    }

    let squaresNeeded = Infinity;

    // consider taking all possible squares as long as that square is within range
    for (let i = 0; i < squares.length; i++) {
      if (squares[i] > remaining) {
        break;
      }
      const waysIfWeTakeThisSquare = 1 + dp(remaining - squares[i]);
      squaresNeeded = Math.min(squaresNeeded, waysIfWeTakeThisSquare);
    }

    memo[remaining] = squaresNeeded;
    return squaresNeeded;
  }

  return dp(n);
};
