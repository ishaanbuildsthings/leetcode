// https://leetcode.com/problems/making-a-large-island/description/
// Difficulty: Hard
// tags: graph, matrix dfs, state machine maybe

// Problem
/*
You are given an n x n binary matrix grid. You are allowed to change at most one 0 to be 1.

Return the size of the largest island in grid after applying this operation.

An island is a 4-directionally connected group of 1s.
*/

// Solution, O(n*m) time and O(n*m) space
/*
First, find the size of all islands, and give a unique idx to each island. So each cell in the islandInfo matrix will contain the size of the island it is in along with its idx.

Then, iterate through each water cell, seeing if we made it land, the total size of the island we would form, by checking the idx / sizes of adjacent islands.

I think for a follow up question where we can flip k ocean tiles, we could maybe use a state machine solution in conjunction with this solution.
*/

var largestIsland = function (grid) {
  const HEIGHT = grid.length;
  const WIDTH = grid[0].length;

  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  /*
    each cell stores information for a given tile of land (water tiles have null)
    when we visit / dfs through an island, and we determine the size of it, we will update all of those cells in here to say the size. we also give each cell an island idx, so each cell has [size, idx]. Later, when we iterate through every cell, testing a flip, we look at the neighbors, determine how many unique islands we connect, and determine the new size
    */
  const islandInfo = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(null));

  function getIslandSize(r, c, visitedCells) {
    // if the cell is out of bounds
    if (r === HEIGHT || r < 0 || c === WIDTH || c < 0) {
      return 0;
    }

    // no extra land is found at a water cell
    if (grid[r][c] === 0) {
      return 0;
    }

    // if we already visited this cell, don't double count it
    if (visited[r][c]) {
      return 0;
    }

    visited[r][c] = true; // so we don't double count
    visitedCells.push([r, c]); // so we can set every cell later to contain the size and idx

    // iterate to adjacent cells
    let adjacentSizes = 0;
    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];
    for (const [rowDiff, colDiff] of diffs) {
      const newR = r + rowDiff;
      const newC = c + colDiff;
      adjacentSizes += getIslandSize(newR, newC, visitedCells);
    }

    return 1 + adjacentSizes;
  }

  let islandIdx = 0;

  // dfs through every root cell that wasn't previously seen, populating the island info table
  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      const visitedFromRoot = []; // the entire island
      // only process root cells we haven't already visited
      if (visited[r][c]) {
        continue;
      }
      const rootSize = getIslandSize(r, c, visitedFromRoot);
      for (const tuple of visitedFromRoot) {
        const [islandCellRow, islandCellCol] = tuple;
        islandInfo[islandCellRow][islandCellCol] = [rootSize, islandIdx];
      }
      islandIdx++;
    }
  }

  let result = 0;

  // dfs through every tile, trying to flip it
  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      // skip land
      if (grid[r][c] === 1) {
        continue;
      }
      let seenIdxs = []; // we will check all 4 adjacencies, only counting the size for the first time if we haven't seen that island

      let totalSizeIfWeFlipThisTile = 1;

      const diffs = [
        [1, 0],
        [-1, 0],
        [0, 1],
        [0, -1],
      ];
      for (const [rowDiff, colDiff] of diffs) {
        const newR = r + rowDiff;
        const newC = c + colDiff;
        if (
          newR >= 0 &&
          newR < HEIGHT &&
          newC >= 0 &&
          newC < WIDTH &&
          islandInfo[newR][newC] !== null
        ) {
          const adjacentData = islandInfo[newR][newC];
          const [islandSize, islandIdx] = adjacentData;
          // if this is a new island idx, add the island size
          if (!seenIdxs.includes(islandIdx)) {
            totalSizeIfWeFlipThisTile += islandSize;
            seenIdxs.push(islandIdx);
          }
        }
      }
      result = Math.max(result, totalSizeIfWeFlipThisTile);
    }
  }

  return result === 0 ? HEIGHT * HEIGHT : result; // edge case, if every tile were land there is nothing to flip
};
