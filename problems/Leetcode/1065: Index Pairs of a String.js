// https://leetcode.com/problems/index-pairs-of-a-string/description/
// Difficulty: Easy
// tags: rolling hash

// Problem
/*
Given a string text and an array of strings words, return an array of all index pairs [i, j] so that the substring text[i...j] is in words.

Return the pairs [i, j] in sorted order (i.e., sort them by their first coordinate, and in case of ties sort them by their second coordinate).

Input: text = "ababa", words = ["aba","ab"]
Output: [[0,1],[0,2],[2,3],[2,4]]
Explanation: Notice that matches can overlap, see "aba" is found in [0,2] and [2,4].
*/

// Solution 1, O(n*m*k + n log n) time, or O(1) given the lax constraints. O(1) storage, or O(n) storage if we consider the storage used by .sort.
// * Solution 2: This solution can be sped up with a rolling hash. We would iterate through m different words, hashing each one, if a word is k long this would take m*k time. Then we run a rolling hash through n, at most m times, since it is possible all the words are different lengths. This would result in n*m + n*k time. We then sort the array which is n log n
// * Solution 3, we iterate through m words, adding them to a set. This takes m*k time as each would has a certain length. We then iterate through n^2 subarrays, and for each iteration do a k operation for the length of the word to do a lookup. Resulting in m*k + n^2*k time
// * Solution 4, populate a trie with all the words, iterate across n^2 subarrays, each time we stop having children we terminate early.
// * Solution 5, aho-corasick
/*
First, iterate across all letters of text, so n. For every letter, iterate across every word, there are m words. For each word, check if the substring matches, by doing a k operation where k is the length of the word. This results in n*m*k time. Since the constraints are small, we can say this is O(1) time, but the solution is not tenable for larger inputs. We then sort the result array, which is upper bounded at n log n.
*/

var indexPairs = function (text, words) {
  const result = [];
  for (let i = 0; i < text.length; i++) {
    for (const word of words) {
      const substring = text.slice(i, i + word.length);
      if (substring === word) {
        result.push([i, i + word.length - 1]);
      }
    }
  }

  result.sort((a, b) => {
    if (a[0] < b[0]) {
      return -1;
    } else if (a[0] > b[0]) {
      return 1;
    } else if (a[0] === b[0]) {
      return a[1] - b[1];
    }
  });

  return result;
};
