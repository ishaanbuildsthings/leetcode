// https://leetcode.com/problems/nim-game/description/
// Difficulty: Easy
// tags: dynamic programming 1d

// Problem

var canWinNim = function (n) {
  if (n % 4 === 0) {
    return false;
  }
  return true;
};
