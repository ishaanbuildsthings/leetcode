// https://leetcode.com/problems/remove-vowels-from-a-string/description/
// Difficulty: Easy

// Problem
/*
Given a string s, remove the vowels 'a', 'e', 'i', 'o', and 'u' from it, and return the new string.
*/

// Solution, O(n) time and O(n) space since we form an array first and then form a string
const VOWELS = ["a", "e", "i", "o", "u"];

var removeVowels = function (s) {
  return s
    .split("")
    .filter((char) => !VOWELS.includes(char))
    .join("");
};
