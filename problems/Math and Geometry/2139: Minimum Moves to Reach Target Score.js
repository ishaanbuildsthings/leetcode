// https://leetcode.com/problems/minimum-moves-to-reach-target-score/description/
// difficulty: Medium

// Problem
/*
You are playing a game with integers. You start with the integer 1 and you want to reach the integer target.

In one move, you can either:

Increment the current integer by one (i.e., x = x + 1).
Double the current integer (i.e., x = 2 * x).
You can use the increment operation any number of times, however, you can only use the double operation at most maxDoubles times.

Given the two integers target and maxDoubles, return the minimum number of moves needed to reach target starting with 1.
*/

// Solution O(log n) time, O(1) space
/*
Instead of determine to add one or not, it's easier to just work backwards (common theme in bit style problems of the same nature).

If even, and doubles left, have it.
If odd, subtract one.
If no doubles left, just take the remaining amount.

Worst case we have to keep halving it, so log n time.
*/

var minMoves = function (target, maxDoubles) {
  let current = target;
  let remainingDoubles = maxDoubles;
  let result = 0;
  while (current > 1) {
    // time optimization
    if (remainingDoubles === 0) {
      return result + current - 1;
    }
    // if we have an even number, halve it if we can
    if (current % 2 === 0) {
      if (remainingDoubles > 0) {
        remainingDoubles--;
        current = current / 2;
      } else {
        current--;
      }
    } else {
      current--;
    }
    result++;
  }
  return result;
};
