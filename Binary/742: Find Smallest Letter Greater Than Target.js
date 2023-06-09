// https://leetcode.com/problems/find-smallest-letter-greater-than-target/description/
// Difficulty: Easy
// tags: binary search

// Problem
/*
Simplified:
Input: letters = ["c","f","j"], target = "a"
Output: "c"
Explanation: The smallest character that is lexicographically greater than 'a' in letters is 'c'.
Detailed:
You are given an array of characters letters that is sorted in non-decreasing order, and a character target. There are at least two different characters in letters.

Return the smallest character in letters that is lexicographically greater than target. If such a character does not exist, return the first character in letters.
*/

// Solution, O(log n) time and O(1) space
/*
Standard binary search. We could also use l <= r to consider all numbers, then check if the left pushed all the way outside the right of the array.
*/

function getNum(char) {
  return char.charCodeAt(0);
}

var nextGreatestLetter = function (letters, target) {
  const targetNum = getNum(target);

  let l = 0;
  let r = letters.length - 1;
  while (l < r) {
    const m = Math.floor((r + l) / 2);
    const letter = letters[m];
    const letterCode = getNum(letter);
    // if the letter we see is too small or equal, consider only the right
    if (letterCode <= targetNum) {
      l = m + 1;
    }
    // if the letter is too big, consider the left as well as the big character
    else {
      r = m;
    }
  }

  if (getNum(letters[l]) <= targetNum) {
    return letters[0];
  }

  return letters[l];
};
