// https://leetcode.com/problems/search-a-2d-matrix/description/
// Difficulty: Medium
// tags: binary search

// Problem
/*
You are given an m x n integer matrix matrix with the following two properties:

Each row is sorted in non-decreasing order.
The first integer of each row is greater than the last integer of the previous row.
Given an integer target, return true if target is in matrix or false otherwise.

You must write a solution in O(log(m * n)) time complexity.
*/

// Solution
// time complexity: log m + log n, which is log(m*n), space complexity: O(1)
/*
  Do a binary search to find the row number, the correct row number will be the highest possible row whose starting number is still less than our target, due to the nature of the problem. There are a few pitfalls though. The first is that binary search is good at finding the exact value, as we end at only one possible remaining result. We can check if that result is valid. In this case, we are looking for a number smaller than our target, not our target, since if we are searching for a 10, a row starting with a 5 may be acceptable. After we filter down to only one remaining row, there are a few outcomes. The first is the starting value of that row is our exact target, which is good. It often will not be though, which means the row is too large. We decrement one to the left. We may be out of bounds though, what if every row was too large? Then we return false immediately. There is also the case where every row is too small, in which case our final row will be the largest one, which is still acceptable.
*/
// ****** a better solution for finding a row would be to compare the element we are looking for with the largest element of the row we are in, makes the code a bit nicer ******

// * Solution 2, you could also flatten out the array and just do one binary search! Or you can do it in constant space by iterating over all possible elements (n*m), but within the loop query the matrix accordingly.

var searchMatrix = function (matrix, target) {
  if (matrix[0][0] > target) return false;

  // do a binary search to identify the row number
  let l = 0;
  let r = matrix.length - 1;
  let m = Math.floor((r + l) / 2); // errs left, initialize m in case l already equals r

  while (l < r) {
    m = Math.floor((r + l) / 2);
    const middleRow = matrix[m];
    const firstValue = middleRow[0];
    // if the value we find is greater than or equal to the target, we need to search to the left, inclusive
    if (firstValue >= target) {
      r = m;
    }
    // if the value we find is strictly less than the target, we search right
    else {
      l = m + 1;
    }
  }

  /* now, l/r is the last possible row that exactly equals our target, but we are actually searching for a number smaller than the starting target
    so we check if the starting number is too big (it almost always will be, since we consider the left numbers first as our middle pointer errs right, it wouldn't be too big only if it were exactly the number, or all the rows were too small)
    */
  // decrement l if the first number was too big
  if (matrix[l][0] > target) {
    l--;
  }
  // if we were pushed out of bounds, which could happen if we only had one row whose starting number was too big, then return false
  if (l < 0) {
    return false;
  }

  // now l points to the right row
  const correctRow = l;

  let l2 = 0;
  let r2 = matrix[correctRow].length;
  let m2 = Math.floor((r2 + l2) / 2);
  while (l2 < r2) {
    m2 = Math.floor((r2 + l2) / 2);
    const middleValue = matrix[correctRow][m2];
    if (middleValue >= target) {
      r2 = m2;
    } else {
      l2 = m2 + 1;
    }
  }

  if (matrix[correctRow][l2] === target) {
    return true;
  }
  return false;
};
