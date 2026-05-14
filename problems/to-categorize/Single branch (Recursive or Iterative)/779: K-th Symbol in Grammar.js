// https://leetcode.com/problems/k-th-symbol-in-grammar/description/
// Difficulty: Medium
// tags: single branch (recursive or iterative)

// Problem
/*
We build a table of n rows (1-indexed). We start by writing 0 in the 1st row. Now in every subsequent row, we look at the previous row and replace each occurrence of 0 with 01, and each occurrence of 1 with 10.

For example, for n = 3, the 1st row is 0, the 2nd row is 01, and the 3rd row is 0110.
Given two integer n and k, return the kth (1-indexed) symbol in the nth row of a table of n rows.
*/

// Solution, O(log n) time or O(1) since n is bounded to ~2^30. O(1) space.
/*
The nth number can be deduced:
if even, is is the opposite of the n/2th number, else it is the same as the ceil(n/2) number.
*/

var kthGrammar = function (n, k) {
  /*
    0
    01
    0110
    01101001



    even->
    divide by two, get the opp
    so 6 is the opposite of the third

    odd->
    divide by two, add one, its that number
    */

  let flipped = false;
  while (k > 1) {
    if (k % 2 === 0) {
      k = k / 2;
      flipped = !flipped;
    } else {
      k = Math.ceil(k / 2);
    }
  }

  if (flipped) {
    return 1;
  }

  return 0;
};
