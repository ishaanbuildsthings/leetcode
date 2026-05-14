// https://leetcode.com/problems/pacific-atlantic-water-flow/description/
// Difficulty: Medium
// tags: graphs, matrix dfs

// Problem
/*
Simplified:
We have an nxm height map. The top and left sides border the pacific, the bottom and right sides border the atlantic. It rains on this height map, and water can flow to <= height neighboring cells. Find the set of cells that can reach both oceans.

Detailed:
There is an m x n rectangular island that borders both the Pacific Ocean and Atlantic Ocean. The Pacific Ocean touches the island's left and top edges, and the Atlantic Ocean touches the island's right and bottom edges.

The island is partitioned into a grid of square cells. You are given an m x n integer matrix heights where heights[r][c] represents the height above sea level of the cell at coordinate (r, c).

The island receives a lot of rain, and the rain water can flow to neighboring cells directly north, south, east, and west if the neighboring cell's height is less than or equal to the current cell's height. Water can flow from any cell adjacent to an ocean into the ocean.

Return a 2D list of grid coordinates result where result[i] = [ri, ci] denotes that rain water can flow from cell (ri, ci) to both the Pacific and Atlantic oceans.
*/

// Solution 1, I think it is O(n*m) time average, but potentially higher worst case, it is a little unclear based on the caching. and O(n*m) space, matrix dfs from island, brute force with caching
// * Solution 2, we iterate from the edges, seeing which cells we can reach. Now, we don't need to repeat inner cells, making it definitely O(n*m) time.
/*
The naive solution is to do a dfs from each cell, seeing which oceans we can reach. Then, we check the cells that can reach both oceans. In the worst case, an upper bound could be m*n*m*n, since we do m*n iterations, and each iteration checks m*n cells. One thing we can do is, as we check if we reach an ocean, if other cells also reached that ocean, we can update those too. For instance:

5 5 5 5 5
1 3 4 5 5
5 5 5 5 5

Here, the 4 can reach the ocean. But we also know the 3 can, since the 4 reaches the ocean through the 3. This means when we solve for the 4, we can solve for the 3, and skip that later.

This follows a very basic recursive pattern: A cell can reach the ocean, if any of its neighbors that it flows to, can reach the ocean. And our base case is if we are at the border.

This does NOT mean that every cell we flow to reaches the ocean, consider:

5 5 5 5
1 3 2 5
5 5 5 5

When we solve for 3, it reaches the ocean through the 1. We also flowed to the 2, but the 2 doesn't necessarily reach the ocean. There might be some tricks with checking if the 2 is the same height as the 3, but I think that doesn't work since I believe I tried similar ideas in trapping rainwater II.

Since water can flow to equal height cells, we maintain a visited table so we don't recurse back and forth between the same cells forever.

When we solve for a root cell, we also might solve for other cells that can flow to the ocean. However, we cannot necessarily say those other cells CANNOT reach the ocean, for instance:

5 5 5 5
5 3 3 2
5 5 5 5

If we solve for the second 3, we flow to the first 3. The first 3 can technically flow out the right, but wouldn't see it in that loop, as the second 3 is already visited.

What this means is:
1) As we solve a root cell, we can potentially solve other cells that also reached the ocean, based on the path we took.
2) Once a root cell is solved, we know if it either can or cannot reach the ocean. If a future cell reaches this cell, we can skip it if it couldn't reach the ocean, or we can immediately say the new root cell can reach the ocean.
*/

var pacificAtlantic = function (heights) {
  const HEIGHT = heights.length;
  const WIDTH = heights[0].length;

  // checks if a cell can reach the pacific. later, if we flow to a cell that can, we know we can. however, if we flow to a cell that cannot, it does not mean our root cell cannot. additionally, if we can reach the pacific, it does not mean all cells we flow to, can.
  const canReachP = new Set(); // stores by WIDTH*row + col
  const canReachA = new Set();

  // helps us track a water flow, since water can flow on even heights, we don't want to recurse back and forth forever. we will reuse this matrix for checking the pacific, and the atlantic.
  const visited = new Array(HEIGHT)
    .fill()
    .map(() => new Array(WIDTH).fill(false));

  // checks if a given cell can reach a specific ocean. if does this by recursing to neighbors, seeing if they can reach the ocean, and so on. or the base case where we flow to the edge.
  function recurse(r, c, ocean, canReachOceanSet) {
    const key = WIDTH * r + c;

    // if we are on an edge, we can reach a certain ocean
    if (ocean === "pacific") {
      if (r === 0 || c === 0) {
        canReachOceanSet.add(key);
      }
    } else if (ocean === "atlantic") {
      if (r === HEIGHT - 1 || c === WIDTH - 1) {
        canReachOceanSet.add(key);
      }
    }

    // if we already saw we could flow to the ocean, we return true as well
    if (canReachOceanSet.has(key)) {
      return true;
    }

    visited[r][c] = true;

    // otherwise, check all adjacent cells that are in range, not yet visited, and have <= heights
    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    let canThisCellReachOcean = false;

    for (const [rowDiff, colDiff] of diffs) {
      const newR = r + rowDiff;
      const newC = c + colDiff;
      if (
        newR >= 0 &&
        newR < HEIGHT &&
        newC >= 0 &&
        newC < WIDTH &&
        !visited[newR][newC] &&
        heights[newR][newC] <= heights[r][c]
      ) {
        const canNeighborReachOcean = recurse(
          newR,
          newC,
          ocean,
          canReachOceanSet
        );
        if (canNeighborReachOcean) {
          canThisCellReachOcean = true;
          break;
        }
      }
    }

    visited[r][c] = false;

    if (canThisCellReachOcean) {
      canReachOceanSet.add(key);
      return true;
    }

    return false;
  }

  for (let r = 0; r < HEIGHT; r++) {
    for (let c = 0; c < WIDTH; c++) {
      recurse(r, c, "pacific", canReachP);
      recurse(r, c, "atlantic", canReachA);
    }
  }

  const result = [];

  for (const key of Array.from(canReachP)) {
    if (canReachA.has(key)) {
      const rowIndex = Math.floor(key / WIDTH);
      const colIndex = key - rowIndex * WIDTH;
      result.push([rowIndex, colIndex]);
    }
  }

  return result;
};
