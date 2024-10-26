// https://leetcode.com/problems/roman-to-integer/description/
// Difficulty: Easy
// tags: arrays

// Solution, O(1) time and O(1) space. O(1) time since the number of valid roman numerals with the given characters is bounded.
/*
Iterate over the roman numeral string. If the current letter is less than the next number, like IV, add the difference and increment past the second letter. Otherwise just add the value as normal.
*/

const VALUES = {
  I: 1,
  V: 5,
  X: 10,
  L: 50,
  C: 100,
  D: 500,
  M: 1000,
};

var romanToInt = function (s) {
  let result = 0;
  let pointer = 0;
  while (pointer < s.length) {
    const letter = s[pointer];
    const value = VALUES[letter];
    const letterNext = s[pointer + 1];
    const valueNext = VALUES[letterNext];
    if (value < valueNext) {
      result += valueNext - value;
      pointer += 2;
    } else {
      result += value;
      pointer++;
    }
  }
  return result;
};
