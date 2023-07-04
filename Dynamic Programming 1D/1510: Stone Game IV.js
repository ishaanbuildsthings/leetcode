// https://leetcode.com/problems/stone-game-iv/description/
// Difficulty: Hard
// tags: dynamic programming 1d

// Problem
/*
Example:
Input: n = 2
Output: false
Explanation: Alice can only remove 1 stone, after that Bob removes the last one winning the game (2 -> 1 -> 0).

Detailed:
Alice and Bob take turns playing a game, with Alice starting first.

Initially, there are n stones in a pile. On each player's turn, that player makes a move consisting of removing any non-zero square number of stones in the pile.

Also, if a player cannot make a move, he/she loses the game.

Given a positive integer n, return true if and only if Alice wins the game otherwise return false, assuming both players play optimally.
*/

// Solution, O(n*root n) time, O(n)
