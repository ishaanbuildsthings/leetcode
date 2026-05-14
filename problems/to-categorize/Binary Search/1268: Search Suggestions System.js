// https://leetcode.com/problems/search-suggestions-system/description/
// tags: binary search

// Problem
/*
Input: products = ["mobile","mouse","moneypot","monitor","mousepad"], searchWord = "mouse"
Output: [["mobile","moneypot","monitor"],["mobile","moneypot","monitor"],["mouse","mousepad"],["mouse","mousepad"],["mouse","mousepad"]]
Explanation: products sorted lexicographically = ["mobile","moneypot","monitor","mouse","mousepad"].
After typing m and mo all products match and we show user ["mobile","moneypot","monitor"].
After typing mou, mous and mouse the system suggests ["mouse","mousepad"].


You are given an array of strings products and a string searchWord.

Design a system that suggests at most three product names from products after each character of searchWord is typed. Suggested products should have common prefix with searchWord. If there are more than three products with a common prefix return the three lexicographically minimums products.

Return a list of lists of the suggested products after each character of searchWord is typed.
*/

// Solution, O(k*m log m + p*k*log m) time = O(k*log m (m + p)) time. O(sort) + O(k) space.
/*
First, sort the products, which takes k*m log m time, where k is the number of letters in a word, and m is the number of words. This is because the word lengths aren't really capped, unlike numbers, so we must consider the length of the words as we need to compare words letter by letter. (technically k<=1000 in the problem, though).

then, for a prefix of length p, we must do log m binary searches, but each binary search takes k time to compare words. So this is p*k*log m time. We also do 3 iterations of at prefix length up to k with the .slice, but k is already included. This also takes up k memory.
*/

var suggestedProducts = function (products, searchWord) {
  products.sort();

  const result = [];

  // do a binary search for every prefix
  for (let i = 1; i < searchWord.length + 1; i++) {
    const prefix = searchWord.slice(0, i);

    // l and r represent pointers in the products array. at every `m`, we will comapre that word to our prefix. our objective is to find the first word that is bigger than our prefix. so if we are searching for mo, mobile might be the first word bigger than it. `myself` might also be, but this is okay, we will validate the prefix-matching once we find the word.
    let l = 0;
    let r = products.length - 1;

    while (l < r) {
      const m = Math.floor((r + l) / 2);
      const word = products[m];
      if (word >= prefix) {
        r = m;
      } else {
        l = m + 1;
      }
    }
    /* l/r represent the last possible word that could be bigger than our prefix */

    // if it is still smaller, we don't have any matches, as our prefix is bigger than all the products
    if (products[r] < prefix) {
      result.push([]); // edge case, problem expects empty lists
      continue;
    }

    const level = []; // each prefix should contribute a list of up to three elements

    // start iterating from the first word bigger than our prefix, up to 3 more suggested words, or until the end of the products
    for (let j = l; j < Math.min(l + 3, products.length); j++) {
      const word = products[j];
      const wordPrefix = word.slice(0, prefix.length);
      if (prefix === wordPrefix) {
        level.push(word);
      }
      // if we don't find a prefix match, none of the remaining words will prefix match
      else {
        break;
      }
    }

    result.push(level);
  }

  return result;
};
