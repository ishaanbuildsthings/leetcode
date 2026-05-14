//https://leetcode.com/problems/encode-and-decode-strings/description/
// Difficulty: Medium

// Problem
/*
Design an algorithm to encode a list of strings to a string. The encoded string is then sent over the network and is decoded back to the original list of strings.
*/

// Other solutions include using a non-ascii delimiter which has better time complexity, or converting the length of the string to binary and then padding it (you can not convert it too). We can also use a function that accepts the prefix amount and that many following characters, parses out the next string with .slice, then returns the next index to start from, which is a bit simpler to follow than using the for in my solution.

// Solution
// O(n) time and O(1) space. Iterate over the array, for each word, determine the length, construct the prefix, and add it out our result string.
var encode = function (strs) {
  let result = "";
  for (const word of strs) {
    const length = word.length;
    const prefix = length + ":";
    result += prefix + word;
  }
  return result;
};

// O(n) time and O(1) space. Iterate over the string, and accumulate the prefix-number. Once we have that, run an inner for loop to gather the word. Add the word to our result array. Move the outer loop to the end of that word and continue. The inner for loop can only run up to 4 times per word, since the prefix is at most 4 digits long (length of words are capped at 200).
var decode = function (s) {
  const words = [];
  let number = "";
  // iterate over characters, figuring out the prefix
  for (let i = 0; i < s.length; i++) {
    // if we have a number, add it
    if (s[i] !== ":") {
      number += s[i];
    } else if (s[i] === ":") {
      let word = "";
      let j;
      for (j = i + 1; j < i + 1 + Number(number); j++) {
        word += s[j];
      }
      words.push(word);
      number = "";
      i = j - 1;
    }
  }
  return words;
};
