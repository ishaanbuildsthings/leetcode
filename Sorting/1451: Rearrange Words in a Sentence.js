// https://leetcode.com/problems/rearrange-words-in-a-sentence/description/
// Difficulty: Medium
// tags: bucket sort

// Problem
/*
Simplified:
Input: text = "Leetcode is cool"
Output: "Is cool leetcode"
Explanation: There are 3 words, "Leetcode" of length 8, "is" of length 2 and "cool" of length 4.
Output is ordered by length and the new first word starts with capital letter.

Detailed
Given a sentence text (A sentence is a string of space-separated words) in the following format:

First letter is in upper case.
Each word in text are separated by a single space.
Your task is to rearrange the words in text such that all words are rearranged in an increasing order of their lengths. If two words have the same length, arrange them in their original order.

Return the new text following the format shown above.
*/

// Solution 1, bucket sort, time: O(n), where n is the length of the text. We have to iterate over all letters of the text to populate our mapping. Then later, we iterate over all possible unique word lengths, which is bounded by the length of text anyway. I didn't use a deque but we could have. Space: O(n), where n is the length of the text, since we may hold that many characters in our mapping.
/*
Iterate over a words array, populating a mapping of word lengths to words of that length. Then iterate again starting from the shortest word to the longest.
*/

var arrangeWords = function (text) {
  const words = text.split(" ");
  words[0] = words[0].toLowerCase();

  // help create bounds for later
  let longestWord = -Infinity;
  let shortestWord = Infinity;

  const mapping = {}; // maps lengths to a list of words of that length

  for (const word of words) {
    // populate bounds
    if (word.length > longestWord) {
      longestWord = word.length;
    }
    // no else statement as initial word should affect both
    if (word.length < shortestWord) {
      shortestWord = word.length;
    }

    // populate mapping
    if (word.length in mapping) {
      mapping[word.length].push(word);
    } else {
      mapping[word.length] = [word];
    }
  }

  const result = [];

  for (let i = shortestWord; i <= longestWord; i++) {
    // if we don't have any words of that length
    if (!(i in mapping)) {
      continue;
    }

    const wordArray = mapping[i];

    while (wordArray.length > 0) {
      result.push(wordArray.shift()); // O(1) for deque
    }
  }

  firstChar = result[0].slice(0, 1);
  firstCharCapital = firstChar.toUpperCase();
  const remainingWord = result[0].slice(1);
  const newWord = firstCharCapital + remainingWord;
  result[0] = newWord;

  return result.join(" ");
};

// Solution 2, built in sort. Time is O(n) to populate the words array, and O(m log m) to sort the words, where m is the number of words. At worst there are n words, so O(n log n) time. Space is also O(n).

var arrangeWords = function (text) {
  const words = text.split(" ");
  words[0] = words[0].toLowerCase(); // handle edge case

  words.sort((a, b) => {
    if (a.length < b.length) {
      return -1;
    } else if (a.length === b.length) {
      return 0;
    }
    return 1;
  });

  const firstWordfirstLetter = words[0].slice(0, 1);
  const capitalChar = firstWordfirstLetter.toUpperCase();
  const remainingWord = words[0].slice(1);
  const newWord = capitalChar + remainingWord;
  words[0] = newWord;

  return words.join(" ");
};
