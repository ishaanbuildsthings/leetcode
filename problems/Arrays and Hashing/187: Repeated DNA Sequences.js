// https://leetcode.com/problems/repeated-dna-sequences/description/
// Difficulty: Medium
// tags: rolling hash, sliding window fixed

// Problem
/*
Simplified: Find repeating sequences of length 10
Input: s = "AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT"
Output: ["AAAAACCCCC","CCCCCAAAAA"]

Detailed:
The DNA sequence is composed of a series of nucleotides abbreviated as 'A', 'C', 'G', and 'T'.

For example, "ACGAATTCCG" is a DNA sequence.
When studying DNA, it is useful to identify repeated sequences within the DNA.

Given a string s that represents a DNA sequence, return all the 10-letter-long sequences (substrings) that occur more than once in a DNA molecule. You may return the answer in any order.
*/

// Solution 1: O(n) time and O(1) space (there is a cap on valid 10 digit sequences), but we use a rolling hash to make it faster. No mod or collision handling is needed since we can keep the numbers small enough.

var findRepeatedDnaSequences = function (s) {
  const seenHashes = new Set();
  const mapping = { A: 1, C: 2, G: 3, T: 4 };
  // first digit in the 10 string will be multiplied by 10^9
  let initialHash = 0;
  for (let i = 0; i < 10; i++) {
    const letter = s[i];
    const power = 9 - i;
    const contribution = mapping[letter] * 10 ** power;
    initialHash += contribution;
    seenHashes.add(initialHash);
  }

  const results = new Set();
  let l = 0;
  let r = 9;
  let runningHash = initialHash;
  while (r < s.length) {
    r++;
    l++;
    if (r === s.length) {
      break;
    }
    const lostLetter = s[l - 1];
    const lostLetterContribution = mapping[lostLetter] * 10 ** 9;
    runningHash = runningHash - lostLetterContribution;
    runningHash *= 10; // shift everything
    const newLetter = s[r];
    const newLetterContribution = mapping[newLetter];
    runningHash += newLetterContribution;
    if (seenHashes.has(runningHash)) {
      results.add(s.slice(l, r + 1));
    } else {
      seenHashes.add(runningHash);
    }
  }

  return Array.from(results);
};

// Solution 2: O(n) (since 10 is a constant) and O(1) space (there is a cap on valid 10 digit sequences). Iterate a fixed sliding window and grab the substring each time.

var findRepeatedDnaSequences = function (s) {
  const seenSequences = new Set();
  const duplicatedSequences = new Set();
  let l = 0;
  let r = 9;
  while (r < s.length) {
    const substring = s.slice(l, r + 1);
    if (seenSequences.has(substring)) {
      duplicatedSequences.add(substring);
    }
    seenSequences.add(substring);
    r++;
    l++;
  }
  return Array.from(duplicatedSequences);
};
