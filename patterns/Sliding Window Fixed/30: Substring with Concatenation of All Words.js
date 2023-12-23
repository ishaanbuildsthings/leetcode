// https://leetcode.com/problems/substring-with-concatenation-of-all-words/description/
// Difficulty: Hard
// tags: sliding window fixed

// Problem
/*
Simplified:
Input: s = "barfoothefoobarman", words = ["foo","bar"]
Output: [0,9]

Detailed:
You are given a string s and an array of strings words. All the strings of words are of the same length.

A concatenated substring in s is a substring that contains all the strings of any permutation of words concatenated.

For example, if words = ["ab","cd","ef"], then "abcdef", "abefcd", "cdabef", "cdefab", "efabcd", and "efcdab" are all concatenated strings. "acdbef" is not a concatenated substring because it is not the concatenation of any permutation of words.
Return the starting indices of all the concatenated substrings in s. You can return the answer in any order.
*/

// Solution 1, O(n*k (setting indicies) + n*k/n (k loops of length n/k)), which is O(n*k) time, where n is the string length and k is the length of a word, and O(n*k (mapping) + m (number of dinstinct words for windowWords)) space. The comoplexity could even be reduce to O(n*max(k, m)) by implementing one of two solutions based on which is larger

/*
Iterate over each index of the string, populating a hashmap that maps indices to the substrings they create. For instance in 'abcdef', where we have words of length 2, we create a map: {0:'ab', 1:'bc', ...}. This is n*k time but since k is bounded it is linear time.

We create a sliding window of length k*words.length, as we know our pattern will always be of this size. Say our input string is 'abcdef', and our words are ['ab', 'cd']. We start out at the window from a to d. We check all the indicies in that window, starting at 0, and incrementing by word.length, so we check index 0, and index 2. We maintain variables for how many words we have matched, and how many we need, and check if we have equality (constant time). We have found one match, and add 0 to the result array. We then shift the window by word.length, and repeat the process until the end of the string.

We then do the same thing, but starting a sliding window at an offset, so we start at index 1. We repeat this for all indices under a word length. We do these multiple fixed sliding window traversals so that when we slide, we can slide by a fixed amount, and pop off and add on only one element at a time. We do k traversals of n/k, which is n.
*/
// * Solution 2 uses a single window, increments one index at a time, and fully resets the window

var findSubstring = function (s, words) {
  const WORD_LENGTH = words[0].length;
  const map = {}; // store indicies : substrings
  // calculate the substring at every index
  for (let i = 0; i < s.length - WORD_LENGTH + 1; i++) {
    const substring = s.slice(i, i + WORD_LENGTH);
    map[i] = substring;
  }

  // calculate the anagram mapping for our target words
  let size = 0;
  const targetAnagram = {};
  for (const word of words) {
    if (word in targetAnagram) {
      targetAnagram[word]++;
    } else {
      targetAnagram[word] = 1;
      size++;
    }
  }

  const WINDOW_LENGTH = words.length * WORD_LENGTH;
  const result = [];

  function fireSlidingWindow(startingIndex) {
    let l = startingIndex;
    let r = l + WINDOW_LENGTH - 1;
    let have = 0;
    let need = size;

    // populate the initial map
    const windowWords = {};
    for (
      let i = startingIndex;
      i < WINDOW_LENGTH + startingIndex;
      i += WORD_LENGTH
    ) {
      const word = map[i];
      if (word in windowWords) {
        windowWords[word]++;
      } else {
        windowWords[word] = 1;
      }
      if (windowWords[word] === targetAnagram[word]) {
        have++;
      }
    }

    while (r < s.length) {
      if (have === need) {
        result.push(l);
      }
      r += WORD_LENGTH;
      l += WORD_LENGTH;
      const leftWord = map[l - WORD_LENGTH];
      windowWords[leftWord]--;
      if (windowWords[leftWord] === targetAnagram[leftWord] - 1) {
        have--;
      }
      const rightWord = map[r - WORD_LENGTH + 1];
      if (rightWord in windowWords) {
        windowWords[rightWord]++;
      } else {
        windowWords[rightWord] = 1;
      }
      if (windowWords[rightWord] === targetAnagram[rightWord]) {
        have++;
      }
    }
  }

  for (let i = 0; i < WORD_LENGTH; i++) {
    fireSlidingWindow(i);
  }

  return result;
};

// Solution 2, uses a single window, increments one index at a time, and fully resets the window

var findSubstring = function (s, words) {
  const WORD_LENGTH = words[0].length;
  const map = {}; // store indicies : substrings
  // calculate the substring at every index
  for (let i = 0; i < s.length - WORD_LENGTH + 1; i++) {
    const substring = s.slice(i, i + WORD_LENGTH);
    map[i] = substring;
  }

  // calculate the anagram mapping for our target words
  let size = 0;
  const targetAnagram = {};
  for (const word of words) {
    if (word in targetAnagram) {
      targetAnagram[word]++;
    } else {
      targetAnagram[word] = 1;
      size++;
    }
  }

  const WINDOW_LENGTH = words.length * WORD_LENGTH;
  let have = 0;
  let need = size;
  let windowWords = {}; // maps words to how often they appear in our window, so we can check if we have a match with have and need
  // populate the initial map
  for (let i = 0; i < WINDOW_LENGTH; i += WORD_LENGTH) {
    const word = map[i];
    if (word in windowWords) {
      windowWords[word]++;
    } else {
      windowWords[word] = 1;
    }
    if (windowWords[word] === targetAnagram[word]) {
      have++;
    }
  }

  const result = [];
  let l = 0;
  let r = WINDOW_LENGTH - 1;
  // slide the fixed window
  while (r < s.length) {
    if (have === need) {
      result.push(l);
    }
    r++;
    l++;
    windowWords = {};
    have = 0;
    for (let i = l; i < WINDOW_LENGTH + l; i += WORD_LENGTH) {
      const word = map[i];
      if (word in windowWords) {
        windowWords[word]++;
      } else {
        windowWords[word] = 1;
      }
      if (windowWords[word] === targetAnagram[word]) {
        have++;
      }
    }
  }

  return result;
};
