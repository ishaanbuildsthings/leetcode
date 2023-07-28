// https://leetcode.com/problems/longest-string-chain/description/
// Difficulty: Medium
// Tags: acyclic graph, dynamic programming 1d

// Problem
/*
You are given an array of words where each word consists of lowercase English letters.

wordA is a predecessor of wordB if and only if we can insert exactly one letter anywhere in wordA without changing the order of the other characters to make it equal to wordB.

For example, "abc" is a predecessor of "abac", while "cba" is not a predecessor of "bcad".
A word chain is a sequence of words [word1, word2, ..., wordk] with k >= 1, where word1 is a predecessor of word2, word2 is a predecessor of word3, and so on. A single word is trivially a word chain with k == 1.

Return the length of the longest possible word chain with words chosen from the given list of words.
*/

// Solution, O(L*n^2) time, O(n^2) space
/*
For each word, we can compute a list of successor words. We first spend n time bucketing the words into buckets by word length, which helps which a minor optimization. Now, we can compare a word only to words with length+1 to see if it is a successor. The worst case time complexity is still n^2 in terms of word comparisons, for instance 500 length 5 words and 500 length 6 words is still 500*500 comparisons. For each comparison, we run the isSuccessor function on the longer word, so L time. L*n^2 time to get a list of all successors.

Now, for each word, n, we compute the max depth. We have to iterate over each word, since the graph may be disconnected (the graph represents successors). For each word, we check up to n successor words (though this could maybe be capped since there's a finite number of letter placements that form a successor). There are n states, and each takes n time to solve (we store results in a dp), so we have n^2 time. The stack depth is n and the memory usage for the successor list is n^2 upper bound (we store n words and each has n successors)
*/

var longestStrChain = function (words) {
  const wordsByLength = {}; // maps a length to an array of words that length, helps us compute predecessors since for each word we should only look at words of length+1

  for (const word of words) {
    if (!(word.length in wordsByLength)) {
      wordsByLength[word.length] = [word];
    } else {
      wordsByLength[word.length].push(word);
    }
  }

  const successors = {}; // maps a word to a list of its successors

  function isSuccessor(word1, word2) {
    let i = 0;
    let j = 0;
    let skips = 0;
    while (j < word2.length) {
      if (word1[i] === word2[j]) {
        i++;
        j++;
      } else if (word1[i] !== word2[j]) {
        skips++;
        // not allowed two different letters
        if (skips === 2) {
          return false;
        }
        j++;
      }
    }
    return true;
  }

  for (const sizeKey in wordsByLength) {
    if (Number(sizeKey) + 1 in wordsByLength) {
      for (const word of wordsByLength[sizeKey]) {
        const successorsOfWord = [];
        for (const longerWord of wordsByLength[Number(sizeKey) + 1]) {
          if (isSuccessor(word, longerWord)) {
            successorsOfWord.push(longerWord);
          }
        }
        successors[word] = successorsOfWord;
      }
    }
  }

  const memo = {}; // memo[word] is the longest word chain we can make starting at that word

  // the longest word chain we can make at a given word is 1 + the longest word chain we can make at any successor word
  function dp(word) {
    // base case, no successors
    if (!(word in successors) || successors[word].length === 0) {
      return 1;
    }

    if (memo[word] !== undefined) {
      return memo[word];
    }

    let resultForThis = 0;

    for (const successor of successors[word]) {
      const lengthFromThatWord = dp(successor);
      const lengthIfWeTakeThisWord = 1 + lengthFromThatWord;
      resultForThis = Math.max(resultForThis, lengthIfWeTakeThisWord);
    }

    memo[word] = resultForThis;
    return resultForThis;
  }

  let result = 0;
  for (const word of words) {
    const chainFromWord = dp(word);
    result = Math.max(result, chainFromWord);
  }

  return result;
};
