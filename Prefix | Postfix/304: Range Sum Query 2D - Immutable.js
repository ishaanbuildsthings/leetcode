// https://leetcode.com/problems/range-sum-query-2d-immutable/description/
// Difficulty: Medium
// tags: prefix

// Solution
// O(n*m) time to construct the prefix square mapping, O(1) to query. O(n*m) space to store the prefix square mapping.
// Create a prefix sum matrix where each cell represents the sum of the square of elements up and left of it, including that element. To get the sum of a region, we take the cell itself, add the left region, add the top region, and subtract the top left region (which was added twice). To compute a prefix sum, we add the cell to the sum of the left and top regions, and subtract the top left region (which was added twice).

const NumMatrix = function (matrix) {
  // a matrix where each cell of the matrix represents the sum of the square of elements up and left of it, including that element
  this.prefixSquares = [];
  for (let rowNumber = 0; rowNumber < matrix.length + 1; rowNumber++) {
    this.prefixSquares.push(new Array(matrix[0].length + 1).fill(0));
  }

  for (let rowNumber = 0; rowNumber < matrix.length; rowNumber++) {
    for (let colNumber = 0; colNumber < matrix[0].length; colNumber++) {
      this.prefixSquares[rowNumber + 1][colNumber + 1] =
        matrix[rowNumber][colNumber] +
        this.prefixSquares[rowNumber][colNumber + 1] +
        this.prefixSquares[rowNumber + 1][colNumber] -
        this.prefixSquares[rowNumber][colNumber];
    }
  }
};
/*
Intuition behind constructing the prefix squares:

To get the size of this region:
1 1 1 O O
1 1 1 O O
1 1 1 O O
O O O O O

We take the cell itself:
O O O O O
O O O O O
O O 1 O O
O O O O O

Add the left region:
1 1 O O O
1 1 O O O
1 1 O O O
O O O O O

Add the top region:
1 1 1 O O
1 1 1 O O
O O O O O
O O O O O

And subtract the overlapped region:
1 1 O O O
1 1 O O O
O O O O O
O O O O O

The overlapped region itself is a sub-dp problem. We can do it in order so we can reuse the prefix square mapping.


*/

/**
 * @param {number} row1
 * @param {number} col1
 * @param {number} row2
 * @param {number} col2
 * @return {number}
 */
NumMatrix.prototype.sumRegion = function (row1, col1, row2, col2) {
  // the sum of an arbitrary square is equal to the the prefix square of the bottom right cell, minus the sum of the prefix square left of the bottom left, minus the sum of the prefix square above the top right, plus the prefix square up and left of the top left cell
  const bottomRightPrefix = this.prefixSquares[row2 + 1][col2 + 1];
  const aboveTopRightPrefix = this.prefixSquares[row1][col2 + 1];
  const leftOfBottomLeftPrefix = this.prefixSquares[row2 + 1][col1];
  const upAndLeftOfTopLeftPrefix = this.prefixSquares[row1][col1];
  return (
    bottomRightPrefix -
    aboveTopRightPrefix -
    leftOfBottomLeftPrefix +
    upAndLeftOfTopLeftPrefix
  );
};

/*
Intuition behind querying the sum region

Say this region is queried
O O O O O
O O 1 1 O
O O 1 1 O
O O O O O

Take the whole region:
1 1 1 1 O
1 1 1 1 O
1 1 1 1 O
O O O O O

Subtract the left region:
1 1 O O O
1 1 O O O
1 1 O O O
O O O O O

Subtract the top region:
1 1 1 1 O
O O O O O
O O O O O
O O O O O

Add the overlapped region:
1 1 O O O
O O O O O
O O O O O
O O O O O

*/

/**
 * Your NumMatrix object will be instantiated and called as such:
 * var obj = new NumMatrix(matrix)
 * var param_1 = obj.sumRegion(row1,col1,row2,col2)
 */
