// https://leetcode.com/problems/buddy-strings/description/
// difficulty: Easy

// Problem
/*
Given two strings s and goal, return true if you can swap two letters in s so the result is equal to goal, otherwise, return false.

Swapping letters is defined as taking two indices i and j (0-indexed) such that i != j and swapping the characters at s[i] and s[j].

For example, swapping at indices 0 and 2 in "abcd" results in "cbad".
*/

// Solution, O(min(len(s), len(goal))) time, O(1) space
/*
Strings are buddy strings if they differ by exactly two characters, or if they differ by none, there is a repeat character.
*/

var buddyStrings = function (s, goal) {
  if (s.length !== goal.length) {
    return false;
  }

  const mismatchedCharPositions = [];
  for (let i = 0; i < s.length; i++) {
    const char1 = s[i];
    const char2 = goal[i];
    if (char1 !== char2) {
      mismatchedCharPositions.push(i);
    }
    if (mismatchedCharPositions.length > 2) {
      return false;
    }
  }

  if (mismatchedCharPositions.length === 0) {
    const chars = new Set();
    for (const char of s) {
      if (chars.has(char)) {
        return true;
      }
      chars.add(char);
    }
    return false;
  }

  if (mismatchedCharPositions.length === 1) {
    return false;
  }

  if (
    s[mismatchedCharPositions[0]] === goal[mismatchedCharPositions[1]] &&
    s[mismatchedCharPositions[1]] === goal[mismatchedCharPositions[0]]
  ) {
    return true;
  }

  return false;
};
