// https://leetcode.com/problems/guess-number-higher-or-lower/description/
// Difficulty: Easy
// tags: binary search

// Problem
/*
Simplifed: Guess a number from 1 to n, every time get feedback on higher or lower, find the number
*/

// Solution, just a normal time: O(log n), space: O(1) binary search

var guessNumber = function (n) {
  let l = 1;
  let r = n;
  let m = Math.floor((r + l) / 2);
  while (l < r) {
    m = Math.floor((r + l) / 2);
    // our guess is too low, and we need to go strictly up
    if (guess(m) === 1) {
      l = m + 1;
    }
    // our guess is higher than or equal to the number, we need to look to the left, inclusive
    else {
      r = m;
    }
  }
  return l;
};
