// https://leetcode.com/problems/find-the-substring-with-maximum-cost/description/
// Difficulty: Medium
// tags: kadane's

// Problem
/*
Simplified:
Input: s = "adaa", chars = "d", vals = [-1000]
Output: 2
Explanation: The value of the characters "a" and "d" is 1 and -1000 respectively.
The substring with the maximum cost is "aa" and its cost is 1 + 1 = 2.
It can be proven that 2 is the maximum cost.

Detailed:
You are given a string s, a string chars of distinct characters and an integer array vals of the same length as chars.

The cost of the substring is the sum of the values of each character in the substring. The cost of an empty string is considered 0.

The value of the character is defined in the following way:

If the character is not in the string chars, then its value is its corresponding position (1-indexed) in the alphabet.
For example, the value of 'a' is 1, the value of 'b' is 2, and so on. The value of 'z' is 26.
Otherwise, assuming i is the index where the character occurs in the string chars, then its value is vals[i].
Return the maximum cost among all substrings of the string s.
*/

// Solution, O(n) time and O(1) space. Generate a cost map for all the letters. Iterate over the string and maintain a prefix cost, whenever it drops below 0 reset the prefix, typical kadane's.

const LETTERS = "abcdefghijklmnopqrstuvwxyz";
var maximumCostSubstring = function (s, chars, vals) {
  const mapping = {};
  for (let i = 1; i <= 26; i++) {
    const letter = LETTERS[i - 1];
    mapping[letter] = i;
  }

  for (let i = 0; i < chars.length; i++) {
    const char = chars[i];
    mapping[char] = vals[i];
  }

  let maxValue = 0;
  let runningValue = 0;
  for (let i = 0; i < s.length; i++) {
    const char = s[i];
    const charValue = mapping[char];
    runningValue += charValue;
    if (runningValue < 0) {
      runningValue = 0;
    }
    maxValue = Math.max(maxValue, runningValue);
  }

  return maxValue;
};
