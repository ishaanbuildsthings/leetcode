// https://leetcode.com/problems/letter-combinations-of-a-phone-number/description/
// Difficulty: Medium
// tags: backtracking

// Problem
/*
Simplified:
Input: digits = "23"
Output: ["ad","ae","af","bd","be","bf","cd","ce","cf"]

Detailed:
Given a string containing digits from 2-9 inclusive, return all possible letter combinations that the number could represent. Return the answer in any order.

A mapping of digits to letters (just like on the telephone buttons) is given below. Note that 1 does not map to any letters.
*/

// Solution, O(n * 4^n) time. O(n) space.
/*
Create a backtracking function. We will walk through every index of digits. For each index, try all possible letters. We terminate when we have finished all digits.

If there are n digits, each digit has at most 4 letters. So there are 4^n possible solutions. Each one takes n time to serialize. We also need n space for the callstack.
*/

const mapping = {
  2: ["a", "b", "c"],
  3: ["d", "e", "f"],
  4: ["g", "h", "i"],
  5: ["j", "k", "l"],
  6: ["m", "n", "o"],
  7: ["p", "q", "r", "s"],
  8: ["t", "u", "v"],
  9: ["w", "x", "y", "z"],
};

var letterCombinations = function (digits) {
  // edge case, problem expects an empty array as opposed to [""]
  if (digits.length === 0) {
    return [];
  }

  const result = [];

  // index will track which digit we are considering. we will try all possible values of that digit
  function backtrack(currentLetters, index) {
    // base case, we have reached all digits, serialize and terminate
    if (index === digits.length) {
      result.push(currentLetters.join(""));
      return;
    }

    const number = Number(digits[index]);
    const letterOptions = mapping[number];

    for (const letter of letterOptions) {
      currentLetters.push(letter);
      backtrack(currentLetters, index + 1);
      currentLetters.pop();
    }
  }

  backtrack([], 0);

  return result;
};
