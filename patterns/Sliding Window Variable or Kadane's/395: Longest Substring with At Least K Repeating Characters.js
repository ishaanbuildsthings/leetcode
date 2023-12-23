// https://leetcode.com/problems/longest-substring-with-at-least-k-repeating-characters/description/
// Difficulty: Medium
// tags: sliding window variable

// Problem
/*
Given a string s and an integer k, return the length of the longest substring of s such that the frequency of each character in this substring is greater than or equal to k.
Input: s = "ababbc", k = 2
Output: 5
Explanation: The longest substring is "ababb", as 'a' is repeated 2 times and 'b' is repeated 3 times.
*/

// Solution, O(n) time and O(1) space, since our mapping is bound by 26 letters
/*
First, count the number of unique letters in s, for instance ababbc has 3. We will try allowing for only 1 unique letter, then 2, then 3. The upper bound is 26, so 26n.
Create a sliding window that only allows one unique letter, iterate, maintain a have and need count, as well as how many unique letters our window currently has. When we exceed the # unique allowed, start decrementing. If our have count equals need count, update max length.
*/
// * Solution 2, I also tried a divide and conquer approach which is normally nlogn average and n^2 worst case (think quick sort), I'm still not fully convinced those restrictions apply to this problem since I couldn't think of worst case scenarios.

var longestSubstring = function (s, k) {
  // determine number of unique letters
  const letters = new Set();
  for (const char of s) {
    letters.add(char);
  }
  const diffLetters = Array.from(letters).length;

  let maxLength = 0;

  // try up to 26 iterations, each with a different amount of allowed letters
  for (let i = 1; i <= diffLetters; i++) {
    let have = 0; // how many letters we have met the frequency for
    let need = i; // how many letters we need to meet the frequency for, bounded by # of allowed letters
    let size = 0; // tells us when we have seen too many new letters
    const mapping = {};
    let l = 0;
    let r = 0;
    while (r < s.length) {
      const letter = s[r];
      // add letter
      if (!(letter in mapping)) {
        mapping[letter] = 1;
        size++;
      } else {
        // in case we added a letter then removed it, we can't just check if the letter exists in the mapping as a key to determine if it is new
        if (mapping[letter] === 0) {
          size++;
        }
        mapping[letter]++;
      }

      // while we have too many letters, decrement from the left
      while (size > i && l < r) {
        l++;
        mapping[s[l - 1]]--;
        if (mapping[s[l - 1]] === 0) {
          size--;
        }
        if (mapping[s[l - 1]] === k - 1) {
          have--;
        }
      }
      // if we have exactly enough of the new letter we added, we gain a have
      if (mapping[letter] === k) {
        have++;
      }

      if (have === need) {
        maxLength = Math.max(maxLength, r - l + 1);
      }
      r++;
    }
  }
  return maxLength;
};
