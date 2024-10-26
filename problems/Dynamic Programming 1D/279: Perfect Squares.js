// https://leetcode.com/problems/perfect-squares/description/
// difficulty: medium
// tags: dynamic programming 1d, top down recursion

// Problem
/*
Given an integer n, return the least number of perfect square numbers that sum to n.

A perfect square is an integer that is the square of an integer; in other words, it is the product of some integer with itself. For example, 1, 4, 9, and 16 are perfect squares while 3 and 11 are not.
*/

// Solution, O(n * root n) time, O(n) space
/*
Create a dp of array of size n. I actually just created one to be the max size of what n could be, since the dp can be reused as it doesn't depend on the input. Also create an array of squares within 10**4 (max n size), which I also did only once. Then, for a given dp state, compute the minimum amount of squares needed by checking all squares smaller than the amount remaining.
*/

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
