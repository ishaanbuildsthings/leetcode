// https://leetcode.com/problems/sort-the-matrix-diagonally/description/
// difficulty: Medium

// Problem
/*
NOTE: It is best to see the image to understand.

A matrix diagonal is a diagonal line of cells starting from some cell in either the topmost row or leftmost column and going in the bottom-right direction until reaching the matrix's end. For example, the matrix diagonal starting from mat[2][0], where mat is a 6 x 3 matrix, includes cells mat[2][0], mat[3][1], and mat[4][2].

Given an m x n matrix mat of integers, sort each matrix diagonal in ascending order and return the resulting matrix.
*/

// Solution, (m+n)* root(m^2 + n^2) * log(root(m^2 + n^2)) time, O(sort(root(m^2 + n^2))) space
/*
Iterate over m+n diagonals, of worst size root(m^2 + n^2). For each diagonal, sort it and put it back in the matrix. Sorting takes root(m^2 + n^2) * log(root(m^2 + n^2)) time, and we do this for m+n diagonals, so (m+n)* root(m^2 + n^2) * log(root(m^2 + n^2)) time. Worst case our space is O(sort(root(m^2 + n^2)))
*/

var diagonalSort = function (mat) {
  const HEIGHT = mat.length;
  const WIDTH = mat[0].length;

  // start leftmost column
  for (let r = HEIGHT - 1; r >= 0; r--) {
    let c = 0; // start at the 0th column
    const numbersInDiagonal = [];
    let rowIterator = r;
    while (true) {
      numbersInDiagonal.push(mat[rowIterator][c]);
      rowIterator++;
      c++;
      if (rowIterator === HEIGHT || c === WIDTH) {
        break;
      }
    }

    numbersInDiagonal.sort((a, b) => a - b);

    // readd the numbers
    let i = 0; // tracks where we are in the numbersInDiagonal
    rowIterator = r;
    c = 0;
    while (true) {
      mat[rowIterator][c] = numbersInDiagonal[i];
      i++;
      rowIterator++;
      c++;
      // stop when we run out of numbers to add
      if (i === numbersInDiagonal.length) {
        break;
      }
    }
  }

  // do first row (column starts at 1)
  for (let c = 1; c < WIDTH; c++) {
    let r = 0;
    let colIterator = c;
    const numbersInDiagonal = [];
    while (true) {
      numbersInDiagonal.push(mat[r][colIterator]);
      colIterator++;
      r++;
      if (colIterator === WIDTH || r === HEIGHT) {
        break;
      }
    }

    numbersInDiagonal.sort((a, b) => a - b);

    // readd the numbers
    let i = 0;
    colIterator = c;
    r = 0;
    while (true) {
      mat[r][colIterator] = numbersInDiagonal[i];
      i++;
      r++;
      colIterator++;
      if (i === numbersInDiagonal.length) {
        break;
      }
    }
  }

  return mat;
};
