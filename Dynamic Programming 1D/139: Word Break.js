// https://leetcode.com/problems/word-break/description/
// Difficulty: Medium
// tags: dynamic programming 1d

// Problem
/*
Simplified:

Input: s = "applepenapple", wordDict = ["apple","pen"]
Output: true
Explanation: Return true because "applepenapple" can be segmented as "apple pen apple".
Note that you are allowed to reuse a dictionary word.

Detailed:

Given a string s and a dictionary of strings wordDict, return true if s can be segmented into a space-separated sequence of one or more dictionary words.

Note that the same word in the dictionary may be reused multiple times in the segmentation.
*/

// Solution, I thought the time was O(n^3 + m*k). Since for each letter, we look at n previous letters, and perform a .slice of time n. But the .slice might be amortized so I am not sure. O(n + m*k) space for the dp, m*k space for the word set.
/*
To solve this, we start at a sub-problem, which is considering just the beginning letter. Say our word is 'abc' and our word dict is 'a', 'bc'.

At 'a', we know it is in the word dict (we use a set). So dp[0] = true, because the problem from the start, to the ending index of 0, is solveable.

Now try 'ab'. Consider all prior prefixes. For instance the empty prefix, dp[-1], is true (by default). So 'ab' is doable if '' (prior dp) + 'ab' new substring we consider is in the word dict. 'ab' is not in the word dict though. But now we try the prefix 'a'. dp[0] is true, so we check if the string from [1, 1] is in the dict. 'b' is not, so 'ab' is not doable.

Repeat the process for all letters, then return the final dp.

For each letter, we look at n prior letters. For each prior letter, if that dp is true, we do a length n substring slice, and break if we get a true statement. We also spend m*k time populating the set, where m is the number of words and k is the length of them, in the word dict.
*/

var wordBreak = function (s, wordDict) {
  const wordSet = new Set();
  for (const word of wordDict) {
    wordSet.add(word);
  }

  /*
    stores if the word starting from 0, ending to a certain index in the dp, can be "word break-ed"
    for instance in 'abc' worddict = ['a' 'b']

    at index 1 of the dp, we have 'ab', which can be word break-ed, so we would say true
     */
  const dp = new Array(s.length).fill(false);
  dp[-1] = true; // since for a word, we iterate over all previous words to see if we had a true dp there, we also need to consider the case that the entire word for what we are solving is in the word dict. for instance if we are solving for 'abc' and 'abcdef' and 'abc' is a word, when we get to the 'abc' sub problem, we should look at the previous ending of -1, which essentially means we are using the entire word as the substring

  // iterate over each letter of the word, solving the word break if we were to end at that letter
  for (let endingIndex = 0; endingIndex < s.length; endingIndex++) {
    // for each letter we end add, we need to look at up to n prior letters, to see if we can make a word break
    // start from -1 to consider the entire word as a substring
    for (
      let previousEnding = -1;
      previousEnding < endingIndex;
      previousEnding++
    ) {
      /*
            say we are trying to solve the word break for 'abc'

            and say 'a' is not doable. now we are trying to solve for 'ab'. so we scan all previous endings. since the ending at 'a' wasn't doable, we have no hope to make a word break with that split, so we continue
            */
      if (!dp[previousEnding]) {
        continue;
      }

      // if the previous dp was doable, we should check a new word and see if that exists in our word dict
      const newWord = s.slice(previousEnding + 1, endingIndex + 1);

      if (wordSet.has(newWord)) {
        dp[endingIndex] = true;
        break;
      }
    }
  }

  return dp[s.length - 1];
};
