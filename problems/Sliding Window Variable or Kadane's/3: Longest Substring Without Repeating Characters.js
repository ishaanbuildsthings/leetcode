// https://leetcode.com/problems/longest-substring-without-repeating-characters/description/
// Difficulty: Medium
// tags: sliding window variable

// Problem
/*
Given a string s, find the length of the longest substring without repeating characters.
*/

// Solution
// O(n) time and O(1) space. The space is constant since it holds at most one instance of any possible english character.  We create a set that will track the current characters in the window, and two pointers starting at the beginning. As soon as we reach a new character, check if it is in the set. If it isn't, get a new size and increment r. If it is, we need to start decrementing from the left until we remove that characters. For instance "abcsdefsg". When we hit the second s, we need to decrement from the left until the left reaches right past the initial s. As we decrement, remove those characters from the set. We only need to remove it once since the window cannot contain two of the same character (otherwise we would've moved the window).

const lengthOfLongestSubstring = function (s) {
  let l = 0;
  let r = 0;
  let currentCharacters = new Set();
  let longestSize = 0;
  while (r < s.length) {
    const char = s[r];
    // undesirable character
    if (currentCharacters.has(char)) {
      while (s[l] !== char) {
        currentCharacters.delete(s[l]);
        l++;
      }
      l++;
    }
    // desirable
    else {
      currentCharacters.add(char);
      longestSize = Math.max(longestSize, r - l + 1);
    }
    r++;
  }
  return longestSize;
};
