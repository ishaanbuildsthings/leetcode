// https://leetcode.com/problems/number-of-islands-ii/description/
// Difficulty: Hard
// Tags: Graphs, Union Find, undirected, unconnected

// Problem
/*
You are given an empty 2D binary grid grid of size m x n. The grid represents a map where 0's represent water and 1's represent land. Initially, all the cells of grid are water cells (i.e., all the cells are 0's).

We may perform an add land operation which turns the water at position into a land. You are given an array positions where positions[i] = [ri, ci] is the position (ri, ci) at which we should operate the ith operation.

Return an array of integers answer where answer[i] is the number of islands after turning the cell (ri, ci) into a land.

An island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.
*/

// Solution, O(positions) time, O(positions) space
/*
Essentially, as we add nodes, we need to know how many connected components we have. We will use the union find class.

Create the union find object, which will track the parents of nodes, and the ranks of parents.

Iterate over each position which we turn from water into land. For a given position, first check it's not already land. If it's already land, it has a registered parent in the union find, and we skip this node.

If it was water, create the node by setting the parent of the node to itself. Also increment the number of islands by 1, since we gained an island. Now, union it with the adjacent cells. We first check if an adjacent cell is in bounds (otherwise we skip, since we might get a bad hash collision) and that it is land. If we are able to union, we lose an island.

During the union, we find the parent representatives of both nodes. We also find their ranks, and assign the smaller parent as a child of the bigger one. We use path compression during the find to amortize the time complexity.
*/

class UnionFind {
  constructor() {
    this.parents = {}; // maps a cell to its parent, we will use COLS * r + c
    this.ranks = {}; // maps a representative cell to its island size
  }

  find(node) {
    // node is COLS * r + c
    let current = node;
    while (this.parents[current] !== current) {
      const tempParent = this.parents[current];
      this.parents[current] = this.parents[tempParent];
      current = tempParent;
    }
    return current;
  }

  union(node1, node2) {
    const parent1 = this.find(node1);
    const parent2 = this.find(node2);

    const rank1 = this.ranks[parent1];
    const rank2 = this.ranks[parent2];

    // if they're already unioned, return false, the union was unsuccessful
    if (parent1 === parent2) {
      return false;
    }

    if (rank1 < rank2) {
      this.parents[parent1] = parent2;
      delete this.ranks[parent1];
    } else if (rank1 > rank2) {
      this.parents[parent2] = parent1;
      delete this.ranks[parent2];
    } else {
      this.parents[parent2] = parent1;
      delete this.ranks[parent2];
      this.ranks[parent1]++; // if the trees have the same rank, the size must increase by 1
    }

    return true;
  }
}

var numIslands2 = function (m, n, positions) {
  const unionFind = new UnionFind();

  const result = [];

  let uniqueIslands = 0;

  for (const [r, c] of positions) {
    const hash = n * r + c;

    // if we already processed this cell, don't do it again
    if (unionFind.parents[hash] !== undefined) {
      result.push(uniqueIslands);
      continue;
    }

    unionFind.parents[hash] = hash;
    unionFind.ranks[hash] = 0;

    uniqueIslands++;

    const diffs = [
      [1, 0],
      [-1, 0],
      [0, 1],
      [0, -1],
    ];

    for (const [rowDiff, colDiff] of diffs) {
      const newRow = r + rowDiff;
      const newCol = c + colDiff;
      const newHash = newRow * n + newCol;

      // if the adjacent cell was never turned into land, we never added it to our unionFind, meaning there's no registered parent
      if (unionFind.parents[newHash] === undefined) {
        continue;
      }

      // if the adjacent cell is out of bounds, we continue, otherwise we get hash collisions
      if (newRow < 0 || newRow >= m || newCol < 0 || newCol >= n) {
        continue;
      }

      /* here, the adjacent cell is land */

      // try to union the two islands
      if (unionFind.union(hash, newHash)) {
        uniqueIslands--;
      }
    }

    result.push(uniqueIslands);
  }

  return result;
};
