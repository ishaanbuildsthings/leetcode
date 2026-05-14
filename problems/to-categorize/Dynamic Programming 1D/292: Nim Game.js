// https://leetcode.com/problems/nim-game/description/
// Difficulty: Easy
// tags: dynamic programming 1d

// Problem
/*
You are playing the following Nim Game with your friend:

Initially, there is a heap of stones on the table.
You and your friend will alternate taking turns, and you go first.
On each turn, the person whose turn it is will remove 1 to 3 stones from the heap.
The one who removes the last stone is the winner.
Given n, the number of stones in the heap, return true if you can win the game assuming both you and your friend play optimally, otherwise return false.
*/

// Solution, O(1) time and space
/*
You could solve this with dp, but the constraint is n < 2^32 - 1. Instead, just understand that we can force a winning state by setting our opponent to a losing state, for all stone counts that aren't divisible by 4.
*/
var canWinNim = function (n) {
  if (n % 4 === 0) {
    return false;
  }
  return true;
};
