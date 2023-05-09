// https://leetcode.com/problems/longest-repeating-character-replacement/description/
// Difficulty: Medium
// tags: sliding window variable

// Solution
// O(n) time and O(1) space. Create a constant storage mapping of letters to the number of times they occur in the current window. As we iterate, we update the occurences. We also need to track the maximum frequency character #, for instance "ABBB" has a maximum frequency character of 3 when considering the entire string. This is important because to know if we can change a string to be valid, given k replacements, we can take the length of the string, subtract the maximum frequency (3), and see we only need 1 replacement to make all the non-b characters into b. We then compare this number with k. If our new letter is the most common, we update the maxFrequency, consider "ABB". Once we reach the second B, our most common # is 2, so we know we would only need to change the non-b character, which is 'a', as opposed to something like changing all the 'b' characters. If our maxFrequency isn't big enough once we hit a new character, we just decrement one from the left. Consider "AABB" and we can make at most one change. Once we hit the second b, we drop a character from the left, shortening the string, making our window valid again.
AAAAAAB;

const characterReplacement = function (s, k) {
  let l = 0;
  let r = 0;
  let longestString = 0;
  let maxFrequency = 0;

  const LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const occurences = {};
  for (const letter of LETTERS) {
    occurences[letter] = 0;
  }

  while (r < s.length) {
    occurences[s[r]]++;

    // if our new number is the most common one, track the new max frequency
    if (occurences[s[r]] > maxFrequency) {
      maxFrequency = occurences[s[r]];
    }

    // if the length of our window, minus the maxFreq is > k, we cannot replace all the wrong digits
    // AAAABBB and we are allowed 2 replacements
    // length is 7, but our max frequency is only 4, so we have a problem
    if (r - l + 1 - maxFrequency > k) {
      occurences[s[l]]--;
      l++;
    }
    // our window is valid
    else {
      longestString = Math.max(longestString, r - l + 1);
    }

    r++;
  }
  return longestString;
};
