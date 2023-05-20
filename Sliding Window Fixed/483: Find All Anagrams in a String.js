// https://leetcode.com/problems/find-all-anagrams-in-a-string/description/
// Difficulty: Medium
// sliding window fixed

// Problem
/*
Simplified:
Input: s = "cbaebabacd", p = "abc"
Output: [0,6]

Detailed:
Given two strings s and p, return an array of all the start indices of p's anagrams in s. You may return the answer in any order.

An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.
*/

// Solution: Time: O(n), Space: O(n)
/*
First, creating a mapping of letters for p to how many times they occur. Then set up the initial fixed window and create an s mapping. Every time we reach the right amount of letters in p for the first time, update our have count, indicating we have that many letters. Enter a while loop where we iterate over s. When we get a new letter, see if it puts us at exactly our have count. When we lose a letter, see if it dropped us from our have count. If we process letters that weren't in p at all (rather than just skipping them, which is a minor optimization), make sure our map is set up to handle that, since the key for that letter might not exist. It doesn't matter if we exceed the frequency needed for a given letter, because it's impossible to get a full string match while a frequency is exceeded, given our fixed window is the same length as p. We can also use an O(n) solution where we stringify the maps on both iterations, since the map contains 26 k:v pairs, but that is still worse.
*/
var findAnagrams = function (s, p) {
  let need = 0; // represents the total number of letter types we need to match the frequencies for in p

  const pMap = {}; // trying to match to this target
  for (const letter of p) {
    if (letter in pMap) {
      pMap[letter]++;
    } else {
      pMap[letter] = 1;
      need++;
    }
  }

  let have = 0;
  // construct the initial window
  const sMap = {}; // changes as we iterate
  for (let i = 0; i < p.length; i++) {
    const letter = s[i];
    if (letter in sMap) {
      sMap[letter]++;
    } else {
      sMap[letter] = 1;
    }
    // after we add our letter, if we reach the exact frequency for the first time, we add to our have count
    if (sMap[letter] === pMap[letter]) {
      have++;
    }
  }

  const result = [];

  // fixed sliding window
  let l = 0;
  let r = p.length - 1;
  while (r < s.length) {
    if (have === need) {
      result.push(l);
    }

    r++;
    l++;

    if (r === s.length) break; // don't update our maps anymore as we broke the boundary

    const lostLetter = s[l - 1];
    sMap[lostLetter] -= 1;
    // if we just lost the amount we needed, we had a letter before but now we don't
    if (sMap[lostLetter] === pMap[lostLetter] - 1) {
      have--;
    }

    const gainedLetter = s[r];
    if (gainedLetter in sMap) {
      sMap[gainedLetter]++;
    } else {
      sMap[gainedLetter] = 1;
    }

    if (sMap[gainedLetter] === pMap[gainedLetter]) {
      have++;
    }
  }

  return result;
};

// cca

// ccc
// have=1

// c
// ccd

// c
// cda
// have=0, but + 1
