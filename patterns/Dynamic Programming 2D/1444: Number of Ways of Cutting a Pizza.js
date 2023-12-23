// https://leetcode.com/problems/number-of-ways-of-cutting-a-pizza/description/
// Difficulty: Hard
// Tags: Dynamic Programming 2d

// Problem
/*
Note: It helps to see the picture

Given a rectangular pizza represented as a rows x cols matrix containing the following characters: 'A' (an apple) and '.' (empty cell) and given the integer k. You have to cut the pizza into k pieces using k-1 cuts.

For each cut you choose the direction: vertical or horizontal, then you choose a cut position at the cell boundary and cut the pizza into two pieces. If you cut the pizza vertically, give the left part of the pizza to a person. If you cut the pizza horizontally, give the upper part of the pizza to a person. Give the last piece of pizza to the last person.

Return the number of ways of cutting the pizza such that each piece contains at least one apple. Since the answer can be a huge number, return this modulo 10^9 + 7.
*/

// Solution, time and space can be optimized so wasn't listed
/*
Since we can shed off from the left or the top, we can memoize r x c states. For each state, we can also have a certain amount of cuts left. So we have r*c*cuts space.

For a state, we can try all cuts then sum their subproblems. Things can be optimized to determine if there are apples in certain regions and whatnot using range queries and more so I didn't bother with listing complexities.
*/

var ways = function (pizza, k) {
  const MOD = 10 ** 9 + 7;
  const HEIGHT = pizza.length;
  const WIDTH = pizza[0].length;

  // edge case, if we have no apples return 0
  let apples = 0;
  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      if (pizza[r][c] === "A") {
        apples++;
      }
    }
  }
  if (!apples) return 0;

  // memo[r][c][cutsLeft] is the answer to the subproblem where we can start at that row and column with that many cuts left
  const memo = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill().map(() => new Array(k).fill(-1)));

  function dp(r, c, cutsLeft) {
    // base case, we have no cuts left, assuming we have an apple
    if (cutsLeft === 0) {
      return 1;
    }

    // count apples
    let apples = 0;
    for (let row = r; row < HEIGHT; row++) {
      for (let col = c; col < WIDTH; col++) {
        if (pizza[row][col] === "A") {
          apples++;
        }
      }
    }

    if (memo[r][c][cutsLeft] !== -1) {
      return memo[r][c][cutsLeft];
    }

    let resultForThis = 0;

    // we can make a row cut as long as there is an apple in both regions
    const originalApples = apples;
    apples = 0;
    // rowCut takes all apples that row and above
    for (let rowCut = r; rowCut < HEIGHT - 1; rowCut++) {
      for (let col = c; col < WIDTH; col++) {
        if (pizza[rowCut][col] === "A") {
          apples++;
        }
      }
      // apples in both regions
      if (apples > 0 && apples < originalApples) {
        const validWays = dp(rowCut + 1, c, cutsLeft - 1) % MOD;
        resultForThis = (resultForThis + validWays) % MOD;
      }
      // pruning
      if (apples === originalApples) {
        break;
      }
    }

    // we can make a col cut as long as there is an apple in both regions
    apples = 0;
    for (let colCut = c; colCut < WIDTH - 1; colCut++) {
      for (let row = r; row < HEIGHT; row++) {
        if (pizza[row][colCut] === "A") {
          apples++;
        }
      }
      if (apples > 0 && apples < originalApples) {
        const validWays = dp(r, colCut + 1, cutsLeft - 1) % MOD;
        resultForThis = (resultForThis + validWays) % MOD;
      }

      if (apples === originalApples) {
        break;
      }
    }

    memo[r][c][cutsLeft] = resultForThis;
    return resultForThis;
  }

  return dp(0, 0, k - 1);
};
